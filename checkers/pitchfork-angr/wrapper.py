import sys, pathlib, json
work_dir = pathlib.Path(__file__).parent.resolve()
sys.path.append(str(work_dir / "pitchfork-angr"))
from pitchfork import funcEntryState, getSimgr, runSimgr, armSpectreExplicitChecks, armSpectreOOBChecks, addSecretObject
from stubs import addDevURandom
from abstractdata import publicValue, secretValue, pointerTo, pointerToUnconstrainedPublic, publicArray, secretArray, array, struct
import angr
import logging
# logging.getLogger("pitchfork").setLevel(logging.WARN)

def run(simgr):
    def terminateOnViolation(simgr):
        if 'spectre_violation' in simgr.stashes and len(simgr.spectre_violation) > 0:
            print('spectre violation detected, terminating.')
            sys.exit(1)
    simgr.run(step_func=terminateOnViolation)
    return simgr

def addDevURandom(state):
    # we don't need the data in /dev/urandom to be symbolic, any concrete data should do
    devurandom = angr.SimFile("devurandom", writable=False, concrete=True, has_end=True,  # if /dev/urandom actually gets to the end of this string and returns ***REMOVED***, we want to be notified and have things fail rather than have it just invisibly generate symbolic data
        content="fdjkslaiuoewouriejaklhewf,masdnm,fuiorewewrhewjlfawjjkl!$RU(!KshjkLAFjfsdu*(SD(*(*(Asafdlksfjfsisefiklsdanm,fsdhjksfesijlfjesfes,se,esf,jkflesejiolflajiewmn,.waehjkowaejhfofyoivnm,cxhvgudyviuovnxcvncvixocjvsidooiI*DVJSKLFE*#L@N#@$$*Dsjklfjksd8fds9#WU*#(R@$JMksldfjfsd89J*F(F#KLJRJ*(RW")
    state.fs.insert('/dev/urandom', devurandom)
    state.options.discard(angr.options.SHORT_READS)

def addDevRandom(state):
    # we don't need the data in /dev/random to be symbolic, any concrete data should do
    devrandom = angr.SimFile("devrandom", writable=False, concrete=True, has_end=True,  # if /dev/random actually gets to the end of this string and returns ***REMOVED***, we want to be notified and have things fail rather than have it just invisibly generate symbolic data
        content="fdjkslaiuoewouriejaklhewf,masdnm,fuiorewewrhewjlfawjjkl!$RU(!KshjkLAFjfsdu*(SD(*(*(Asafdlksfjfsisefiklsdanm,fsdhjksfesijlfjesfes,se,esf,jkflesejiolflajiewmn,.waehjkowaejhfofyoivnm,cxhvgudyviuovnxcvncvixocjvsidooiI*DVJSKLFE*#L@N#@$$*Dsjklfjksd8fds9#WU*#(R@$JMksldfjfsd89J*F(F#KLJRJ*(RW")
    state.fs.insert('/dev/random', devrandom)
    state.options.discard(angr.options.SHORT_READS)

def main(args: "list[str]") -> None:
    if len(args) != 4:
        print("Usage: wrapper.py <binary> <function> <arguments_file>")
        exit(2)

    binary_path = pathlib.Path(args[1])
    func_name = args[2]
    arguments_path = pathlib.Path(args[3])
    with open(arguments_path, "r") as f:
        arguments = json.load(f)
    
    proj = angr.Project(str(binary_path.resolve()))
    state = funcEntryState(proj, func_name, [])
    
    try:
        for arg in arguments:
            addSecretObject(proj, state, str(arg["name"]), int(arg["size"]))
    except:
        print("Error caught.")
        exit(2)

    addDevRandom(state)
    addDevURandom(state)
    armSpectreExplicitChecks(proj, state, [], False, [])
    simgr = getSimgr(proj, state, spec=False)
    run(simgr)
    sys.exit(0)

main(sys.argv)