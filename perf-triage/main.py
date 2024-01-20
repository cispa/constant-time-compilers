import subprocess
import os
from shlex import split
import sys
import pprint

tmp_file_name = "a.out"

OPT_LEVELS = ["O0", "O1", "O2", "O3", "Ofast", "Os"]
DEBUG_COMMANDS = False


def compile(file, flags):
    command = ["gcc", "-Q"] + flags + ["-o", f"{tmp_file_name}", file]
    if DEBUG_COMMANDS:
        print(" ".join(command))
    subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)


def check_is_ct():
    command = ["valgrind", f"./{tmp_file_name}"]
    if DEBUG_COMMANDS:
        print(" ".join(command))
    res = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return not b"uninitialised value" in res.stderr


def get_flags(opt_level):
    command = f"gcc -{opt_level} -Q --help=optimizers | grep enabled"
    if DEBUG_COMMANDS:
        print(command)
    res = subprocess.check_output(command, stderr=subprocess.STDOUT, shell=True)
    flags = split(res.decode().strip().replace("[enabled]", ""))
    return set(flags)


def get_option_change(set1, set2):
    added = set()
    removed = set()
    for elem in set1:
        if elem not in set2:
            removed.add(elem)
    for elem in set2:
        if elem not in set1:
            added.add(elem)
    return added, removed


opt_level_to_flags = {opt_level: get_flags(opt_level) for opt_level in OPT_LEVELS}

for file in os.listdir("examples/"):
    if not file.endswith(".c"):
        continue

    file_path = os.path.join("examples/", file)
    previous_flags = set()

    # check if behavior is the same with options per opt level
    for opt_level in OPT_LEVELS:
        flags = [opt for opt in opt_level_to_flags[opt_level]]
        compile(file_path, flags)
        toggle_result = check_is_ct()
        compile(file_path, [f"-{opt_level}"])
        original_result = check_is_ct()
        assert toggle_result == original_result

    previous_flags = set()
    previous_result = None
    for opt_level in OPT_LEVELS:
        if previous_result != None:
            print("\n" + opt_level + "\n")
            base_flags = previous_flags.copy()
            added_flags = opt_level_to_flags[opt_level] - base_flags
            removed_flags = base_flags - opt_level_to_flags[opt_level]

            for flag in added_flags:
                compile(file_path, list(base_flags) + [flag])
                flag_result = check_is_ct()
                if flag_result != previous_result:
                    print("Flags:")
                    pprint.pprint(list(base_flags) + [flag])
                    print(f"\nUsing {flag} flips the result!")
                    sys.exit(0)

            for flag in added_flags:
                compile(file_path, list(base_flags - set([flag])))
                flag_result = check_is_ct()
                if flag_result != previous_result:
                    print(f"\nNot using {flag} flips the result!")
                    sys.exit(0)

        # update stuff for next iteration
        compile(file_path, [f"-{opt_level}"])
        previous_result = check_is_ct()
        previous_flags = opt_level_to_flags[opt_level]
