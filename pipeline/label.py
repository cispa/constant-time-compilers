from pathlib import Path
import json
import copy

class ValueConstraint:
    def getType(self):
        raise NotImplemented()
    
    def exportToDict(self) -> dict:
        raise NotImplementedError()

class FixedValueConstraint(ValueConstraint):
    value: int

    def __init__(self, value: int) -> None:
        self.value = value

    def getType(self):
        return "fixed"
    
    def exportToDict(self) -> dict:
        return {
            "type": "fixed",
            "value": self.value
        }

class RangeValueConstraint(ValueConstraint):
    start: int
    end: int

    def __init__(self, start, end) -> None:
        self.start = start
        self.end = end

    def getType(self):
        return "range"
    
    def exportToDict(self) -> dict:
        return {
            "type": "range",
            "start": self.start,
            "end": self.end
        }

class Argument:
    secret: bool = False

    def getType(self) -> str:
        raise NotImplementedError()
    
    def exportToDict(self) -> dict:
        raise NotImplementedError()

class IntegerArgument(Argument):
    bits: int
    value: ValueConstraint

    def __init__(self, bits: int, value: ValueConstraint, secret: bool = False) -> None:
        self.bits = bits
        self.value = value
        self.secret = secret

    def getType(self) -> str:
        return 'integer'
    
    def exportToDict(self) -> dict:
        if self.value is None:
            return {
                "type": "i%d" % self.bits
            }
        
        return {
            "type": "i%d" % self.bits,
            "value": self.value.exportToDict(),
            "secret": self.secret
        }

class ArrayArgument(Argument):
    length: int
    of: Argument

    def __init__(self, length: int, of: Argument) -> None:
        self.length = length
        self.of = of

    def getType(self) -> str:
        return 'array'

    def exportToDict(self) -> dict:
        return {
            "type": "array",
            "length": self.length,
            "of": self.of.exportToDict()
        }

class PointerArgument(Argument):
    to: Argument

    def __init__(self, to: Argument) -> None:
        self.to = to

    def getType(self) -> str:
        return 'pointer'
    
    def exportToDict(self) -> dict:
        return {
            "type": "pointer",
            "to": self.to.exportToDict()
        }

class PreparationLabel:
    function: str = ""
    size: int = -1

    def __init__(self, size: int, function: str) -> None:
        self.size = size
        self.function = function


class SnippetLabel:
    basedir: Path
    source_files: list[Path] = []
    object_files: list[Path] = []
    header_dirs: list[Path] = []
    additional_flags: list[str] = []
    function_name: str = "main"
    arguments: list[Argument] | None = []
    preparation: PreparationLabel | None = None

    def __init__(self) -> None:
        self.basedir = None
        self.source_files = []
        self.object_files = []
        self.header_dirs = []
        self.additional_flags = []
        self.function_name = ""
        self.arguments = []

    def exportToDict(self) -> dict:
        return {
            "basedir":      str(self.basedir.resolve()),
            "sources":      [copy.copy(p) for p in self.source_files],
            "headers":      [copy.copy(p) for p in self.header_dirs],
            "objects":      [copy.copy(p) for p in self.object_files],
            "flags":        [copy.copy(p) for p in self.additional_flags],
            "function":     copy.copy(self.function_name),
            "arguments":    [copy.deepcopy(arg.exportToDict()) for arg in self.arguments]
        }

def parseArgument(data: dict) -> Argument:
    '''Parse an argument declared in a snippet label file'''

    def parseValueConstraint(data: dict) -> ValueConstraint:
        '''Parse a value constraint declared in a snippet label file'''
        if not isinstance(data, dict) or 'type' not in data:
            raise ValueError("Invalid or malformed value constraint declaration '%s'" % (json.dumps(data)))

        if data['type'] == 'fixed':
            if 'value' not in data or not isinstance(data['value'], int):
                raise ValueError("Missing or invalid value inside fixed value constraint declaration '%s'" % (json.dumps(data)))
            return FixedValueConstraint(data['value'])
        elif data['type'] == 'range':
            if 'start' not in data or not isinstance(data['start'], int):
                raise ValueError("Missing or invalid start value inside range value constraint declaration '%s'" % (json.dumps(data)))
            if 'end' not in data or not isinstance(data['end'], int):
                raise ValueError("Missing or invalid end value inside range value constraint declaration '%s'" % (json.dumps(data)))
            if data['start'] > data['end']:
                raise ValueError("Malformed range value constraint declaration: start (%d) > end (%d)" % (data['start'], data['end']))
            return RangeValueConstraint(data['start'], data['end'])
        else:
            raise ValueError("Invalid value constraint type '%s' (expected 'fixed' or 'range')" % (data['type']))

    if not isinstance(data, dict) or 'type' not in data:
        raise ValueError("Invalid or malformed argument declaration '%s'" % (json.dumps(data)))
    
    arg_type = data['type']
    if arg_type in ['i8', 'i16', 'i32', 'i64']:
        bits = int(arg_type[1:])
        value = parseValueConstraint(data['value']) if 'value' in data else None
        secret = bool(data['secret']) if 'secret' in data else False
        return IntegerArgument(bits, value, secret)
    elif arg_type == 'array':
        if 'length' not in data or not isinstance(data['length'], int):
            raise ValueError("Missing or invalid array length inside array argument declaration '%s'" % (json.dumps(data)))
        if 'of' not in data or not isinstance(data['of'], dict):
            raise ValueError("Missing or invalid array length inside array argument declaration '%s'" % (json.dumps(data)))
        return ArrayArgument(data['length'], parseArgument(data['of']))
    elif arg_type == 'pointer':
        if 'to' not in data or not isinstance(data['to'], dict):
            raise ValueError("Missing or invalid pointer target inside pointer argument declaration '%s'" % (json.dumps(data)))
        return PointerArgument(parseArgument(data['to']))
    else:
        raise ValueError("Invalid argument type provided in argument declaration '%s'" % (json.dumps(data)))

