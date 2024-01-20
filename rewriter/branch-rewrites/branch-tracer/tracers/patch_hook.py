# This is a really diry hack to skip unupported instruction remove or emulate them if needed


from qiling import Qiling
from capstone.mips import *
from capstone.arm64 import *

class Patch_Hook:

    def __init__(self, arch):
        self.arch = arch
        

    def skip(self, ql: Qiling, address: int, size: int, md) -> None:
        
        buf = ql.mem.read(address, size)
        for insn in md.disasm(buf, address):
            if self.arch == "arm64" and (insn.id == ARM64_INS_CASA or insn.id == ARM64_INS_SWPL):  # TODO: emulate if needed
                            ql.log.debug("Instruction unsupported, skipping")
                            ql.arch.regs.write("pc", ql.arch.regs.read("pc") + 4)

    def patch(self, ql: Qiling, address: int, size: int, data) -> None:
        pass #TODO: Skip and emulate instructions