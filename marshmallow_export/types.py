import dataclasses
from dataclasses import dataclass

from marshmallow import Schema

from typing import Optional, Union, List, Dict, Set


@dataclass
class Mapping:
    mapping: str
    includes: Optional[
        Union[
            List[str],
            Dict[str, List[str]]
        ]
    ] = None


@dataclass
class SchemaInfo:
    nests: Set[Schema] = dataclasses.field(default_factory=set)
    nested_by: Set[Schema] = dataclasses.field(default_factory=set)
    ordering: int = 0
