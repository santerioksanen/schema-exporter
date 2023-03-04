from enum import Enum
from typing import Type

from rest_framework import serializers

from marshmallow_export.parsers.drf_mappings import drf_mappings
from marshmallow_export.types import EnumInfo, ParsedField, ParsedSchema


class DRFParser:
    def __init__(
        self, default_info_kwargs: dict[str, any], strip_schema_from_name: bool = True
    ):
        self.strip_schema_from_name = strip_schema_from_name
        self.schemas: dict[str, ParsedSchema] = dict()
        self.serializer_nests: dict[ParsedSchema, set[str]] = dict()
        self.enums: dict[Type[Enum], EnumInfo] = dict()
        self.serializers_to_parse: set[Type[serializers.Serializer]] = set()
        self.default_info_kwargs = default_info_kwargs

    def _get_serializer_export_name(
        self,
        serializer: Type[serializers.Serializer],
    ):
        name = serializer.__name__
        if self.strip_schema_from_name:
            name = name.replace("Serializer", "")

        return name

    def parse_field(
        self, field_name: str, field: Type[serializers.Field]
    ) -> tuple[ParsedField, set[str]]:
        drf_field = field
        many = False
        python_datatype = None
        export_name = None
        nested_serializers = set()

        if isinstance(drf_field, serializers.ListField):
            drf_field = drf_field.child
            many = True

        if issubclass(drf_field, serializers.Serializer):
            self.serializers_to_parse.add(drf_field)
            export_name = self._get_serializer_export_name(drf_field)
            nested_serializers.add(export_name)

        # TODO: Add parsers for choice field, enum fields
        elif issubclass(drf_field.__class__, serializers.Field):
            if drf_field.__class__ not in drf_mappings:
                raise NotImplementedError(
                    f"Parser for {drf_field.__class__} not implemented"
                )
            python_datatype = drf_mappings[drf_field.__class__]

        return (
            ParsedField(
                python_datatype=python_datatype,
                export_name=export_name,
                field_name=field_name,
                required=drf_field.required,
                allow_none=drf_field.allow_null,
                many=many,
                dump_only=drf_field.read_only,
                load_only=drf_field.write_only,
            ),
            nested_serializers,
        )

    def parse_and_add_serializer(
        self, 
        serializer: serializers.Serializer,
        schema_kwargs: dict[str, any] = None
    ) -> None:
        if schema_kwargs is None:
            schema_kwargs = self.default_info_kwargs

        name = self._get_serializer_export_name(serializer)
        if name in self.schemas:
            return

        nested_schemas = set()
        fields: list[ParsedField] = []
        for field_name, field in serializer.fields.items():
            parsed_field, _nested_serializers = self.parse_field(field_name, field)
            nested_schemas.update(_nested_serializers)
            fields.append(parsed_field)

        parsed_schema = ParsedSchema(name=name, fields=fields, kwargs=schema_kwargs)
        self.serializer_nests[parsed_schema] = nested_schemas
        self.schemas[name] = parsed_schema

    def add_enum(self, en: Type[Enum], info_kwargs: dict[str, any] = None) -> None:
        if info_kwargs is None:
            info_kwargs = self.default_info_kwargs

        self.enums[en] = EnumInfo(kwargs=info_kwargs)

    def parse_nested(self):
        while len(self.serializers_to_parse):
            serializer = self.serializers_to_parse.pop()
            self.parse_and_add_serializer(serializer)

        # Add nests to parsed schema details
        for parsed_schema, nested_schema_names in self.serializer_nests.items():
            for nested_schema_name in nested_schema_names:
                parsed_schema.nests.add(self.schemas[nested_schema_name])
