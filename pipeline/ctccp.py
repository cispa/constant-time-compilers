#!/bin/env python3

import argparse, tempfile, copy, shutil
import asyncio
from enum import Enum
from pathlib import Path
from typing import Callable
from label import SnippetLabel, parseLabelFromFile
from checkers.collector import Checker, CheckerResult
import checkers.collector
from compilers.collector import Compiler
import compilers.collector
import logging
from pathos.multiprocessing import ProcessPool
import os
l = logging
l.basicConfig(level=logging.DEBUG)

class PipelineRun:
    '''Descriptor for pipeline runs'''

    id: str
    checker: Checker
    compiler: Compiler
    optionPreset: str
    label: SnippetLabel
    binaryTarget: Path

    def __init__(self, id: str, checker: Checker, compiler: Compiler, optionPreset: str, label: SnippetLabel, binaryTarget: str) -> None:
        self.id = id
        self.checker = checker
        self.compiler = compiler
        self.optionPreset = optionPreset
        self.label = label
        self.binaryTarget = binaryTarget

    def runCompiler(self):
        self.compiler.compileSnippet(self.label, self.optionPreset, self.binaryTarget)

    def runChecker(self) -> CheckerResult:
        return self.checker.runChecker(self.label, self.binaryTarget)

class RunState(Enum):
    PREPARE_COMPLETE = "Prepare Complete"
    COMPILE_COMPLETE = "Compile Complete"
    CHECK_COMPLETE = "Checking Complete"

async def check_snippet(label: SnippetLabel, workdir: Path, checkers: list, compilers: list, callback: Callable|None = None) -> list[tuple[PipelineRun, CheckerResult]]:
    # Copy snippets for all runs to the working directory and let checkers prepare the snippets
    runs: list[PipelineRun] = []
    for checker in checkers:
        for compiler in checker.compatibleCompilers(compilers):
            for option_preset in compiler.availableOptionPresets():
                run_id: str = "%s_%s_%s" % (checker.identifier(), compiler.identifier(), option_preset)
                l.debug("Preparing run %s", run_id)

                # Copy label and snippet files
                run_label: SnippetLabel = copy.deepcopy(label)
                run_snippet_path = workdir / run_id / 'snippet'
                run_compiled_path = workdir / run_id / 'compiled'
                run_snippet_path.mkdir(parents=True)
                run_compiled_path.mkdir(parents=True)
                shutil.copytree(run_label.basedir, run_snippet_path, dirs_exist_ok=True)

                # Prepare snippet for compilation and checking
                run_label.basedir = run_snippet_path
                for id, source in enumerate(run_label.source_files):
                    run_label.source_files[id] = Path(str(source).replace("%PLBASE", str(Path(__file__).parent.resolve())).replace("%COMP", compiler.identifier()).replace("%COPT", option_preset))
                    if run_label.source_files[id].is_absolute():
                        run_label.source_files[id] = run_label.source_files[id].resolve()
                for id, header_dir in enumerate(run_label.header_dirs):
                    run_label.header_dirs[id] = Path(str(header_dir).replace("%PLBASE", str(Path(__file__).parent.resolve())).replace("%COMP", compiler.identifier()).replace("%COPT", option_preset))
                    if run_label.header_dirs[id].is_absolute():
                        run_label.header_dirs[id] = run_label.header_dirs[id].resolve()
                run_label = checker.prepareSnippet(run_label)
                runs.append(PipelineRun(run_id, checker, compiler, option_preset, run_label, (run_compiled_path / run_id)))
    if len(runs) == 0:
        raise ValueError("The requested combination of compilers and checkers is not compatible.")

    if callback is not None:
        await callback(RunState.PREPARE_COMPLETE)

    # Run the compilers
    def print_and_compile(run):
        l.debug("Compiling snippet for run %s", run.id)
        run.runCompiler()

    with ProcessPool(nodes=os.cpu_count()) as p:
        p.map(print_and_compile,runs)

    if callback is not None:
        await callback(RunState.COMPILE_COMPLETE)

    # Run the checkers
    results: list[tuple[PipelineRun, CheckerResult]] = []

    def print_and_run_checker(run):
        l.debug("Running checker for run %s", run.id)
        result = run.runChecker()
        if result.data_oblivious is None:
            l.info("No result for %s." % run.id)
        elif result.data_oblivious is not None:
            l.info("Result for %s: %s.", run.id, "data oblivious" if result.data_oblivious else "not data oblivious")
        elif result.timeout:
            l.info("Timeout fo %s.", run.id)
        return (run,result)

    # First run checkers that cannot deal with noise on system
    for run in runs[:]:
        if not run.checker.is_parralelizeble():
            result = print_and_run_checker(run)
            results.append(result)
            runs.remove(run)

    # Then go fast by multithreading
    with ProcessPool(nodes=os.cpu_count()) as p:
        results += p.map(print_and_run_checker,runs)

    if callback is not None:
        await callback(RunState.CHECK_COMPLETE)

    return results


