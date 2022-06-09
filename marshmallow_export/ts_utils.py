from marshmallow import Schema
from marshmallow import fields

from .type_mappings import type_mappings
from .type_mappings import Languages

from .type_mappings import NOT_IMPLEMENTED_TYPE
from .type_mappings import TsTypes


def _get_ts_type(
        name: str,
        ma_field,
        strip_schema_keyword: bool
) -> (str, str):
    if isinstance(ma_field, fields.Nested):
        ts_type = ma_field.nested.__name__

        if strip_schema_keyword:
            ts_type = ts_type.replace('Schema', '')

        if ma_field.many:
            ts_type += '[]'

    else:
        ts_type = type_mappings[ma_field.__class__][Languages.TS]

    if ts_type == NOT_IMPLEMENTED_TYPE:
        raise NotImplementedError(f'Type: {ts_type} not implemented for Typescript')

    if isinstance(ts_type, TsTypes):
        ts_type = ts_type.value

    if ma_field.allow_none:
        ts_type += ' | null'

    if not ma_field.required:
        name += '?'

    return name, ts_type


def _get_ts_mapping(
        schema: Schema.__class__,
        strip_schema_keyword: bool,
        include_dump_only: bool,
        include_load_only: bool,
):

    schma_name = schema.__name__

    if strip_schema_keyword:
        schma_name = schma_name.replace('Schema', '')

    ts_fields = []

    for field_name, ma_field in schema._declared_fields.items():
        if not include_dump_only and ma_field.dump_only:
            continue

        if not include_load_only and ma_field.load_only:
            continue

        field_name, ts_type = _get_ts_type(field_name, ma_field, strip_schema_keyword)

        ts_fields.append(
            f'  {field_name}: {ts_type};'
        )

    ts_fields = '\n'.join(ts_fields)
    return f'export interface {schma_name} {{\n{ts_fields}\n}};\n'
