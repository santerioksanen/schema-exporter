from enum import Enum, EnumMeta

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from .abstract import AbstractLanguage
from marshmallow_export.types import Mapping, EnumInfo, SchemaInfo

from typing import Tuple, Dict, Any, List


DEFAULT_ENUM_DERIVES = [
    Mapping(mapping='Debug'),
    Mapping(mapping='Clone'),
    Mapping(mapping='Copy'),
    Mapping(mapping='Serialize', imports={'serde': ['Serialize']}),
    Mapping(mapping='Deserialize', imports={'serde': ['Deserialize']}),
    Mapping(mapping='EnumString', imports={'strum_macros': ['EnumString']}),
]


DEFAULT_SCHEMA_DERIVES = [
    Mapping(mapping='Debug'),
    Mapping(mapping='Clone'),
    Mapping(mapping='Copy'),
    Mapping(mapping='Serialize', imports={'serde': ['Serialize']}),
    Mapping(mapping='Deserialize', imports={'serde': ['Deserialize']}),
]


class Types(Enum):
    BOOL = Mapping(mapping='bool')
    INTEGER = Mapping(mapping='i64')
    FLOAT = Mapping(mapping='f64')
    DECIMAL = Mapping(mapping='Decimal', imports={'rust_decimal': ['Decimal']})
    STRING = Mapping(mapping='String')
    DATE_TIME_AWARE = Mapping(mapping='DateTime<Utc>', imports={'chrono': ['DateTime', 'Utc']})
    UUID = Mapping(mapping='UUID', imports={'uuid': ['UUID']})


type_mappings = {
    fields.Bool: Types.BOOL.value,
    fields.Boolean: Types.BOOL.value,
    fields.Constant: Types.STRING.value,
    fields.DateTime: Types.DATE_TIME_AWARE.value,
    fields.Decimal: Types.DECIMAL.value,
    fields.Dict: None,
    fields.Email: Types.STRING.value,
    fields.Field: None,
    fields.Float: Types.FLOAT.value,
    fields.Function: None,
    fields.Int: Types.INTEGER.value,
    fields.Integer: Types.INTEGER.value,
    fields.Mapping: None,
    fields.Method: None,
    fields.Number: Types.FLOAT.value,
    fields.Raw: None,
    fields.Str: Types.STRING.value,
    fields.String: Types.STRING.value,
    fields.TimeDelta: None,
    fields.Url: Types.STRING.value,
    fields.UUID: Types.STRING.value,
}


class Rust(AbstractLanguage):

    @property
    def type_mappings(self) -> Dict[fields.Field, Enum]:
        return type_mappings

    @staticmethod
    def get_default_kwargs() -> Dict[str, Any]:
        return {
            'rust_enum_derives': DEFAULT_ENUM_DERIVES,
            'rust_schema_derives': DEFAULT_SCHEMA_DERIVES,
        }

    @staticmethod
    def _format_enum_field(field_name: str, value: Enum) -> str:
        return f'    {field_name},'

    @staticmethod
    def _format_enum(e: EnumMeta, enum_fields: List[str], enum_info: EnumInfo) -> str:
        enum_fields = '\n'.join(enum_fields)
        derives = ''
        if 'rust_enum_derives' in enum_info.kwargs and len(enum_info.kwargs['rust_enum_derives']) > 0:
            derives = f'#[derive({", ".join([m.mapping for m in enum_info.kwargs["rust_enum_derives"]])})]\n'

        return f'{derives}pub enum {e.__name__} {{\n{enum_fields}\n}}\n'

    def format_header(self, namespace: str) -> str:
        return ''

    def _format_schema_field(
            self,
            field_name: str,
            ma_field: fields.Field
    ) -> str:
        export_type, many = self.map_schema_field(ma_field)

        if many:
            export_type = f'Vec<{export_type}>'
        
        if ma_field.allow_none or not ma_field.required:
            export_type = f'Option<{export_type}>'
        
        return f'    pub {field_name}: {export_type},'

    def _format_schema(
            self,
            schema: Schema,
            schema_info: SchemaInfo,
            schema_fields: List[str]
    ) -> str:
        schema_name = self.get_schema_export_name(schema)
        schema_fields = '\n'.join(schema_fields)
        derives = ''

        if 'rust_schema_derives' in schema_info.kwargs and len(schema_info.kwargs['rust_schema_derives']) > 0:
            derives = f'#[derive({", ".join([m.mapping for m in schema_info.kwargs["rust_schema_derives"]])})]\n'

        return f'{derives}pub struct {schema_name} {{\n{schema_fields}\n}}\n'

