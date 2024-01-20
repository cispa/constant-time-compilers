from qiling import Qiling
from capstone.riscv import *

# Source https://riscv.org/wp-content/uploads/2017/05/riscv-spec-v2.2.pdf

class Riscv64_Tracer:
    def __init__(self, logfile):
        self.logfile = logfile

    def get_ops(self, ql: Qiling, insn):
        ops = []
        for i in insn.operands: 
            if i.type == RISCV_OP_REG:
                regname = insn.reg_name(i.reg)
                regval = ctypes.c_uint64(ql.arch.regs.read(regname)).value
                ops.append(regval)
        return ops

    def trace(self, ql: Qiling, address: int, size: int, data) -> None:
        # Get disassembler and logfile
        md, log = data[0], data[1]

        buf = ql.mem.read(address, size)
        for insn in md.disasm(buf, address):
            # Check if instruction is conditional branch
            match insn.mnemonic:
                case "beq":
                    ops = self.get_ops(ql,insn)
                    self.logfile.write(f'{address:#x}:{ops[0] == ops[1]}\n')
                case "bne":
                    ops = self.get_ops(ql,insn)
                    self.logfile.write(f'{address:#x}:{ops[0] != ops[1]}\n')
                case "blt" | "bltu":
                    ops = self.get_ops(ql,insn)
                    self.logfile.write(f'{address:#x}:{ops[0] < ops[1]}\n')
                case "bge" | "bgeu":
                    ops = self.get_ops(ql,insn)
                    self.logfile.write(f'{address:#x}:{ops[0] >= ops[1]}\n')
                case "bgt" | "bgtu":
                    ops = self.get_ops(ql,insn)
                    self.logfile.write(f'{address:#x}:{ops[0] > ops[1]}\n')
                case "ble" | "bleu":
                    ops = self.get_ops(ql,insn)
                    self.logfile.write(f'{address:#x}:{ops[0] <= ops[1]}\n')

