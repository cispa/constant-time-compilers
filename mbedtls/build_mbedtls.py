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
            # Special case for compcert which does not support compiler intrinsics  
            if compiler["name"] == "compcert":
                subprocess.run(["scripts/config.py", "unset", "MBEDTLS_AESNI_C"], cwd=Path("mbedtls-git/").resolve()) 
            env = os.environ.copy()
            env.update({
                "PWD": str(Path("mbedtls-git/").resolve()),
                "CC": compiler["cc"],
                "CXX": compiler["cxx"],
                "WARNING_CFLAGS":"",
                "CFLAGS": "-Wall -%s -g" % (option),
                "CXXFLAGS": "-Wall -%s -g" % (option)
            })
            subprocess.run(["make", "clean"], cwd=Path("mbedtls-git/").resolve())
            build_res = subprocess.run(["make", "-j", "lib"], cwd=Path("mbedtls-git/").resolve(), env=env)
            if build_res.returncode == 0:
                shutil.move(Path("mbedtls-git/library/libmbedtls.a"), Path("precompiled/libmbedtls.%s_%s.a" % (compiler["name"], option)))
                shutil.move(Path("mbedtls-git/library/libmbedx509.a"), Path("precompiled/libmbedx509.%s_%s.a" % (compiler["name"], option)))
                shutil.move(Path("mbedtls-git/library/libmbedcrypto.a"), Path("precompiled/libmbedcrypto.%s_%s.a" % (compiler["name"], option)))
        

if __name__ == "__main__":
    main()
