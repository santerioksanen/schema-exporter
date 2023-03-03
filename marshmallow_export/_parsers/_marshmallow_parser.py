from enum import Enum
from typing import Type

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from marshmallow_export._parsers._marshmallow_mappings import marshmallow_mappings
from marshmallow_export.types import EnumInfo, ParsedField, ParsedSchema


class _MarshmallowParser:
    def __init__(
        self, default_info_kwargs: dict[str, any], strip_schema_from_name: bool = True
    ):
        self.strip_schema_from_name = strip_schema_from_name
        self.schemas: dict[str, ParsedSchema] = dict()
        self.schema_nests: dict[str, set[str]] = dict()
        self.enums: dict[Type[Enum], EnumInfo] = dict()
        self.schemas_to_parse: set[Schema] = set()
        self.default_info_kwargs = default_info_kwargs

    def _get_schema_export_name(
        self,
        schema: Type[Schema],
    ):
        name = schema.__name__
        if self.strip_schema_from_name:
            name = name.replace("Schema", "")

        return name

    def parse_field(
        self, field_name: str, field: Type[fields.Field]
    ) -> tuple[ParsedField, set[str]]:
        ma_field = field
        many = False
        python_datatype = None
        export_name = None
        nested_schemas = set()

        if isinstance(ma_field, fields.List):
            ma_field = ma_field.inner
            many = True

        if isinstance(ma_field, fields.Nested):
            self.schemas_to_parse.add(ma_field.nested)
            export_name = self._get_schema_export_name(ma_field.nested)
            nested_schemas.add(export_name)
            if ma_field.many:
                many = True
        elif isinstance(ma_field, EnumField):
            export_name = ma_field.enum.__name__
            self.add_enum(ma_field.enum)
        elif issubclass(ma_field.__class__, fields.Field):
            if ma_field.__class__ not in marshmallow_mappings:
                raise NotImplementedError(
                    f"Parser for {ma_field.__class__} not implemented"
                )
            python_datatype = marshmallow_mappings[ma_field.__class__]

        return (
            ParsedField(
                python_datatype=python_datatype,
                export_name=export_name,
                field_name=field_name,
                required=ma_field.required,
                allow_none=ma_field.allow_none,
                many=many,
                dump_only=ma_field.dump_only,
                load_only=ma_field.load_only,
            ),
            nested_schemas,
        )

    def parse_and_add_schema(
        self, schema: Schema, schema_kwargs: dict[str, any] = None
    ) -> None:
        if schema_kwargs is None:
            schema_kwargs = self.default_info_kwargs

        name = self._get_schema_export_name(schema)
        if name in self.schemas:
            return

        nested_schemas = set()
        fields: list[ParsedField] = []
        for field_name, field in schema._declared_fields.items():
            parsed_field, _nested_schemas = self.parse_field(field_name, field)
            nested_schemas.update(_nested_schemas)
            fields.append(parsed_field)

        parsed_schema = ParsedSchema(name=name, fields=fields, kwargs=schema_kwargs)
        self.schema_nests[parsed_schema] = nested_schemas
        self.schemas[name] = parsed_schema

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
