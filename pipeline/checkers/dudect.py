from pathlib import Path
from checkers import CheckerResult
from label import ArrayArgument, IntegerArgument, PointerArgument, SnippetLabel, ValueConstraint
from . import Checker, CheckerResult
import pathlib, subprocess

BITS_PER_CHAR = 8

class DudectChecker(Checker):
    def identifier(self) -> str:
        return 'dudect'

    def is_parralelizeble(self) -> bool:
        return False

    def prepareSnippet(self, label: SnippetLabel) -> SnippetLabel:
        if label.arguments is None or label.preparation is not None:
            return self.preparePreparedSnippet(label)
        else:
            return self.prepareArgumentsSnippet(label)

    def preparePreparedSnippet(self, label: SnippetLabel) -> SnippetLabel:
        checker_file = "#include<stdint.h>\n"
        checker_file += "#define DUDECT_PREPARATION_FUNCTION %s\n" % label.preparation.function
        checker_file += "#define DUDECT_PREPARATION_SIZE %d\n" % label.preparation.size
        checker_file += "void %s(void* data);\n" % label.function_name
        checker_file += "void %s(void* data);\n" % label.preparation.function
        checker_file += '#include "checker_dudect.h"\n#include <string.h>\n'

        checker_file += "uint8_t do_one_computation(uint8_t *raw_data) {\n"
        checker_file += "%s(raw_data);\n}\n" % label.function_name
        
        with open(label.basedir / "ctccp_check.c", "w") as f:
            f.write(checker_file)

        label.header_dirs.append(pathlib.Path(__file__).parent.parent.parent / "checkers" / "common")
        label.header_dirs.append(pathlib.Path(__file__).parent.parent.parent / "checkers" / "dudect")
        label.source_files.append(label.basedir / "ctccp_check.c")
        label.additional_flags.append("-lm")
        return label



    def prepareArgumentsSnippet(self, label: SnippetLabel) -> SnippetLabel:
        # Struct elements: name, type
        struct_elements: list[str] = []

        # Code lines to append to checker_dudect_fill_struct
        fill_struct_additions: list[str] = []
        
        # Public/Secret elements: name, size, count, constraint
        secret_elements: list[tuple[str, str, int, ValueConstraint]] = []
        public_elements: list[tuple[str, str, int, ValueConstraint]] = []          

        arg_counter = 0
        arg_names = []

        """Unpacks an array argument and generates matching C code
        """
        def unpackArray(arg: ArrayArgument, sizes_before_orig: list[int]) -> tuple[str, list[int]]:
            sizes_before = sizes_before_orig.copy()
            sizes_before.append(arg.length)

            if arg.of.getType() == 'integer':
                int_arg: IntegerArgument = arg.of
                arg_name = "arg_%d_%d" % (arg_counter, len(sizes_before))
                base_type = "uint%d_t" % int_arg.bits
                extended_type = "%s %s" % (base_type, arg_name)
                elements = 1
                for size in sizes_before:
                    if size > 0:
                        extended_type += "[%d]" % size
                        elements *= size
                struct_elements.append(extended_type)
                if int_arg.secret:
                    secret_elements.append((arg_name, "sizeof(%s)" % base_type, elements, int_arg.value))
                else:
                    public_elements.append((arg_name, "sizeof(%s)" % base_type, elements, int_arg.value))
                return (base_type, [arg.length])
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
            sizes_before = sizes_before_orig.copy()
            sizes_before.append(0)

            def generateArrayOfPointers(sizes_remaining: list[int], indices: list[int]):
                if len(sizes_remaining) == 0:
                    ref = "&dest->arg_%d_%d" % (arg_counter, len(sizes_before) + len(indices))
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
                base_type = "uint%d_t" % (int_arg.bits)
                extended_type = "%s %s" % (base_type, arg_data_name)
                elements = 1
                for size in sizes_before:
                    if size > 0:
                        extended_type += "[%d]" % size
                        elements *= size
                struct_elements.append(extended_type)
                if int_arg.secret:
                    secret_elements.append((arg_data_name, "sizeof(%s)" % base_type, elements, int_arg.value))
                else:
                    public_elements.append((arg_data_name, "sizeof(%s)" % base_type, elements, int_arg.value))
                
                arg_ptr = "*(%s)" % (arg_ptr_name)
                for size in sizes_before:
                    if size > 0:
                        arg_ptr = "(%s)[%d]" % (arg_ptr, size)

                struct_elements.append("uint%d_t %s" % (int_arg.bits, arg_ptr))

                def generateArrayOfIntPointers(sizes_bef, indices):
                    while (len(sizes_bef) > 0 and sizes_bef[0] == 0):
                        sizes_bef = sizes_bef[1:]
                    if (len(sizes_bef) == 0):
                        ref = "&(dest->%s)" % arg_data_name
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
                fill_struct_additions.append("dest->%s = %s;\n" % (arg_ptr_name, generateArrayOfIntPointers(sizes_before.copy(), [])))
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
                        ref = "&(dest->%s)" % arg_data_name
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
    
                fill_struct_additions.append("dest->%s = %s;\n" % (arg_ptr_name, generateArrayOfArrPointers(sizes_before.copy(), [])))

                all_sizes = sizes_before.copy()
                all_sizes.extend(sizes_after)
                for id, size in enumerate(all_sizes):
                    if size > 0:
                        arg_ptr_name = "(%s)[%d]" % (arg_ptr_name, size)
                    elif id > len(sizes_before_orig) - 1:
                        arg_ptr_name = "*(%s)" % (arg_ptr_name)
                
                struct_elements.append("%s %s" % (base_type, arg_ptr_name))

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
                        ref = "&(dest->%s)" % arg_data_name
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
                
                fill_struct_additions.append("dest->%s = %s;\n" % (arg_ptr_name, generateArrayOfArrPointers(sizes_before.copy(), [])))
                
                all_sizes = sizes_before.copy()
                all_sizes.extend(sizes_after)
                for id, size in enumerate(all_sizes):
                    if size > 0:
                        arg_ptr_name = "(%s)[%d]" % (arg_ptr_name, size)
                    elif id > len(sizes_before_orig) - 1:
                        arg_ptr_name = "*(%s)" % (arg_ptr_name)

                struct_elements.append("%s %s" % (base_type, arg_ptr_name))

                res = [0]
                res.extend(sizes_after)
                return base_type, res

            raise ValueError("Found invalid argument type")

        arg_types_simplified: list[str] = []

        for arg in label.arguments:
            arg_name = "arg_" + str(arg_counter)
            if arg.getType() == 'integer':
                arg: IntegerArgument = arg
                struct_elements.append("uint%d_t %s" % (arg.bits, arg_name))
                if arg.secret:
                    secret_elements.append((arg_name, "sizeof(uint%d_t)" % arg.bits, 1, arg.value))
                else:
                    public_elements.append((arg_name, "sizeof(uint%d_t)" % arg.bits, 1, arg.value))
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

        checker_file = "#include<stdint.h>\n"
        checker_file += "typedef struct checker_dudect_args {\n"
        for element in struct_elements:
            checker_file += "%s;\n" % element
        checker_file += "} checker_dudect_args_t;\nchecker_dudect_args_t template;\n"

        checker_file += "uint8_t %s(" % label.function_name
        for idx, type in enumerate(arg_types_simplified):
            if idx > 0:
                checker_file += ", "
            checker_file += type
        checker_file += ");\n"
        
        checker_file += "#define DUDECT_PUBLIC_VARS %d\n" % len(public_elements)
        checker_file += '#include "checker_dudect.h"\n#include <string.h>\n'

        checker_file += "void checker_dudect_fill_struct(checker_dudect_args_t* dest, checker_dudect_args_t* copy_src) {\n"
        checker_file += "memcpy(dest, &template, sizeof(checker_dudect_args_t));\n"
        for name, size, count, constraint in secret_elements:
            checker_file += "if (copy_src) {\n"
            checker_file += "memcpy(&(dest->%s), &(copy_src->%s), sizeof((dest->%s)));\n" % (name, name, name)
            checker_file += "} else {\n"
            if constraint is None:
                checker_file += "checker_fill_unconstrained((void*) &(dest->%s), %s, %s);\n" % (name, count, size)
            elif constraint.getType() == "fixed":
                checker_file += "checker_fill_fixed((void*) &(dest->%s), %d, %s, %s);\n" % (name, constraint.value, count, size)
            elif constraint.getType() == "range":
                checker_file += "checker_fill_range((void*) &(dest->%s), %d, %d, %s, %s);\n" % (name, constraint.start, constraint.end, count, size)
            checker_file += "}\n"
        for line in fill_struct_additions:
            checker_file += line
        checker_file += "}\n"

        checker_file += "void checker_dudect_fill_template() {\n"
        for name, size, count, constraint in public_elements:
            if constraint is None:
                checker_file += "checker_fill_unconstrained((void*) &(template.%s), %s, %s);\n" % (name, count, size)
            elif constraint.getType() == "fixed":
                checker_file += "checker_fill_fixed((void*) &(template.%s), %d, %s, %s);\n" % (name, constraint.value, count, size)
            elif constraint.getType() == "range":
                checker_file += "checker_fill_range((void*) &(template.%s), %d, %d, %s, %s);\n" % (name, constraint.start, constraint.end, count, size)
        checker_file += "}\n"

        checker_file += "uint8_t do_one_computation(uint8_t *raw_data) {\n"
        checker_file += "checker_dudect_args_t *data = (void*) raw_data;\n"
        checker_file += "return %s(" % label.function_name
        for id, arg_name in enumerate(arg_names):
            if id > 0:
                checker_file += ", "
            checker_file += "data->%s" % arg_name

        checker_file += ");\n}\n"

        
        with open(label.basedir / "ctccp_check.c", "w") as f:
            f.write(checker_file)

        label.header_dirs.append(pathlib.Path(__file__).parent.parent.parent / "checkers" / "common")
        label.header_dirs.append(pathlib.Path(__file__).parent.parent.parent / "checkers" / "dudect")
        label.source_files.append(label.basedir / "ctccp_check.c")
        label.additional_flags.append("-lm")
        return label


    def runChecker(self, label: SnippetLabel, binary: Path, timeout: int=120) -> CheckerResult:
        try:
            output = subprocess.run(
                [str(binary)], 
                #stdout=subprocess.PIPE, 
                #stderr=subprocess.PIPE,
                timeout=timeout
            )
        except subprocess.TimeoutExpired:
            return CheckerResult(None,True)
        return CheckerResult(output.returncode == 0, False)


def registerCheckers() -> list[Checker]:
    return [
        DudectChecker()
    ]