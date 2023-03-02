from enum import Enum, EnumMeta

from marshmallow import Schema, fields

from .abstract import AbstractLanguage
from marshmallow_export.types import Mapping, EnumInfo, ParsedSchema, PythonDatatypes, ParsedField

from typing import List, Dict, Any


class Types(Enum):
    BOOL = Mapping(mapping='boolean')
    NUMBER = Mapping(mapping='number')
    STRING = Mapping(mapping='string')
    DATE = Mapping(mapping='Date')
    OBJECT = Mapping(mapping='object')
    ANY = Mapping(mapping='any')


type_mappings: dict[PythonDatatypes, Mapping] = {
    PythonDatatypes.BOOL: Types.BOOL.value,
    PythonDatatypes.CONSTANT: Types.STRING.value,
    PythonDatatypes.DATETIME: Types.DATE.value,
    PythonDatatypes.DECIMAL: Types.NUMBER.value,
    PythonDatatypes.DICT: Types.OBJECT.value,
    PythonDatatypes.EMAIL: Types.STRING.value,
    PythonDatatypes.FIELD: Types.ANY.value,
    PythonDatatypes.FLOAT: Types.NUMBER.value,
    PythonDatatypes.FUNCTION: Types.ANY.value,
    PythonDatatypes.INT: Types.NUMBER.value,
    PythonDatatypes.MAPPING: Types.ANY.value,
    PythonDatatypes.METHOD: Types.ANY.value,
    PythonDatatypes.NUMBER: Types.NUMBER.value,
    PythonDatatypes.RAW: Types.ANY.value,
    PythonDatatypes.STRING: Types.STRING.value,
    PythonDatatypes.TIMEDELTA: Types.ANY.value,
    PythonDatatypes.URL: Types.STRING.value,
    PythonDatatypes.UUID: Types.STRING.value,
}


class Typescript(AbstractLanguage):

    @property
    def type_mappings(self) -> Dict[PythonDatatypes, Mapping]:
        return type_mappings

    @staticmethod
    def get_default_kwargs() -> Dict[str, Any]:
        return dict()

    @staticmethod
    def _format_enum_field(field_name: str, value: Enum) -> str:
        value = value.value
        if not isinstance(value, int):
            value = f'"{value}"'

        return f'  {field_name} = {value},'

    @staticmethod
    def _format_enum(e: EnumMeta, enum_fields: List[str], enum_info: EnumInfo) -> str:
        enum_fields = '\n'.join(enum_fields)
        return f'export enum {e.__name__} {{\n{enum_fields}\n}}\n'

    def format_header(
            self,
            include_dump_only: bool,
            include_load_only: bool
    ) -> str:
        return ''

    def _format_schema_field(
            self,
            field: ParsedField,
    ) -> str:
        export_type = self.map_schema_field(field)
        field_name = field.field_name
        
        if isinstance(export_type, Mapping):
            export_type = export_type.mapping

        if field.many:
            export_type += '[]'

        if field.allow_none:
            export_type += ' | null'

        if not field.required:
            field_name += '?'

        return f'  {field_name}: {export_type};'

    def _format_schema(
            self,
            schema: ParsedSchema,
            schema_fields: List[str]
    ) -> str:
        schema_fields = '\n'.join(schema_fields)
        return f'export interface {schema.name} {{\n{schema_fields}\n}}\n'