def parseLabelFromFile(path: Path) -> SnippetLabel:
    '''Parse a snippet label file from json to SnippetLabel representation and validate it.'''
    data = None

    # Load data
    with open(path, "r") as file_handle:
        data = json.load(file_handle)
    if data is None:
        raise ImportError("Could not load label file.")
    
    data['parent_path'] = path.parent
    return parseLabelFromDict(data)

def parseLabelFromDict(data: dict):
    label = SnippetLabel()

    # Parse base directory
    if 'basedir' in data:
        basedir = Path(data['basedir'])
        if basedir.is_absolute():
            label.basedir = basedir.resolve()
        else:
            label.basedir = (data['parent_path'] / basedir).resolve()
    else:
        label.basedir = data['parent_path'].resolve()

    # Parse list of source files
    if 'sources' not in data or not isinstance(data['sources'], list):
        raise ValueError("Missing or invalid entry 'sources' in label file. A list of C source files with paths absolute or relative to the given basedir is required.")
    label.source_files = []
    for source in data['sources']:
        source_path = Path(source)
        if source_path.is_absolute():
            resolved_source_path = source_path.resolve()
        else:
            resolved_source_path = (label.basedir / source_path).resolve()
        if (not resolved_source_path.exists() or not resolved_source_path.is_file()) and not "%" in source:
            raise ValueError("Missing or invalid source file '%s' given." % (source))
        label.source_files.append(source_path)

    # Parse list of directories to include headers from
    if 'headers' in data:
        if not isinstance(data['headers'], list):
            raise ValueError("Invalid entry 'headers' in label file. Header directories have to be provided as a list of paths absolute or relative to the given basedir.")
        for header in data['headers']:
            header_path = Path(header)
            if header_path.is_absolute():
                resolved_header_path = header_path.resolve()
            else:
                resolved_header_path = (label.basedir / header_path).resolve()
            if (not resolved_header_path.exists() or not resolved_header_path.is_dir()) and not "%" in header:
                raise ValueError("Missing or invalid header directory '%s' (resolved to '%s') given." % (header, resolved_header_path))
            label.header_dirs.append(header_path)
        
    # Parse list of already-built objects to link against
    if 'objects' in data:
        if not isinstance(data['objects'], list):
            raise ValueError("Invalid entry 'objects' in label file. Precompiled object files have to be provided as a list of paths absolute or relative to the given basedir.")
        for object in data['objects']:
            object_path = Path(object)
            if object_path.is_absolute():
                resolved_object_path = object_path.resolve()
            else:
                resolved_object_path = (label.basedir / object_path).resolve()
            if not resolved_object_path.exists() or not resolved_object_path.is_dir():
                raise ValueError("Missing or invalid precompiled object file '%s' given." % object)
            label.object_files.append(object_path)

    # Parse list of additional compiler flags
    if 'flags' in data:
        if not isinstance(data['flags'], list):
            raise ValueError("Invalid entry 'flags' in label file. Additional compiler flags have to be provided as a list of strings.")
        for flag in data['flags']:
            label.additional_flags.append(flag)
    
    # Parse name of function to check
    if not 'function' in data or not isinstance(data['function'], str):
        raise ValueError("Missing or invalid entry 'function' in label file. The name of the function to be tested is required.")
    label.function_name = data['function']

    # Parse argument list or preparation function
    if not 'arguments' in data or data['arguments'] is None:
        if not 'preparation' in data or not isinstance(data['preparation'], dict):
            raise ValueError("Missing or invalid entry 'arguments' or 'preparation' in label file. At least one must be specified.")
        preparation = data['preparation']
        if not "size" in preparation or not isinstance(preparation['size'], int):
            raise ValueError("Missing or invalid entry 'size' in preparation function specification.")
        if not "function" in preparation or not isinstance(preparation['function'], str):
            raise ValueError("Missing or invalid entry 'size' in preparation function specification.")
        
        label.arguments = None
        label.preparation = PreparationLabel(preparation['size'], preparation['function'])
    else:    
        if not isinstance(data['arguments'], list):
            raise ValueError("Invalid entry 'arguments' in label file. The arguments of the function to be tested are required if no input preparation function is specified.")
        for argument in data['arguments']:
            label.arguments.append(parseArgument(argument))

    # Successfully parsed label, so return it
    return label


