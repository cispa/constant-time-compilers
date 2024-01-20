from pathlib import Path 
from label import SnippetLabel

class Compiler:
    def identifier(self) -> str:
        '''Returns the identifier of the compiler class. Compiler identifiers should only consist of alphanumeric characters, dashes and underscores.'''
        raise NotImplementedError()
    
    def availableOptionPresets(self) -> list[str]:
        '''Returns a list of available compiler option presets'''
        raise NotImplementedError()

    def compileSnippet(self, label: SnippetLabel, option_preset: str, output_file: Path) -> bool:
        '''Takes a snippet as provided by the label and compiles it into the given output file. Returns if compilation was successful.'''
        raise NotImplementedError()
