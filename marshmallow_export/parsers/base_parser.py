from abc import ABC, abstractmethod
from enum import Enum
from typing import Type, TypeVar, Generic

from marshmallow_export.types import EnumInfo, ParsedField, ParsedSchema

S, F = TypeVar("T"), TypeVar("F")


class BaseParser(ABC, Generic[S, F]):
    def __init__(
        self, default_info_kwargs: dict[str, any], strip_schema_from_name: bool = True
    ):
        self.strip_schema_from_name = strip_schema_from_name
        self.schemas: dict[str, ParsedSchema] = dict()
        self.schema_nests: dict[ParsedSchema, set[str]] = dict()
        self.enums: dict[Type[Enum], EnumInfo] = dict()
        self.schemas_to_parse: set[Type[S]] = set()
        self.default_info_kwargs = default_info_kwargs

    @abstractmethod
    def _get_schema_export_name(
        self,
        schema: Type[S],
    ):
        pass

    @abstractmethod
    def parse_field(
        self, field_name: str, field: Type[F]
    ) -> tuple[ParsedField, set[str]]:
        pass

    @abstractmethod
    def parse_and_add_schema(
        self, schema: S, schema_kwargs: dict[str, any] = None
    ) -> None:
        pass

    def add_enum(self, en: Type[Enum], info_kwargs: dict[str, any] = None) -> None:
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