def main():
    '''Main entry point'''

    # Collect compilers
    available_compilers = compilers.collector.collectCompilers()

    # Collect checkers
    available_checkers = checkers.collector.collectCheckers()

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument('-lk', '--list-checkers', action='store_true', help="print a list of available checkers and exit")
    action.add_argument('-lm', '--list-compilers', action='store_true', help="print a list of available compilers and exit")
    action.add_argument('-lp', '--list-pipelines', action='store_true', help="print a list of available compiler-checker pipelines and exit")
    action.add_argument('-i', '--label', type=str, help="the snippet label to work on")
    parser.add_argument('-w', '--workdir', type=str, help="work directory to use")
    parser.add_argument('-k', '--checker', type=str, nargs='*', default=[], help='identifiers of checkers to use (leave out to run all registered checkers)')
    parser.add_argument('-m', '--compiler', type=str, nargs='*', default=[], help='identifiers of compilers to use (leave out to run all registered compilers)')
    arguments = parser.parse_args()

    # List checkers if requested
    if (arguments.list_checkers):
        for checker in available_checkers:
            print(checker.identifier())
        exit(1)
        
    # List compilers if requested
    if (arguments.list_compilers):
        for compiler in available_compilers:
            print(compiler.identifier())
        exit(1)

    # List supported compiler-checker pipelines if requested
    if (arguments.list_pipelines):
        for checker in available_checkers:
            print(checker.identifier() + " (" + ", ".join([compiler.identifier() for compiler in checker.compatibleCompilers(available_compilers)]) + ")")
        exit(1)

    # If we got here, run compiler and checker

    # Check and parse label file
    label_path = Path(arguments.label)
    label: SnippetLabel = parseLabelFromFile(label_path)

    # Create workdir if it not does exist
    workdir: Path
    if arguments.workdir is None:
        # No workdir specified, use temporary folder
        workdir = Path(tempfile.mkdtemp(prefix="ctccp_"))
    else:
        # Workdir specified, check if empty
        workdir = Path(arguments.workdir).resolve()
        if workdir.exists():
            if not workdir.is_dir():
                raise ValueError("Invalid working directory specified: Not a directory.")
        else:
            workdir.mkdir(parents=True)
    l.info("Working in %s" % (workdir))


    # Generate a list of compiler and checker runs
    used_compilers: list[Compiler] = []
    used_checkers: list[Checker] = []
    
    # Collect compilers
    if len(arguments.compiler) == 0:
        used_compilers = available_compilers
    else:
        compilers_to_find: list[str] = arguments.compiler
        for compiler in available_compilers:
            if (identifier := compiler.identifier()) in compilers_to_find:
                used_compilers.append(compiler)
                compilers_to_find.remove(identifier)
        if len(compilers_to_find) > 0:
            raise ValueError("Invalid compiler(s) given: %s" % (", ".join(compilers_to_find)))
        
    # Collect checkers
    if len(arguments.checker) == 0:
        used_checkers = available_checkers
    else:
        checkers_to_find: list[str] = arguments.checker
        for checker in available_checkers:
            if (identifier := checker.identifier()) in checkers_to_find:
                used_checkers.append(checker)
                checkers_to_find.remove(identifier)
        if len(checkers_to_find) > 0:
            raise ValueError("Invalid checker(s) given: %s" % (", ".join(checkers_to_find)))
    l.info("Finished collecting checkers and compilers")

    # Run checks
    results = asyncio.run(check_snippet(label, workdir, used_checkers, used_compilers, None))

    # Output the results
    for (run, res) in results: 
        if res.timeout:
            print("[TOUT] %s" % run.id)
        else:
            print("[%s] %s" % ("NONE" if res.data_oblivious is None else ("PASS" if res.data_oblivious else "FAIL"), run.id))

if __name__ == "__main__":
    main()