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
        "cxx": "clang++",
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
        "name": "zigcc",
        "options": ["O0", "O1", "O2", "O3", "Ofast", "Os"],
        "cc": "zig cc -fno-sanitize=undefined -fdebug-default-version=4",
        "cxx": "",
    },
    {
        "name": "compcert",
        "options": ["O0", "O1", "Obranchless", "Os"],
        "cc": "ccomp -fall -g",
        "cxx": "",
    },
]

def main():
    Path("./precompiled").mkdir(exist_ok=True)

    for compiler in COMPILERS:
        for option in compiler["options"]: 
            env = os.environ.copy()
            env.update({
                "PWD": str(Path("ipp-crypto-git/").resolve()),
                "CC": compiler["cc"],
                "CXX": compiler["cxx"],
                "WARNING_CFLAGS":"",
                "CFLAGS": "-Wall -%s -g" % (option),
                "CXXFLAGS": "-Wall -%s -g" % (option)
            })
            subprocess.run(["make", "clean"], cwd=Path("wolfssl-stable/").resolve())
            subprocess.run(["./configure", "--enable-shared=no", "--enable-static=yes", "--enable-all-crypto"],cwd=Path("wolfssl-stable/").resolve(), env=env)
            build_res = subprocess.run(["make", "-j"], cwd=Path("wolfssl-stable/").resolve(), env=env)
            if build_res.returncode == 0:
                shutil.move(Path("wolfssl-stable/src/.libs/libwolfssl.a"), Path("precompiled/libwolfssl.%s_%s.a" % (compiler["name"], option)))        

if __name__ == "__main__":
    main()
