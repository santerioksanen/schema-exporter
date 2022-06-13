from enum import Enum

from marshmallow import Schema, fields

from marshmallow_export import type_mappings

from ._abstract import AbstractLanguage
from marshmallow_export.types import Mapping

from typing import Dict, Tuple


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

    name = 'Typescript'

    @staticmethod
    def _export_enum(enum: Enum) -> str:
        pass

    def _export_header(self, namespace: str) -> str:
        return ''

    def _export_field(
        self,
        field_name: str,
        ma_field: fields.Field,
        strip_schema_keyword: bool
    ) -> Tuple[str, str]:

        many = False
        ts_type = None
        if isinstance(ma_field, fields.Nested):
            ts_type = self._get_schema_export_name(ma_field.nested, strip_schema_keyword)
            if ma_field.many:
                many = True
        
        elif isinstance(ma_field, fields.List):
            many = True
            if isinstance(ma_field.inner, fields.Nested):
                ts_type = self._get_schema_export_name(ma_field.inner.nested, strip_schema_keyword)
            else:
                ma_field = ma_field.inner
        
        if ts_type is None:
            if not ma_field.__class__ in type_mappings:
                raise NotImplementedError(f'{ma_field} not implemented for {self.name}')
            
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
        strip_schema_keyword: bool,
        include_dump_only: bool,
        include_load_only: bool
    ) -> str:

        schema_name = self._get_schema_export_name(schema, strip_schema_keyword)
        ts_fields = list()

        for field_name, ma_field in schema._declared_fields.items():
            if not include_dump_only and ma_field.dump_only:
                continue

            if not include_load_only and ma_field.load_only:
                continue

            field_name, ts_type = self._export_field(
                field_name,
                ma_field,
                strip_schema_keyword
            )

            ts_fields.append(
                f'  {field_name}: {ts_type};'
            )

        ts_fields = '\n'.join(ts_fields)
        return f'export interface {schema_name} {{\n{ts_fields}\n}};\n'
