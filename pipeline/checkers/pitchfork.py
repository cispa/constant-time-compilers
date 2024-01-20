import json
import logging
from pathlib import Path
import pathlib
import shutil
import subprocess
from compilers import Compiler
from label import ArrayArgument, IntegerArgument, PointerArgument, SnippetLabel, ValueConstraint
from . import Checker, CheckerResult

BITS_PER_CHAR = 8

class PitchforkChecker(Checker):
    def identifier(self) -> str:
        return 'pitchfork'
    
    def prepareSnippet(self, label: SnippetLabel) -> SnippetLabel:
        global checker_file
        checker_file = '#define CHECKER_RANDOM_DEVURANDOM 1\n#include "checker_random.h"\n#include <time.h>\n$FUNC_DECL$\n'

        if label.arguments is None or label.preparation is not None:
            raise ValueError("Pitchfork cannot check snippets with custom preparation functions.")

        # Constrains
        vars_to_constrain: list[tuple[str, int, int, ValueConstraint]] = []
        
        # List of secret variables
        vars_to_protect: list[tuple[str, int]] = []
        arg_counter = 0
        arg_names = []

        """Unpacks an array argument and generates matching C code
        """
        def unpackArray(arg: ArrayArgument, sizes_before_orig: list[int]) -> tuple[str, list[int]]:
            global checker_file
            sizes_before = sizes_before_orig.copy()
            sizes_before.append(arg.length)

            if arg.of.getType() == 'integer':
                int_arg: IntegerArgument = arg.of
                arg_name = "arg_%d_%d" % (arg_counter, len(sizes_before))
                checker_file += "uint%d_t %s" % (int_arg.bits, arg_name)
                elements = 1
                for size in sizes_before:
                    if size > 0:
                        checker_file += "[%d]" % size
                        elements *= size
                checker_file += ";\n"
                if int_arg.secret:
                    vars_to_protect.append((arg_name, elements * int_arg.bits // BITS_PER_CHAR))
                vars_to_constrain.append((arg_name, int_arg.bits, elements, int_arg.value))
                return ('uint%d_t' % int_arg.bits, [arg.length])
            elif arg.of.getType() == 'array':
                arr_arg: ArrayArgument = arg.of
                (base_type, sizes_after) = unpackArray(arr_arg, sizes_before)
                res = [arg.length]
                res.extend(sizes_after)
                return (base_type, res)
            elif arg.of.getType() == 'pointer':
                ptr_arg: PointerArgument = arg.of
                (base_type, sizes_after) = unpackPointer(ptr_arg, sizes_before)
                res = [arg.length]
                res.extend(sizes_after)
                return (base_type, res)
            
            raise ValueError("Found invalid argument type")


        def unpackPointer(arg: PointerArgument, sizes_before_orig: list[int]) -> tuple[str, list[int]]:
            global checker_file
            sizes_before = sizes_before_orig.copy()
            sizes_before.append(0)

            def generateArrayOfPointers(sizes_remaining: list[int], indices: list[int]):
                if len(sizes_remaining) == 0:
                    ref = "&arg_%d_%d" % (arg_counter, len(sizes_before) + len(indices))
                    for i in indices:
                        ref += "[%d]" % i
                    return ref
                
                arr = "{"
                for i in range(sizes_after[0]):
                    if i > 0:
                        arr += ", "
                    arr += generateArrayOfPointers(sizes_after[1:], indices.copy().append(i))
                arr += "}"
                return arr

            if arg.to.getType() == 'integer':
                int_arg: IntegerArgument = arg.to
                arg_data_name = "arg_%d_%d" % (arg_counter, len(sizes_before) + 1)
                arg_ptr_name = "arg_%d_%d" % (arg_counter, len(sizes_before))
                checker_file += "uint%d_t %s" % (int_arg.bits, arg_data_name)
                elements = 1
                for size in sizes_before:
                    if size > 0:
                        checker_file += "[%d]" % size
                        elements *= size
                checker_file += ";\n"
                if int_arg.secret:
                    vars_to_protect.append((arg_data_name, elements * int_arg.bits // BITS_PER_CHAR))
                vars_to_constrain.append((arg_data_name, int_arg.bits, elements, int_arg.value))
                
                arg_ptr_name = "*(%s)" % (arg_ptr_name)
                for size in sizes_before:
                    if size > 0:
                        arg_ptr_name = "(%s)[%d]" % (arg_ptr_name, size)

                checker_file += "uint%d_t %s = " % (int_arg.bits, arg_ptr_name)
                def generateArrayOfIntPointers(sizes_bef, indices):
                    while (len(sizes_bef) > 0 and sizes_bef[0] == 0):
                        sizes_bef = sizes_bef[1:]
                    if (len(sizes_bef) == 0):
                        ref = "&%s" % arg_data_name
                        for i in indices:
                            ref += "[%d]" % i
                        return ref
                    arr = "{"
                    for i in range(sizes_bef[0]):
                        if i > 0:
                            arr += ", "
                        new_indices = indices.copy()
                        new_indices.append(i)
                        arr += generateArrayOfIntPointers(sizes_bef[1:], new_indices)
                    arr += "}"
                    return arr
                checker_file += generateArrayOfIntPointers(sizes_before.copy(), []) + ";\n"
                return ('uint%d_t' % int_arg.bits, [0])
            elif arg.to.getType() == 'array':
                arr_arg: ArrayArgument = arg.to
                base_type, sizes_after = unpackArray(arr_arg, sizes_before)
                offset = 0
                for size in sizes_after:
                    offset += 1
                    if size == 0:
                        break
                arg_data_name = "arg_%d_%d" % (arg_counter, len(sizes_before) + offset)
                arg_ptr_name = "arg_%d_%d" % (arg_counter, len(sizes_before))

                def generateArrayOfArrPointers(sizes_bef, indices):
                    while (len(sizes_bef) > 0 and sizes_bef[0] == 0):
                        sizes_bef = sizes_bef[1:]
                    if (len(sizes_bef) == 0):
                        ref = "&%s" % arg_data_name
                        for i in indices:
                            ref += "[%d]" % i
                        return ref
                    arr = "{"
                    for i in range(sizes_bef[0]):
                        if i > 0:
                            arr += ", "
                        new_indices = indices.copy()
                        new_indices.append(i)
                        arr += generateArrayOfArrPointers(sizes_bef[1:], new_indices)
                    arr += "}"
                    return arr
                
                all_sizes = sizes_before.copy()
                all_sizes.extend(sizes_after)
                for id, size in enumerate(all_sizes):
                    if size > 0:
                        arg_ptr_name = "(%s)[%d]" % (arg_ptr_name, size)
                    elif id > len(sizes_before_orig) - 1:
                        arg_ptr_name = "*(%s)" % (arg_ptr_name)

                checker_file += "%s %s = " % (base_type, arg_ptr_name)
                checker_file += generateArrayOfArrPointers(sizes_before.copy(), []) + ";\n"

                res = [0]
                res.extend(sizes_after)
                return base_type, res
            elif arg.to.getType() == 'pointer':
                ptr_arg: PointerArgument = arg.to
                base_type, sizes_after = unpackPointer(ptr_arg, sizes_before)
                offset = 0
                for size in sizes_after:
                    offset += 1
                    if size == 0:
                        break
                arg_data_name = "arg_%d_%d" % (arg_counter, len(sizes_before) + offset)
                arg_ptr_name = "arg_%d_%d" % (arg_counter, len(sizes_before))

                def generateArrayOfArrPointers(sizes_bef, indices):
                    while (len(sizes_bef) > 0 and sizes_bef[0] == 0):
                        sizes_bef = sizes_bef[1:]
                    if (len(sizes_bef) == 0):
                        ref = "&%s" % arg_data_name
                        for i in indices:
                            ref += "[%d]" % i
                        return ref
                    arr = "{"
                    for i in range(sizes_bef[0]):
                        if i > 0:
                            arr += ", "
                        new_indices = indices.copy()
                        new_indices.append(i)
                        arr += generateArrayOfArrPointers(sizes_bef[1:], new_indices)
                    arr += "}"
                    return arr
                
                all_sizes = sizes_before.copy()
                all_sizes.extend(sizes_after)
                for id, size in enumerate(all_sizes):
                    if size > 0:
                        arg_ptr_name = "(%s)[%d]" % (arg_ptr_name, size)
                    elif id > len(sizes_before_orig) - 1:
                        arg_ptr_name = "*(%s)" % (arg_ptr_name)

                checker_file += "%s %s = " % (base_type, arg_ptr_name)
                checker_file += generateArrayOfArrPointers(sizes_before.copy(), []) + ";\n"

                res = [0]
                res.extend(sizes_after)
                return base_type, res

            raise ValueError("Found invalid argument type")

        arg_types_simplified: list[str] = []

        for arg in label.arguments:
            arg_name = "arg_" + str(arg_counter)
            if arg.getType() == 'integer':
                checker_file += "volatile uint%d_t %s = 0;\n" % (arg.bits, arg_name)
                if arg.secret:
                    vars_to_protect.append((arg_name, arg.bits // BITS_PER_CHAR))
                vars_to_constrain.append((arg_name, arg.bits, 1, arg.value))
                arg_names.append(arg_name)
                arg_types_simplified.append("uint%d_t" % arg.bits)
            elif arg.getType() == 'array':
                _, sizes = unpackArray(arg, [])
                offset = 0
                for size in sizes:
                    offset += 1
                    if size == 0:
                        break
                arg_names.append(arg_name + "_" + str(offset))
                arg_types_simplified.append("void*")

            elif arg.getType() == 'pointer':
                unpackPointer(arg, [])
                arg_names.append(arg_name + "_1")
                arg_types_simplified.append("void*")

            arg_counter += 1

        func_decl = "void %s(" % label.function_name
        for id, arg_type in enumerate(arg_types_simplified):
            if id > 0:
                func_decl += ", "
            func_decl += arg_type
        func_decl += ");"
        checker_file = checker_file.replace("$FUNC_DECL$", func_decl)

        checker_file += "int main() {\n"
        for var, elem_bits, elements, constraint in vars_to_constrain:
            if constraint is None:
                continue
            elif constraint.getType() == "fixed":
                checker_file += "checker_fill_fixed((void*) &%s, %d, %s, %s);\n" % (var, constraint.value, elements, elem_bits // BITS_PER_CHAR)
            elif constraint.getType() == "range":
                checker_file += "checker_limit_to_bounds_%d((void*) &%s, %d, %d, %d);\n" % (elem_bits, var, elements, constraint.start, constraint.end)

        checker_file += "%s(" % label.function_name
        for id, arg_name in enumerate(arg_names):
            if id > 0:
                checker_file += ", " 
            checker_file += arg_name

        checker_file += ");\nreturn 0;\n}\n"

        for (arg_name, size) in vars_to_protect:
            checker_file += "// protect %d bytes of %s\n" % (size, arg_name)
        
        with open(label.basedir / "pitchfork_check.c", "w") as f:
            f.write(checker_file)

        with open(label.basedir / "pitchfork_check.json", "w") as f:
            json.dump([{"name": name, "size": size} for (name, size) in vars_to_protect], f)

        label.header_dirs.append((pathlib.Path(__file__).parent.parent.parent / "checkers" / "common").resolve())
        label.source_files.append(label.basedir / "pitchfork_check.c")
        return label


    def runChecker(self, label: SnippetLabel, binary: Path, timeout: int=120) -> CheckerResult:
        try:
            output = subprocess.run(
                [
                    "timeout",
                    str(timeout),
                    str((pathlib.Path(__file__).parent.parent.parent / "checkers" / "pitchfork-angr" / "wrapper.sh").resolve()),
                    str(binary.resolve()),
                    "main",
                    str((label.basedir / "pitchfork_check.json").resolve())
                ], 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE, 
                cwd=((pathlib.Path(__file__).parent.parent.parent / "checkers" / "pitchfork-angr")),
                timeout=timeout
            )
            if output.returncode >= 2:
                logging.error("pitchfork-angr terminated with return code %d." % output.returncode)
                return CheckerResult(None,False)
        except subprocess.TimeoutExpired:
            return CheckerResult(None, True)
        return CheckerResult(output.returncode == 0, False)

def registerCheckers() -> list[Checker]:
    return [
        PitchforkChecker()
    ]
