from abc import ABCMeta
from abc import abstractmethod

from dataclasses import dataclass
from email.policy import default

from marshmallow import fields
from marshmallow import Schema

from marshmallow_enum import EnumField

from enum import Enum
from typing import Tuple
from typing import Dict
from typing import List
from typing import Set
from typing import Optional
from typing import Union


@dataclass
class Mapping:
    mapping: str
    includes: Optional[
        Union[
            List[str],
            Dict[str, List[str]]
        ]
    ]


class AbstractLanguage(metaclass = ABCMeta):

    def __init__(
        self,
        schemas: Dict[str, Set[Schema]],
        enums: Dict[str, Set[Enum]],
        expand_nested: bool
    ) -> None:

        self.schemas = schemas
        self.enums = enums

        if expand_nested:
            self._expand_nested()

    def _expand_nested(self):
        for namespace, schema_list in self.schemas.items():
            schemas_to_add = set()
            enums_to_add = set()
            for schema in schema_list:
                for field in schema._declared_fields.values():
                    if isinstance(field, fields.Nested):
                        schemas_to_add.add(field.nested)
                    elif isinstance(field, fields.List):
                        if isinstance(field.inner, fields.Nested):
                            schemas_to_add.add(field.inner.nested)
                        elif isinstance(field.inner, EnumField):
                            enums_to_add.add(field.inner.enum)
                    elif isinstance(field, EnumField):
                        enums_to_add.add(field.enum)
            
            self.schemas[namespace] = self.schemas[namespace].union(schemas_to_add)
            if not namespace in self.enums:
                self.enums[namespace] = set()
            
            self.enums[namespace] = self.enums[namespace].union(enums_to_add)

    @staticmethod
    def _get_schema_export_name(
        schema: Schema,
        strip_schema_keyword: bool
    ) -> str:
        name = schema.__name__

        if strip_schema_keyword:
            name = name.replace('Schema', '')
        
        return name
    
    @staticmethod
    @property
    @abstractmethod
    def _mappings() -> Dict[fields.Field, Mapping]:
        pass

    @abstractmethod
    def _export_field(
        self,
        ma_field: fields.Field,
        strip_schema_keyword: bool
    ) -> Tuple[str, str]:
        pass
    
    @staticmethod
    @abstractmethod 
    def _export_schema(
        schema: Schema,
        strip_schema_keyword: bool,
        include_dump_only: bool,
        include_load_only: bool
    ) -> str:
        pass

    @staticmethod
    @abstractmethod
    def _export_enum(enum: Enum):
        pass

    def export_namespaces(
        self,
        namespaces: List[str],
        strip_schema_keyword: bool,
        include_dump_only: bool,
        include_load_only: bool
    ) -> str:
        pass
