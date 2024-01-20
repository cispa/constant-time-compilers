from qiling import Qiling
from capstone.x86 import *

# Source http://unixwiz.net/techtips/x86-jumps.html

class Arm64_Tracer:
    def __init__(self, logfile):
        self.logfile = logfile

    def get_flags(self,bits):
        """
        get flags from ql.reg.eflags
        """

        return {
                "CF" : bits & 0x0001 != 0, # CF, carry flag
                "PF" : bits & 0x0004 != 0, # PF, parity flag
                "AF" : bits & 0x0010 != 0, # AF, adjust flag
                "ZF" : bits & 0x0040 != 0, # ZF, zero flag
                "SF" : bits & 0x0080 != 0, # SF, sign flag
                "OF" : bits & 0x0800 != 0, # OF, overflow flag
                }

    def trace(self, ql: Qiling, address: int, size: int, data) -> None:
        # Get disassembler and logfile
        md, log = data[0], data[1]

        # Get instruction from memory
        buf = ql.mem.read(address, size)
        for insn in md.disasm(buf, address):
            # Check if instruction is conditional branch
            match insn.mnemonic:
                case "jo":
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{flags["OF"]}\n')
                case "jno":
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{not flags["OF"]}\n')
                case "js":
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{flags["SF"]}\n')
                case "jns":
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{not flags["SF"]}\n')
                case "je" | "jz":
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{flags["ZF"]}\n')
                case "jne" | "jnz":
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{not flags["ZF"]}\n')
                case "jb" | "jnae" | "jc": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{flags["CF"]}\n')
                case "jnb" | "jae" | "jnc": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{not flags["CF"]}\n')
                case "jbe" | "jna": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{flags["CF"] or flags["ZF"]}\n')
                case "ja" | "jnbe": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{not flags["CF"] and not flags["ZF"]}\n')
                case "jl" | "jnge": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{flags["SF"] != flags["OF"]}\n')
                case "jge" | "jnl": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{flags["SF"] == flags["OF"]}\n')
                case "jle" | "jng": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{flags["ZF"] or (flags["SF"] == flags["OF"])}\n')
                case "jg" | "jnle": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{not flags["ZF"] and (flags["SF"] == flags["OF"])}\n')
                case "jp" | "jpe": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{flags["PF"]}\n')
                case "jnp" | "jpo": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{not flags["PF"]}\n')
                case "jcxz" | "jecxz": 
                    flags = self.get_flags(ql.arch.regs.eflags)
                    self.logfile.write(f'{address:#x}:{ql.arch.regs.ecx == 0}\n')
                
