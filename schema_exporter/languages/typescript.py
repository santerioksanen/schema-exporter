from enum import Enum, EnumMeta
from typing import Any, Dict, List

from schema_exporter.types import (
    EnumInfo,
    Mapping,
    ParsedField,
    ParsedSchema,
    PythonDatatypes,
)

from .base_language import BaseLanguage


class Types(Enum):
    BOOL = Mapping(mapping="boolean")
    NUMBER = Mapping(mapping="number")
    STRING = Mapping(mapping="string")
    DATE = Mapping(mapping="Date")
    OBJECT = Mapping(mapping="object")
    ANY = Mapping(mapping="any")


type_mappings: Dict[PythonDatatypes, Mapping] = {
    PythonDatatypes.ANY: Types.ANY.value,
    PythonDatatypes.BOOL: Types.BOOL.value,
    PythonDatatypes.CONSTANT: Types.STRING.value,
    PythonDatatypes.DATETIME: Types.STRING.value,
    PythonDatatypes.DATE: Types.STRING.value,
    PythonDatatypes.TIME: Types.STRING.value,
    PythonDatatypes.DECIMAL: Types.NUMBER.value,
    PythonDatatypes.DICT: Types.OBJECT.value,
    PythonDatatypes.EMAIL: Types.STRING.value,
    PythonDatatypes.FIELD: Types.ANY.value,
    PythonDatatypes.FLOAT: Types.NUMBER.value,
    PythonDatatypes.FUNCTION: Types.ANY.value,
    PythonDatatypes.INT: Types.NUMBER.value,
    PythonDatatypes.MAPPING: Types.ANY.value,
    PythonDatatypes.METHOD: Types.ANY.value,
    PythonDatatypes.STRING: Types.STRING.value,
    PythonDatatypes.TIMEDELTA: Types.NUMBER.value,
    PythonDatatypes.URL: Types.STRING.value,
    PythonDatatypes.UUID: Types.STRING.value,
    PythonDatatypes.IP_ADDRESS: Types.STRING.value,
    PythonDatatypes.IP_INTERFACE: Types.STRING.value,
    PythonDatatypes.IPv4_ADDRESS: Types.STRING.value,
    PythonDatatypes.IPv4_INTERFACE: Types.STRING.value,
    PythonDatatypes.IPv6_ADDRESS: Types.STRING.value,
    PythonDatatypes.IPv6_INTERFACE: Types.STRING.value,
    PythonDatatypes.JSON_FIELD: Types.OBJECT.value,
}


class Typescript(BaseLanguage):
    @property
    def type_mappings(self) -> Dict[PythonDatatypes, Mapping]:
        return type_mappings

    @staticmethod
    def get_default_kwargs() -> Dict[str, Any]:
        return dict()

    @staticmethod
    def _format_enum_field(field_name: str, value: Enum) -> str:
        val = value.value
        if not isinstance(val, int):
            val = f'"{val}"'

        return f"  {field_name} = {val},"

    @staticmethod
    def _format_enum(e: EnumMeta, enum_fields: List[str], enum_info: EnumInfo) -> str:
        enum_fields_formatted = "\n".join(enum_fields)
        return f"export enum {e.__name__} {{\n{enum_fields_formatted}\n}}\n"

    def format_header(self, include_dump_only: bool, include_load_only: bool) -> str:
        return ""

    def _format_schema_field(
        self,
        field: ParsedField,
    ) -> str:
        export_type = self.map_schema_field(field)
        field_name = field.field_name
        readonly = ""

        if isinstance(export_type, Mapping):
            export_type = export_type.mapping

        if field.many:
            export_type += "[]"

        if field.allow_none:
            export_type += " | null"

        if not field.required:
            field_name += "?"

        if field.dump_only:
            readonly = "readonly "

        return f"  {readonly}{field_name}: {export_type}"

    def _format_schema(
        self, schema: ParsedSchema, schema_fields: List[ParsedField]
    ) -> str:
        schema_fields_formatted = "\n".join(
            [self._format_schema_field(fld) for fld in schema_fields]
        )
        return f"export interface {schema.name} {{\n{schema_fields_formatted}\n}}\n"
