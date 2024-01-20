from . import Checker, CheckerResult, ctgrind, data, dudect, pitchfork, library

CHECKER_MODULES: list = [
    dudect, 
    ctgrind, 
    data, 
    pitchfork
]

def collectCheckers() -> list[Checker]:
    checkers: list[Checker] = list()

    for module in CHECKER_MODULES:
        if hasattr(module, 'registerCheckers') and hasattr(module.registerCheckers, '__call__'):
            checkers += module.registerCheckers()

    return checkers