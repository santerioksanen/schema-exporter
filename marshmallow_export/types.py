import dataclasses
import uuid
from dataclasses import dataclass

from enum import Enum, auto

from typing import Optional, Union, List, Dict, Set, Any


class PythonDatatypes(Enum):
    BOOL = auto()
    CONSTANT = auto()
    STRING = auto()
    DATETIME = auto()
    DECIMAL = auto()
    DICT = auto()
    EMAIL = auto()
    FIELD = auto()
    FLOAT = auto()
    FUNCTION = auto()
    INT = auto()
    MAPPING = auto()
    METHOD = auto()
    NUMBER = auto()
    RAW = auto()
    TIMEDELTA = auto()
    URL = auto()
    UUID = auto()


@dataclass
class Mapping:
    mapping: str
    imports: Optional[
        Union[
            List[str],
            Dict[str, List[str]]
        ]
    ] = None


@dataclass
class ParsedField:
    python_datatype: PythonDatatypes | None # Set to none if a reference to other
    export_name: str | None                 # Set name to reference
    field_name: str
    required: bool = False
    allow_none: bool = False
    many: bool = False
    dump_only: bool = False
    load_only: bool = False


@dataclass
class ParsedSchema:
    name: str
    fields: list[ParsedField]
    nests: Set['ParsedSchema'] = dataclasses.field(default_factory=set)
    nested_by: Set['ParsedSchema'] = dataclasses.field(default_factory=set)
    ordering: int = 0
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)
    _uuid: uuid = uuid.uuid4()

    def __hash__(self):
        return hash(self._uuid)


@dataclass
class SchemaInfo:
    nests: Set['ParsedSchema'] = dataclasses.field(default_factory=set)         # TODO: Remove me
    nested_by: Set['ParsedSchema'] = dataclasses.field(default_factory=set)     # TODO: Remove me
    ordering: int = 0                                                           # TODO: Remove me
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)


@dataclass
class EnumInfo:
    kwargs: Dict[str, Any] = dataclasses.field(default_factory=dict)
