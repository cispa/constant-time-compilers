from qiling import *
from qiling.const import QL_VERBOSE
from pwn import ELF
import click

from tracers.aarch64_tracer import Aarch64_Tracer
from tracers.arm64_tracer import Arm64_Tracer
from tracers.riscv64_tracer import Riscv64_Tracer
from tracers.patch_hook import Patch_Hook

SINGLETON = True
HOOK = None

NEEDSPATCH = {
    "aarch64",
}  # Architectures that need operand patching bc they are not fully supported


def skip_insn(ql: Qiling, addr):
    ql.log.debug("Instruction unsupported, skipping")
    ql.arch.regs.write("pc", ql.arch.regs.read("pc") + 4)


def set_trace(ql: Qiling, data):
    global SINGLETON, HOOK
    if SINGLETON:
        SINGLETON = False
        ql.log.info("Registerd branch tracer")
        tracer, log = data
        HOOK = ql.hook_code(tracer.trace, user_data=[ql.arch.disassembler, log])


def unset_trace(ql: Qiling):
    global HOOK
    if HOOK:
        ql.log.info("Unregistered branch tracer")
        ql.hook_del(HOOK)
        ql.stop()
        HOOK = None


def snapshot(ql: Qiling):
    ql.log.info("Snapshotting programm")
    return ql.save()


@click.command()
@click.argument("program")
@click.argument("args", default="")
@click.argument("logfile")
@click.option("--function", default="main", help="Function to trace")
@click.option("--rootfs", default=".", help="Rootfs for binary")
@click.option(
    "--verbose",
    default="DEFAULT",
    type=click.Choice(["OFF", "DEFAULT", "DEBUG", "DISASM"], case_sensitive=False),
)
def collect_trace_command(program, args, logfile, function, rootfs, verbose):
    """
    Produce branch trace of a program. Arguments can be provided whith the ARGS parameter.
    The results of the trace are written to LOGFILE.
    """
    collect_trace(program, args, logfile, function, rootfs, verbose)


def collect_trace(program, args, logfile, function, rootfs, verbose):
    # Get function to trace
    elf = ELF(program)
    fun = elf.functions[function]
    start = fun.address
    end = fun.address + fun.size - 1

    # Open log file
    log = open(logfile, "w")

    # Dictionary mapping architectures to tracers
    arch_tracer_dict = {
        "amd64": Arm64_Tracer(log),
        "aarch64": Aarch64_Tracer(log),
        "em_riscv": Riscv64_Tracer(log),
    }

    # Start emulator
    ql = Qiling([program] + args.split(), rootfs, verbose=QL_VERBOSE[verbose])

    # Log binary info
    ql.log.info(f"Arch: {elf.arch}, Os: {elf.os} , Endian: {elf.endian}")

    # Set disassembler to detailled output
    ql.arch.disassembler.detail = True

    # Set singleton for hook registration to true
    global SINGLETON
    SINGLETON = True

    # Register patch handler if needed
    if elf.arch in NEEDSPATCH:
        ql.log.info("Skip hook installed")
        ql.hook_intno(skip_insn, 0x1)
    # Additionaly skip breakpoints in mips
    if elf.arch == "mips":
        ql.hook_intno(skip_insn, 0x12)

    # Register activation hook on function entry
    ql.hook_address(set_trace, start, user_data=[arch_tracer_dict[elf.arch], log])

    # Register deactivation hook on function exit
    ql.hook_address(unset_trace, end)

    # Set thread local storage if on arm64
    if elf.arch == "amd64":
        addr = ql.mem.map_anywhere(4096)
        ql.arch.regs.write("fs", addr)

    # do the magic!
    ql.run()


if __name__ == "__main__":
    collect_trace_command()
