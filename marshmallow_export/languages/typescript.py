from enum import Enum, EnumMeta

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from .abstract import AbstractLanguage
from marshmallow_export.types import Mapping, EnumInfo

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
