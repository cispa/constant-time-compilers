import pathlib, subprocess, shutil, os, logging
from pathlib import Path
from compilers.collector import Compiler
from label import ArrayArgument, IntegerArgument, PointerArgument, SnippetLabel, ValueConstraint, SnippetLabel
from . import Checker, CheckerResult

NUM_CLASSES_BASE = 2
NUM_RUNS_PER_CLASS = 3

class DataChecker(Checker):
    def identifier(self) -> str:
        return 'data'

    def prepareSnippet(self, label: SnippetLabel) -> SnippetLabel:

        # Struct elements: name, type
        struct_elements: list[str] = []

        # Code lines to append to checker_data_fill_struct
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

        checker_file = "#include <stdint.h>\n"
        checker_file += '#include <stdlib.h>\n'
        checker_file += '#include <stdio.h>\n'
        checker_file += '#include <string.h>\n'
        checker_file += '#include "checker_random.h"\n'
        checker_file += "typedef struct checker_data_args {\n"
        for element in struct_elements:
            checker_file += "%s;\n" % element
        checker_file += "} checker_data_args_t;\nchecker_data_args_t template;\n"

        checker_file += "uint8_t %s(" % label.function_name
        for idx, type in enumerate(arg_types_simplified):
            if idx > 0:
                checker_file += ", "
            checker_file += type
        checker_file += ");\n"
        

        checker_file += "void checker_data_fill_struct(checker_data_args_t* dest) {\n"
        checker_file += "memcpy(dest, &template, sizeof(checker_data_args_t));\n"
        for name, size, count, constraint in secret_elements:
            if constraint is None:
                checker_file += "checker_fill_unconstrained((void*) &(dest->%s), %s, %s);\n" % (name, count, size)
            elif constraint.getType() == "fixed":
                checker_file += "checker_fill_fixed((void*) &(dest->%s), %d, %s, %s);\n" % (name, constraint.value, count, size)
            elif constraint.getType() == "range":
                checker_file += "checker_fill_range((void*) &(dest->%s), %d, %d, %s, %s);\n" % (name, constraint.start, constraint.end, count, size)
        for line in fill_struct_additions:
            checker_file += line
        checker_file += "}\n"

        checker_file += "void checker_data_fill_template() {\n"
        for name, size, count, constraint in public_elements:
            if constraint is None:
                checker_file += "checker_fill_unconstrained((void*) &(template.%s), %s, %s);\n" % (name, count, size)
            elif constraint.getType() == "fixed":
                checker_file += "checker_fill_fixed((void*) &(template.%s), %d, %s, %s);\n" % (name, constraint.value, count, size)
            elif constraint.getType() == "range":
                checker_file += "checker_fill_range((void*) &(template.%s), %d, %d, %s, %s);\n" % (name, constraint.start, constraint.end, count, size)
        checker_file += "}\n"

        checker_file += "uint8_t do_one_computation(checker_data_args_t *data) {\n"
        checker_file += "return %s(" % label.function_name
        for id, arg_name in enumerate(arg_names):
            if id > 0:
                checker_file += ", "
            checker_file += "data->%s" % arg_name

        checker_file += ");\n}\n"

        checker_file += """int main(int argc, char* argv[]) {
if (argc < 3) {
exit(1);
}
char run_seed_raw[255];
FILE* run_seed_file = fopen(argv[2], "r");
fread(&run_seed_raw, 255, 1, run_seed_file);
fclose(run_seed_file);
size_t run_seed = 0;
for (int i = 0; i < 255; ++i) {
run_seed += run_seed_raw[i];
}
size_t class_seed = atoi(argv[1]);
checker_data_args_t args;
srand(class_seed);
checker_random_refill();
checker_data_fill_template();
srand(run_seed);
checker_random_refill();
checker_data_fill_struct(&args);
do_one_computation(&args);
}
"""

        
        with open(label.basedir / "ctccp_check.c", "w") as f:
            f.write(checker_file)

        label.header_dirs.append(pathlib.Path(__file__).parent.parent.parent / "checkers" / "common")
        label.source_files.append(label.basedir / "ctccp_check.c")
        label.additional_flags.append("-lm")
        label.additional_flags.append("-g")
        return label

    def runChecker(self, label: SnippetLabel, binary: Path, timeout: int=120) -> CheckerResult:
        framework = binary.parent / "framework.sh"
        target = binary.parent / "targets.txt"
        with open(target, "w") as tf:
            for i in range(10):
                tf.write("TEST %d\n" % i)
        shutil.copy(pathlib.Path(__file__).parent.parent.parent / "checkers" / "DATA" / "framework.sh", framework)
        for i in range(10):
            try:
                proc_res = subprocess.run([str(framework), "--phase1", "-p", "TEST", str(i)], cwd=binary.parent, env={
                    "DATA_ROOT": pathlib.Path(__file__).parent.parent.parent / "checkers" / "DATA" / "DATA-git",
                    "BINARY": binary,
                    "TARGETFILE": target,
                    "DATA_RUN_COUNT": str(3),
                }, stdout=subprocess.PIPE, timeout=timeout)
                data_output = proc_res.stdout.decode()
                if ("Testing 'TEST %d' completed" % i) not in data_output:
                    logging.error("DATA produced an unexpected result:")
                    [logging.error(line) for line in data_output.split("\n")]
                    return CheckerResult(None, False)
                if "Phase1: Results generated" in data_output:
                    logging.debug("Found trace difference on class seed %d." % i)
                    return CheckerResult(False, False)
                logging.debug("Traces for class seed %d were equal." % i)
            except subprocess.TimeoutExpired:
                return CheckerResult(None, True)
        return CheckerResult(True, False)

def registerCheckers() -> list[Checker]:
    return [
        DataChecker()
    ]