from pathlib import Path
from label import SnippetLabel
from . import Compiler
import subprocess
import logging

GCC_BINARY = 'gcc'

class GccCompiler(Compiler):
    __options = {
        "O0": ["-O0"],
        "O1": ["-O1"],
        "O2": ["-O2"],
        "O3": ["-O3"],
        "Ofast": ["-Ofast"],
        "Os": ["-Os"],
    }

    def __init__(self) -> None:
        super().__init__()

    def availableOptionPresets(self) -> list[str]:
        return list(self.__options.keys())

    def identifier(self) -> str:
        return 'gcc'
    
    def compileSnippet(self, label: SnippetLabel, option_preset: str, output_file: Path) -> bool:
        command = [GCC_BINARY,'-g', '-o', str(output_file.resolve())]
        if option_preset in self.__options:
            command += self.__options[option_preset]
        elif option_preset != '' and option_preset is not None:
            raise ValueError("Invalid option preset '%s' provided for %s compiler" % (option_preset, self.identifier()))
        
        for header in label.header_dirs:
            command += ['-I', str(header)]

        for source in label.source_files + label.object_files:
            command.append(str(source))

        for flag in label.additional_flags:
            command.append(flag)
        
        result = subprocess.run(command, cwd=label.basedir, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        if result.returncode != 0:
            logging.warn("%s returned with error code %d.\nstdout:\n%s\n\nstderr:\n%s\n", command, result.returncode, result.stdout.decode(), result.stderr.decode())
            return False
        else: 
            return True
        
    

def registerCompilers() -> list[Compiler]:
    return [
        GccCompiler()
    ]