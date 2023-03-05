from enum import Enum
from typing import Any, Dict, List, Set, Tuple, Type, Union

from rest_framework import serializers

from marshmallow_export.parsers.drf_mappings import drf_mappings
from marshmallow_export.types import ParsedField, ParsedSchema

from .base_parser import BaseParser


def _to_pascal_case(s: str) -> str:
    return s.replace("_", " ").title().replace(" ", "")


def _create_enum_from_choices(
    field_name: str,
    field: Union[serializers.ChoiceField, serializers.MultipleChoiceField],
) -> Tuple[Type[Enum], bool]:
    choices = {}
    many = False
    if isinstance(field, serializers.MultipleChoiceField):
        many = True

    if isinstance(field.choices, dict):
        choices.update(field.choices)

    return Enum(_to_pascal_case(field_name), choices), many  # type: ignore


class DRFParser(BaseParser[serializers.Serializer, serializers.Field]):
    def _get_schema_export_name(
        self,
        serializer: serializers.Serializer,
    ):
        name = serializer.__class__.__name__
        if self.strip_schema_from_name:
            name = name.replace("Serializer", "")

        return name

    def parse_field(
        self, field_name: str, field: serializers.Field
    ) -> Tuple[ParsedField, Set[str]]:
        drf_field = field
        many = False
        python_datatype = None
        export_name = None
        nested_serializers = set()

        if issubclass(drf_field.__class__, serializers.ListSerializer) or isinstance(
            drf_field, serializers.ListField
        ):
            drf_field = drf_field.child  # type: ignore[attr-defined]
            many = True

        if hasattr(drf_field, "many"):
            many = drf_field.many

        if issubclass(drf_field.__class__, serializers.Serializer):
            self.schemas_to_parse.add(drf_field)  # type: ignore
            export_name = self._get_schema_export_name(drf_field)  # type: ignore
            nested_serializers.add(export_name)

        elif isinstance(drf_field, serializers.ChoiceField):
            en, many = _create_enum_from_choices(field_name, drf_field)
            export_name = en.__name__
            self.add_enum(en)

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

    def parse_and_add_schema(
        self,
        serializer: serializers.Serializer,
        schema_kwargs: Union[Dict[str, Any], None] = None,
    ) -> None:
        if schema_kwargs is None:
            schema_kwargs = self.default_info_kwargs

        name = self._get_schema_export_name(serializer)
        if name in self.schemas:
            return

        nested_schemas = set()
        fields: List[ParsedField] = []
        for field_name, field in serializer.fields.items():
            parsed_field, _nested_serializers = self.parse_field(field_name, field)
            nested_schemas.update(_nested_serializers)
            fields.append(parsed_field)

        parsed_schema = ParsedSchema(name=name, fields=fields, kwargs=schema_kwargs)
        self.schema_nests[parsed_schema] = nested_schemas
        self.schemas[name] = parsed_schema
