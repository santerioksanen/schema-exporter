from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Dict, Generic, Type, TypeVar

from marshmallow_export.types import EnumInfo, ParsedField, ParsedSchema

S = TypeVar("S")
F = TypeVar("F")


class BaseParser(ABC, Generic[S, F]):
    def __init__(
        self, default_info_kwargs: Dict[str, Any], strip_schema_from_name: bool = True
    ):
        self.strip_schema_from_name = strip_schema_from_name
        self.schemas: Dict[str, ParsedSchema] = dict()
        self.schema_nests: Dict[ParsedSchema, set[str]] = dict()
        self.enums: Dict[Type[Enum], EnumInfo] = dict()
        self.schemas_to_parse: set[S] = set()
        self.default_info_kwargs = default_info_kwargs

    @abstractmethod
    def _get_schema_export_name(
        self,
        schema: S,
    ):
        pass

    @abstractmethod
    def parse_field(self, field_name: str, field: F) -> tuple[ParsedField, set[str]]:
        pass

    @abstractmethod
    def parse_and_add_schema(
        self, schema: S, schema_kwargs: Dict[str, Any] | None = None
    ) -> None:
        pass

    def add_enum(
        self, en: Type[Enum], info_kwargs: Dict[str, Any] | None = None
    ) -> None:
        if info_kwargs is None:
            info_kwargs = self.default_info_kwargs

        self.enums[en] = EnumInfo(kwargs=info_kwargs)

    def parse_nested(self):
        while len(self.schemas_to_parse):
            schema = self.schemas_to_parse.pop()
            self.parse_and_add_schema(schema)

        # Add nests to parsed schema details
        for parsed_schema, nested_schema_names in self.schema_nests.items():
            for nested_schema_name in nested_schema_names:
                parsed_schema.nests.add(self.schemas[nested_schema_name])
