import subprocess, shutil, os, logging
from pathlib import Path
import json

COMPILERS = [
    {
        "name": "gcc",
        "options": ["O0", "O1", "O2", "O3", "Ofast", "Os"],
        "cc": "gcc",
        "cxx": "g++",
    },
    {
        "name": "clang",
        "options": ["O0", "O1", "O2", "O3", "Ofast", "Os"],
        "cc": "clang -fdebug-default-version=4",
        "cxx": "clang++ -fdebug-default-version=4",
    },
    {
        "name": "aocc",
        "options": ["O0", "O1", "O2", "O3", "Ofast", "Os"],
        "cc": "/opt/AMD/aocc-compiler-4.0.0/bin/clang",
        "cxx": "/opt/AMD/aocc-compiler-4.0.0/bin/clang++",
    },
    {
        "name": "icx",
        "options": ["O0", "O1", "O2", "O3", "Ofast", "Os"],
        "cc": "/opt/intel/oneapi/compiler/latest/linux/bin/icx-cc",
        "cxx": "/opt/intel/oneapi/compiler/latest/linux/bin/icx",
    },
    {
        "name": "compcert",
        "options": ["O0", "O1", "Obranchless", "Os"],
        "cc": "ccomp -fall",
        "cxx": "",
    },
    {
        "name": "zigcc",
        "options": ["O0", "O1", "O2", "O3", "Ofast", "Os"],
        "cc": "zig cc -fno-sanitize=undefined -fdebug-default-version=4",
        "cxx": "",
    }
]

def compile_to_lib(compiler,option):
    c_files = []
    
    # Step 1: List all .h and .c files in the directory
    for filename in os.listdir("./ct-toolkit-git/src"):
        if filename.endswith('.c'):
            c_files.append(filename)
            
    # Step 2: Generate the gcc command to compile the .c files into a .a library
    if c_files:
        # Compile each .c file to its corresponding .o object file
        for c_file in c_files:
            subprocess.run(compiler.split() + ["-g", "-%s" % option, "-I./ct-toolkit-git/inc", "-c", os.path.join("./ct-toolkit-git/src", c_file)])
        
        # Generate list of .o files
        o_files = [c_file.replace('.c', '.o') for c_file in c_files]
        
        # Create the .a static library from all .o files
        build_res = subprocess.run(["ar", "rcs", "libcttk.a"] + o_files)

        if build_res.returncode == 0:
            for o_file in o_files:
                os.remove(o_file)
            return True
        else: 
            return False

    else:
        return False

def main():
    Path("./precompiled").mkdir(exist_ok=True)
    # Modify makefile to allow passing compiler settings via environment

    for compiler in COMPILERS:
        for option in compiler["options"]:   
            if Path("precompiled/libcttk.%s_%s.a" % (compiler["name"], option)).exists():
                continue
            if compile_to_lib(compiler["cc"], option):
                shutil.move(Path("libcttk.a"), Path("precompiled/libcttk.%s_%s.a" % (compiler["name"], option)))

if __name__ == "__main__":
    main()