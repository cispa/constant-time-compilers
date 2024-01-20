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

def main():
    Path("./precompiled").mkdir(exist_ok=True)
    # Modify makefile to allow passing compiler settings via environment
    with open("bearssl-git/conf/Unix.mk", 'r+') as fp:
        lines = fp.readlines()
        fp.seek(0)
        fp.truncate()
        for line in lines:
            skip_line = False
            for prefix in ["CC =", "CFLAGS =", "LD ="]:
                if line.startswith(prefix):
                    skip_line = True
            if skip_line:
                continue
            fp.write(line)

    for compiler in COMPILERS:
        for option in compiler["options"]:    
            env = os.environ.copy()
            env.update({
                "PWD": str(Path("bearssl-git/").resolve()),
                "CC": compiler["cc"],
                "CXX": compiler["cxx"],
                "CFLAGS": "-Wall -%s -g" % (option),
                "CXXFLAGS": "-Wall -%s -g" % (option)
            })
            subprocess.run(["make", "clean"], cwd=Path("bearssl-git/").resolve())
            build_res = subprocess.run(["make", "-j", "lib"], cwd=Path("bearssl-git/").resolve(), env=env)
            if build_res.returncode == 0:
                shutil.move(Path("bearssl-git/build/libbearssl.a"), Path("precompiled/libbearssl.%s_%s.a" % (compiler["name"], option)))
        

if __name__ == "__main__":
    main()
