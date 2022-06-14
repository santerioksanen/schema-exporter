from enum import Enum, EnumMeta

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from .abstract import AbstractLanguage
from marshmallow_export.types import Mapping, EnumInfo

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
        if 'rust_enum_derives' in enum_info.kwargs:
            derives = f'#[derive({", ".join([m.mapping for m in enum_info.kwargs["rust_enum_derives"]])})]\n'

        return f'{derives}pub enum {e.__name__} {{\n{enum_fields}\n}}\n'

    def _export_header(self, namespace: str) -> str:
        return ''

    def _export_field(
            self,
            field_name: str,
            ma_field: fields.Field
    ) -> Tuple[str, str]:

        many = False
        ts_type = None

        if isinstance(ma_field, fields.List):
            many = True
            ma_field = ma_field.inner

        if isinstance(ma_field, fields.Nested):
            ts_type = self.get_schema_export_name(ma_field.nested)
            if ma_field.many:
                many = True

        elif isinstance(ma_field, EnumField):
            ts_type = ma_field.enum.__name__

        elif isinstance(ma_field, fields.List):
            many = True
            if isinstance(ma_field.inner, fields.Nested):
                ts_type = self.get_schema_export_name(ma_field.inner.nested)
            else:
                ma_field = ma_field.inner

        if ts_type is None:
            if ma_field.__class__ not in type_mappings:
                raise NotImplementedError(f'{ma_field} not implemented for {self.__name__}')

            ts_type = type_mappings[ma_field.__class__]

        if isinstance(ts_type, Mapping):
            ts_type = ts_type.mapping

        if many:
            ts_type += '[]'

        if ma_field.allow_none:
            ts_type += ' | null'

        if not ma_field.required:
            field_name += '?'

        return field_name, ts_type

    def _export_schema(
            self,
            schema: Schema,
            include_dump_only: bool,
            include_load_only: bool
    ) -> str:

        schema_name = self.get_schema_export_name(schema)
        ts_fields = list()

        for field_name, ma_field in schema._declared_fields.items():
            if not include_dump_only and ma_field.dump_only:
                continue

            if not include_load_only and ma_field.load_only:
                continue

            field_name, ts_type = self._export_field(
                field_name,
                ma_field
            )

            ts_fields.append(
                f'  {field_name}: {ts_type};'
            )

        ts_fields = '\n'.join(ts_fields)
        return f'export interface {schema_name} {{\n{ts_fields}\n}}\n'
