import subprocess, shutil, os, logging
from pathlib import Path
import json
from pathos.multiprocessing import ProcessPool
import os
p = ProcessPool(nodes=os.cpu_count())

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
        "cc": "clang",
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
        "name": "compcert",
        "options": ["O0", "O1", "Obranchless", "Os"],
        "cc": "ccomp -fstruct-passing",
        "cxx": "",
    },
    {
        "name": "zigcc",
        "options": ["O0", "O1", "O2", "O3", "Ofast", "Os"],
        "cc": "zig cc",
        "cxx": "",
    }
]

TEST_PATHS = [
    # ASCON
    ("./ascon/Implementations/crypto_aead/ascon80pqv12/ref","ascon80pqv12"),
    ("./ascon/Implementations/crypto_aead/ascon128av12/ref","ascon128av12"),
    ("./ascon/Implementations/crypto_aead/ascon128v12/ref","ascon128v12"),
    # Elephant
    ("./elephant/Implementations/crypto_aead/elephant160v2/ref","elephant160v2"),
    ("./elephant/Implementations/crypto_aead/elephant176v2/ref","elephant176v2"),
    ("./elephant/Implementations/crypto_aead/elephant200v2/ref","elephant200v2"),
    # GIFT-COFB
    ("./gift-cofb/Implementations/crypto_aead/giftcofb128v1/ref","giftcofb128v1"),
    # GRAIN-128aead
    ("./grain-128aead/Implementations/crypto_aead/grain128aeadv2/ref","grain128aeadv2"),
    # ISAP
    ("./isap/Implementations/crypto_aead/isapa128av20/ref","isapa128av20"),
    ("./isap/Implementations/crypto_aead/isapa128v20/ref","isapa128v20"),
    ("./isap/Implementations/crypto_aead/isapk128av20/ref","isapk128av20"),
    ("./isap/Implementations/crypto_aead/isapk128v20/ref","isapk128v20"),
    ("./isap/Implementations/crypto_aead/isapxv20/ref","isapxv20"),
    # PHOTON-BEETLE
    ("./photon-beetle/Implementations/crypto_aead/photonbeetleaead128rate32v1/ref","photonbeetleaead128rate32v1"),
    ("./photon-beetle/Implementations/crypto_aead/photonbeetleaead128rate128v1/ref","photonbeetleaead128rate128v1"),
    # ROMULUS
    ("./romulus/Implementations/crypto_aead/romulush/ref","romulush"),
    ("./romulus/Implementations/crypto_aead/romulusm/ref","romulusm"),
    ("./romulus/Implementations/crypto_aead/romulusm_romulush/ref","romulusm_romulush"),
    ("./romulus/Implementations/crypto_aead/romulusn/ref","romulusn"),
    ("./romulus/Implementations/crypto_aead/romulusn_romulush/ref","romulusn_romulush"),
    ("./romulus/Implementations/crypto_aead/romulust/ref","romulust"),
    ("./romulus/Implementations/crypto_aead/romulust_romulush/ref","romulust_romulush"),
    # SPARKLE
    ("./sparkle/Implementations/crypto_aead/schwaemm128128v2/ref","schwaemm128128v2"),
    ("./sparkle/Implementations/crypto_aead/schwaemm192192v2/ref","schwaemm192192v2"),
    ("./sparkle/Implementations/crypto_aead/schwaemm256128v2/ref","schwaemm256128v2"),
    ("./sparkle/Implementations/crypto_aead/schwaemm256256v2/ref","schwaemm256256v2"),
    # TINYJAMBU
    ("./tinyjambu/Implementations/crypto_aead/tinyjambu128v2/ref","tinyjambu128v2"),
    ("./tinyjambu/Implementations/crypto_aead/tinyjambu192v2/ref","tinyjambu192v2"),
    ("./tinyjambu/Implementations/crypto_aead/tinyjambu256v2/ref","tinyjambu256v2"),
    # XOODYAK
    ("./xoodyak/Implementations/crypto_aead/xoodyakround3/ref","xoodyakround3"),
]
    
