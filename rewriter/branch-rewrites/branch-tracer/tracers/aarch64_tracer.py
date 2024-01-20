from qiling import Qiling
from capstone.arm64 import * 

# Source https://azeria-labs.com/arm-conditional-execution-and-branching-part-6/

class Aarch64_Tracer:

    def __init__(self,logfile):
        self.logfile = logfile

    def get_flags(self,bits):
        return {
                "C" : bits & 0x20000000 != 0, # CF, carry flag
                "Z" : bits & 0x40000000 != 0, # ZF, zero flag
                "V" : bits & 0x10000000 != 0, # VF, overflow flag
                "N" : bits & 0x80000000 != 0, # NF, negative flag
        }

    def trace(self, ql: Qiling, address: int, size: int, data) -> None:
        # Get disassembler and logfile
        md, log = data[0], data[1]

        # Get instruction from memory
        buf = ql.mem.read(address, size)
        for insn in md.disasm(buf, address):
            match insn.mnemonic:
                case "b.eq":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{flags["Z"]}\n')
                case "b.ne":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{not flags["Z"]}\n')
                case "b.cs":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{flags["C"]}\n')
                case "b.cc":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{not flags["C"]}\n')
                case "b.mi":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{flags["N"]}\n')
                case "b.pl":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{not flags["N"]}\n')
                case "b.vs":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{flags["V"]}\n')
                case "b.vc":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{not flags["V"]}\n')
                case "b.hi":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{flags["C"] and not flags["Z"]}\n')
                case "b.ls":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{not flags["C"] or not flags["Z"]}\n')
                case "b.ge":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{flags["N"] == flags["V"]}\n')
                case "b.lt":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{flags["N"] != flags["V"]}\n')
                case "b.gt":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{not flags["Z"] and (flags["N"] == flags["V"])}\n')
                case "b.le":
                    flags = self.get_flags(ql.arch.regs.pstate)
                    self.logfile.write(f'{address:#x}:{flags["Z"] and (flags["N"] != flags["V"])}\n')
