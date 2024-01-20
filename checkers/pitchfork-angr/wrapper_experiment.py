import sys
import pathlib
workdir = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(workdir / "pitchfork-angr"))

print(sys.path)

import pitchfork
from pitchfork import funcEntryState, getSimgr, runSimgr, armSpectreExplicitChecks, armSpectreOOBChecks, addSecretObject
from abstractdata import publicValue, secretValue, pointerTo, pointerToUnconstrainedPublic, publicArray, secretArray, array, struct
import angr

binary_path = workdir / '..' / '..' / 'experiment' / 'test_pitchfork'
func_name = "main"


def violationDetected(simgr):
    return 'spectre_violation' in simgr.stashes and len(simgr.spectre_violation) > 0

proj = angr.Project(str(binary_path.resolve()))
state = funcEntryState(proj, func_name, [])


addSecretObject(proj, state, 'arg_x', 4)
addSecretObject(proj, state, 'arg_y', 4)

# armSpectreOOBChecks(proj, state)
armSpectreExplicitChecks(proj, state, [], False, [])
simgr = getSimgr(proj, state, spec=False)
result = runSimgr(simgr)
print("RESULT")
print(violationDetected(result))
print(result.stashes)