def compile_to_lib(compiler,option,target_dir):
    c_files = []

    macro_defs = []
    if "isapxv20" in target_dir:
        macro_defs = "-DDEBUG=0 -DKECCAKP400 -DISAP128".split()
    
    # Step 1: List all .h and .c files in the directory
    for filename in os.listdir(target_dir):
        if "genkat" in filename:
                continue
        if filename.endswith('.c'):
            c_files.append(filename)

            
    # Step 2: Generate the gcc command to compile the .c files into a .a library
    def do_compile(c_file):
        print(" ".join(compiler.split() + ["-I.", "-I%s/" % target_dir, "-%s" % option , "-g", *macro_defs, "-c", os.path.join(target_dir, c_file)]))
        subprocess.run(compiler.split() + ["-I.", "-I%s/" % target_dir, "-%s" % option , "-g", *macro_defs, "-c", os.path.join(target_dir, c_file)])


    if c_files:
        # Compile each .c file to its corresponding .o object file
        p.map(do_compile,c_files)
    
        # Generate list of .o files
        o_files = [c_file.replace('.c', '.o') for c_file in c_files]
        
        # Create the .a static library from all .o files
        build_res = subprocess.run(["ar", "rcs", "libcrypt.a"] + o_files)

        if build_res.returncode == 0:
            for o_file in o_files:
                os.remove(o_file)
            return True
        else: 
            return False

    else:
        return False

def gen_json(target_dir, algo_name):
    api_params = {}
    for line in open(os.path.join(target_dir, "api.h"),"r").readlines():
        if line.startswith("#define"):
            split_line = line.strip().split()
            if "VERSION" in line or len(split_line) != 3:
                continue 
            _, param_name, val = split_line
            api_params[param_name] = int(val)
    
    json_res = {}
    json_res["basedir"] = "."
    json_res["sources"] = ["test.c", "%%PLBASE/../nist-lightweight/precompiled/%s.%%COMP_%%COPT.a" % (algo_name)]
    json_res["function"] = "test_aead_encrypt"
    json_res["headers"] = ["%PLBASE/../nist-lightweight/", "%%PLBASE/../nist-lightweight/%s" % target_dir]
    json_res["arguments"] = [
        {
            "name": "c",
            "type": "pointer",
            "to": {
                "type": "array",
                "length": api_params.get("CRYPTO_MSGBYTES",32) + api_params.get("CRYPTO_ABYTES",0),
                "of": {
                    "type": "i8",
                    "secret": False
                }
            }
        },
        {
            "name": "clen",
            "type": "pointer",
            "to": {
                "type": "i64",
                "secret": False,
                "value": {
                    "type": "fixed",
                    "value": api_params.get("CRYPTO_MSGBYTES",32) + api_params.get("CRYPTO_ABYTES",0),
                }
            }
        },
        {
            "name": "m",
            "type": "pointer",
            "to": {
                "type": "array",
                "length": api_params.get("CRYPTO_MSGBYTES",32),
                "of": {
                    "type": "i8",
                    "secret": True
                }
            }
        },
        {
            "name": "mlen",
            "type": "i64",
            "secret": False,
            "value": {
                "type": "fixed",
                "value": api_params.get("CRYPTO_MSGBYTES",32)
            }
        },
        {
            "name": "ad",
            "type": "pointer",
            "to": {
                "type": "array",
                "length": api_params.get("CRYPTO_ADBYTES",0),
                "of": {
                    "type": "i8",
                    "secret": False
                }
            }
        },
        {
            "name": "adlen",
            "type": "i64",
            "secret": False,
            "value": {
                "type": "fixed",
                "value": api_params.get("CRYPTO_ADBYTES",0)
            }
        },
        {
            "name": "nsec",
            "type": "pointer",
            "to": {
                "type": "array",
                "length": api_params.get("CRYPTO_NSECBYTES",0),
                "of": {
                    "type": "i8",
                    "secret": False
                }
            }
        },
        {
            "name": "npub",
            "type": "pointer",
            "to": {
                "type": "array",
                "length": api_params.get("CRYPTO_NPUBBYTES",0),
                "of": {
                    "type": "i8",
                    "secret": False
                }
            }
        },
        {
            "name": "k",
            "type": "pointer",
            "to": {
                "type": "array",
                "length": api_params.get("CRYPTO_KEYBYTES",0),
                "of": {
                    "type": "i8",
                    "secret": True
                }
            }
        },
    ]

    json_object = json.dumps(json_res)
    with open("precompiled/%s.json" % (algo_name), "w") as outfile:
        outfile.write(json_object)

def main():
    Path("./precompiled").mkdir(exist_ok=True)
    # Modify makefile to allow passing compiler settings via environment

    for path,algo_name in TEST_PATHS:
        gen_json(path, algo_name)
        for compiler in COMPILERS:
            for option in compiler["options"]:   
                if Path("precompiled/%s.%s_%s.a" % (algo_name,compiler["name"], option)).exists():
                    continue
                if compile_to_lib(compiler["cc"], option, path):
                    shutil.move(Path("libcrypt.a"), Path("precompiled/%s.%s_%s.a" % (algo_name,compiler["name"], option)))

if __name__ == "__main__":
    main()