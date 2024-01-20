from pathlib import Path 
from label import SnippetLabel
from compilers.collector import Compiler

class CheckerResult:
    data_oblivious: bool
    timeout: bool

    def __str__(self) -> str:
        if self.timeout:
            return 'timeout'
        return 'data_oblivious:' + str(self.data_oblivious) 
    
    def __init__(self, data_oblivious: bool,timeout: bool) -> None:
        self.data_oblivious = data_oblivious
        self.timeout = timeout

class Checker:
    def identifier(self) -> str:
        '''Returns the identifier of the checker class. Checker identifiers should only consist of alphanumeric characters, dashes and underscores.'''
        raise NotImplementedError()
    
    def compatibleCompilers(self, compilers: list[Compiler]) -> list[Compiler]:
        '''Returns the sublist of given compilers that are compatible with this checker.'''
        return compilers
    
    def prepareSnippet(self, label: SnippetLabel) -> SnippetLabel:
        '''Prepares a snippet for compilation to work with this checker'''
        return label

    def runChecker(self, label: SnippetLabel, binary: Path, timeout: int) -> CheckerResult:
        '''Runs the checker on a given binary compiled from a previously-prepared snippet'''
        raise NotImplementedError()

    def is_parralelizeble(self) -> bool:
        '''Returns if the checker can be run with multiple instances in parralel'''
        return True
