import click
import subprocess
import os
from pathlib import Path

@click.argument("target_binary")
@click.argument("instruction_list")
@click.argument("e9patch_path")
@click.command()
def rewrite(e9patch_path,instruction_list,target_binary):
   """
   Rewrite binary to add secret dependent control and data flow.

   E9PATCH_PATH: Path to the e9patch build folder

   INSTRUCTION_LIST: Comma seperated list of instructions that should be rewritten

   TARGET_BINARY: Binary that should be rewritten
   """

   # Get instructions from list
   instructions = instruction_list.split(",")
   # Build matcher
   matcher ="'" + " or ".join([f"mnemonic==\"{inst}\"" for inst in instructions]) + "'" 

   # Compile rewrite using e9compile
   print("[+] Compiling patch trampoline")
   e9compile_path = Path(e9patch_path).joinpath("./e9compile.sh")
   subprocess.run([e9compile_path.as_posix(), "../rewrite.c"])

   # Rewrite binary using e9tool
   print("[+] Patching binary")
   e9tool_path = Path(e9patch_path).joinpath("./e9tool")
   cmd = " ".join(["./"+e9tool_path.as_posix(), "-O0", "-M", matcher, "-P", "'entry(src[0],src[1])@rewrite'", target_binary])
   subprocess.run(cmd,shell=True)

   print("[+] Cleaning up")
   os.rename("a.out", target_binary)
   

if __name__ == "__main__":
   rewrite()