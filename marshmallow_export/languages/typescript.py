from enum import Enum, EnumMeta

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from .abstract import AbstractLanguage
from marshmallow_export.types import Mapping, EnumInfo, SchemaInfo

from typing import Tuple, List, Dict, Any


class Types(Enum):
    BOOL = Mapping(mapping='boolean')
    NUMBER = Mapping(mapping='number')
    STRING = Mapping(mapping='string')
    DATE = Mapping(mapping='Date')
    OBJECT = Mapping(mapping='object')
    ANY = Mapping(mapping='any')


type_mappings = {
    fields.Bool: Types.BOOL.value,
    fields.Boolean: Types.BOOL.value,
    fields.Constant: Types.STRING.value,
    fields.DateTime: Types.DATE.value,
    fields.Decimal: Types.NUMBER.value,
    fields.Dict: Types.OBJECT.value,
    fields.Email: Types.STRING.value,
    fields.Field: Types.ANY.value,
    fields.Float: Types.NUMBER.value,
    fields.Function: Types.ANY.value,
    fields.Int: Types.NUMBER.value,
    fields.Integer: Types.NUMBER.value,
    fields.Mapping: Types.ANY.value,
    fields.Method: Types.ANY.value,
    fields.Number: Types.NUMBER.value,
    fields.Raw: Types.ANY.value,
    fields.Str: Types.STRING.value,
    fields.String: Types.STRING.value,
    fields.TimeDelta: Types.ANY.value,
    fields.Url: Types.STRING.value,
    fields.UUID: Types.STRING.value,
}


class Typescript(AbstractLanguage):

    @property
    def type_mappings(self) -> Dict[fields.Field, Enum]:
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

    def format_header(self, namespace: str) -> str:
        return ''
    
    def _format_schema_field(
            self,
            field_name: str,
            ma_field: fields.Field
    ) -> str:
        export_type, many = self.map_schema_field(ma_field)

        if many:
            export_type += '[]'
        
        if ma_field.allow_none:
            export_type += ' | null'
        
        if not ma_field.required:
            field_name += '?'
        
        return f'  {field_name}: {export_type};'

    def _format_schema(
            self,
            schema: Schema,
            schema_info: SchemaInfo,
            schema_fields: List[str]
    ) -> str:
        schema_name = self.get_schema_export_name(schema)
        schema_fields = '\n'.join(schema_fields)
        return f'export interface {schema_name} {{\n{schema_fields}\n}}\n'

