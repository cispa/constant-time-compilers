from . import Compiler, gcc, clang, aocc, icx, compcert, zigcc

COMPILER_MODULES: list = [
    gcc,
    clang,
    aocc,
    icx,
    compcert,
    zigcc
]

def collectCompilers() -> list[Compiler]:
    compilers: list[Compiler] = list()

    for module in COMPILER_MODULES:
        if hasattr(module, 'registerCompilers') and hasattr(module.registerCompilers, '__call__'):
            compilers += module.registerCompilers()

    return compilers