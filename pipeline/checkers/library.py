import pathlib, subprocess, shutil, os, logging
from pathlib import Path
from compilers.collector import Compiler
from label import ArrayArgument, IntegerArgument, PointerArgument, SnippetLabel, ValueConstraint, SnippetLabel
from . import Checker, CheckerResult

NUM_CLASSES_BASE = 2
NUM_RUNS_PER_CLASS = 3

class LibraryChecker(Checker):
    def identifier(self) -> str:
        return 'lib'

    def prepareSnippet(self, label: SnippetLabel) -> SnippetLabel:
        label.additional_flags.append("-fPIC")
        label.additional_flags.append("-shared")
        return label

    def runChecker(self, label: SnippetLabel, binary: Path) -> CheckerResult:
        outpath = label.basedir.parent.parent / "out"
        os.makedirs(outpath, exist_ok=True)
        shutil.move(binary, outpath / binary.name)
        return CheckerResult(True)

def registerCheckers() -> list[Checker]:
    return [
        LibraryChecker()
    ]