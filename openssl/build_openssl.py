import subprocess, shutil, os, logging
from pathlib import Path

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
    #{
    #    "name": "compcert",
    #    "options": ["O0", "O1", "Obranchless", "Os"],
    #    "cc": "ccomp -fall",
    #    "cxx": "",
    #},
    #{
    #    "name": "zigcc",
    #    "options": ["O0", "O1", "O2", "O3", "Ofast", "Os"],
    #    "cc": "zig cc -fno-sanitize=undefined  -fdebug-default-version=4",
    #    "cxx": "",
    #}
]

def main():
    Path("./precompiled").mkdir(exist_ok=True)
    # Modify makefile to allow passing compiler settings via environment
    with open("openssl-git/Makefile", 'r+') as fp:
        lines = fp.readlines()
        fp.seek(0)
        fp.truncate()
        for line in lines:
            skip_line = False
            for prefix in ["CC=", "CXX=", "CFLAGS=", "CXXFLAGS="]:
                if line.startswith(prefix):
                    skip_line = True
            if skip_line:
                continue
            line = line.replace("CC=\"$(CC)\"", "CC=\"gcc\"") # fix for building asm
            fp.write(line)

    for compiler in COMPILERS:
        for option in compiler["options"]:    
            env = os.environ.copy()
            env.update({
                "PWD": str(Path("openssl-git/").resolve()),
                "CC": compiler["cc"],
                "CXX": compiler["cxx"],
                "CFLAGS": "-Wall -%s -g" % (option),
                "CXXFLAGS": "-Wall -%s -g" % (option)
            })
            subprocess.run(["make", "clean"], cwd=Path("openssl-git/").resolve())
            build_res = subprocess.run(["make", "-j", "build_libs"], cwd=Path("openssl-git/").resolve(), env=env)
            if build_res.returncode == 0:
                shutil.move(Path("openssl-git/libcrypto.a"), Path("precompiled/libcrypto.%s_%s.a" % (compiler["name"], option)))
        

if __name__ == "__main__":
    main()
