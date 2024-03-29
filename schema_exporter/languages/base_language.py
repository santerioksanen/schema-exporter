from abc import ABCMeta, abstractmethod
from enum import Enum
from typing import Any, Dict, List, Tuple, Type, Union

from schema_exporter.types import (
    EnumInfo,
    Mapping,
    ParsedField,
    ParsedSchema,
    PythonDatatypes,
)


class BaseLanguage(metaclass=ABCMeta):
    def __init__(
        self,
        schemas: List[ParsedSchema],
        enums: List[Tuple[Type[Enum], EnumInfo]],
    ) -> None:
        self.schemas = schemas
        self.enums = enums

    @property
    @abstractmethod
    def type_mappings(self) -> Dict[PythonDatatypes, Mapping]:
        pass

    def map_schema_field(self, field: ParsedField) -> Union[str, Mapping]:
        if field.export_name is not None:
            return field.export_name

        if (
            field.python_datatype is not None
            and field.python_datatype in self.type_mappings
        ):
            return self.type_mappings[field.python_datatype]

        raise ValueError(
            f"Incompatible parsed field: {field}. Either export_name or python_datatype must be set"
        )

    @staticmethod
    @abstractmethod
    def get_default_kwargs() -> Dict[str, Any]:
        pass

    @staticmethod
    @abstractmethod
    def _format_enum_field(field_name: str, value: Enum) -> str:
        pass

    @staticmethod
    @abstractmethod
    def _format_enum(e: Type[Enum], enum_fields: List[str], enum_info: EnumInfo) -> str:
        pass

    def format_enum(self, e: Type[Enum], enum_info: EnumInfo) -> str:
        enum_fields = [
            self._format_enum_field(field_name, value)
            for field_name, value in e._member_map_.items()
        ]

        return self._format_enum(e, enum_fields, enum_info)

    @abstractmethod
    def _format_schema(
        self, schema: ParsedSchema, schema_fields: List[ParsedField]
    ) -> str:
        pass

    @abstractmethod
    def _format_schema_field(self, field: ParsedField) -> str:
        pass

    def format_schema(
        self, schema: ParsedSchema, include_dump_only: bool, include_load_only: bool
    ) -> str:
        schema_fields = list()

        for field in schema.fields:
            if not include_dump_only and field.dump_only:
                continue

            if not include_load_only and field.load_only:
                continue

            schema_fields.append(field)

        return self._format_schema(schema, schema_fields)

    @abstractmethod
    def format_header(self, include_dump_only: bool, include_load_only: bool) -> str:
        pass

    def export(self, include_dump_only: bool, include_load_only: bool) -> str:
        header = self.format_header(
            include_dump_only=include_dump_only, include_load_only=include_load_only
        )
        output = [header] if len(header) > 0 else list()
        output += [self.format_enum(e, enum_info) for e, enum_info in self.enums]
        output += [
            self.format_schema(
                schema=schema,
                include_dump_only=include_dump_only,
                include_load_only=include_load_only,
            )
            for schema in self.schemas
        ]

        return "\n".join(output)
