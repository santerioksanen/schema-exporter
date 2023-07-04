from enum import Enum
from types import NoneType, UnionType
from typing import (
    Any,
    Dict,
    List,
    Set,
    Tuple,
    Type,
    Union,
    get_args,
    get_origin,
    get_type_hints,
)

from rest_framework import serializers

from schema_exporter.parsers.drf_mappings import drf_mappings
from schema_exporter.types import ParsedField, ParsedSchema, PythonDatatypes

from .base_parser import BaseParser
from .django_mappings import django_mappings
from .python_native_mappings import python_native_mappings


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

    @staticmethod
    def _parse_primary_key_related_field(
        drf_field: serializers.PrimaryKeyRelatedField,
    ) -> PythonDatatypes:
        serializer = drf_field.parent
        django_model = None
        if hasattr(serializer, "Meta") and hasattr(serializer.Meta, "model"):
            django_model = serializer.Meta.model

        if django_model is None:
            # Fallback python datatype
            return PythonDatatypes.INT

        if drf_field.field_name is None:
            return PythonDatatypes.INT

        forward_django_field = getattr(django_model, drf_field.field_name, None)
        if forward_django_field is None:
            return PythonDatatypes.INT

        django_field = getattr(forward_django_field, "field", None)
        if django_field is None:
            return PythonDatatypes.INT

        related_model = getattr(django_field, "model", None)
        related_field_names = getattr(django_field, "to_fields", [])
        if related_model is None or len(related_field_names) == 0:
            return PythonDatatypes.INT

        remote_field = getattr(django_field, "remote_field", None)
        if remote_field is None:
            return PythonDatatypes.INT

        remote_model = getattr(remote_field, "model", None)
        if remote_model is None:
            return PythonDatatypes.INT

        deferred_related_field = getattr(remote_model, related_field_names[0], None)
        if deferred_related_field is None:
            return PythonDatatypes.INT

        related_field = getattr(deferred_related_field, "field")
        if related_field.__class__ not in django_mappings:
            return PythonDatatypes.INT

        return django_mappings[related_field.__class__]

    @staticmethod
    def _parse_readonly_field(
        drf_field: serializers.ReadOnlyField,
    ) -> Tuple[bool, PythonDatatypes]:
        serializer = drf_field.parent
        if not isinstance(serializer, serializers.ModelSerializer):
            print(
                "Warning, trying to parse readonly field from non ModelSerializer. Fallback to any."
            )
            return False, PythonDatatypes.ANY

        django_model = serializer.Meta.model

        if drf_field.field_name is None:
            return False, PythonDatatypes.ANY

        django_method = getattr(django_model, drf_field.field_name, None)
        if django_method is None:
            return False, PythonDatatypes.ANY

        django_method_getter = getattr(django_method, "fget", None)

        if django_method_getter is None:
            return False, PythonDatatypes.ANY

        type_hints = get_type_hints(django_method_getter)
        if "return" not in type_hints:
            return False, PythonDatatypes.ANY

        type_hint = type_hints["return"]

        if type_hint in python_native_mappings:
            return False, python_native_mappings[type_hint]

        if get_origin(type_hint) is UnionType:
            type_args = list(get_args(type_hint))
            if len(type_args) != 2 or NoneType not in type_args:
                return False, PythonDatatypes.ANY

            type_args.remove(NoneType)

            if type_args[0] in python_native_mappings:
                return True, python_native_mappings[type_args[0]]

        return False, PythonDatatypes.ANY

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

        allow_none = drf_field.allow_null

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

        elif isinstance(drf_field, serializers.PrimaryKeyRelatedField):
            python_datatype = self._parse_primary_key_related_field(drf_field)

        elif isinstance(drf_field, serializers.ReadOnlyField):
            allow_none, python_datatype = self._parse_readonly_field(drf_field)

        # TODO: Add parsers for choice field, enum fields
        elif issubclass(drf_field.__class__, serializers.Field):
            if drf_field.__class__ not in drf_mappings:
                print(
                    f"Warning: Parser for {drf_field.__class__} not implemented, falling back to any"
                )
                python_datatype = PythonDatatypes.ANY
            else:
                python_datatype = drf_mappings[drf_field.__class__]

        return (
            ParsedField(
                python_datatype=python_datatype,
                export_name=export_name,
                field_name=field_name,
                required=drf_field.required,
                allow_none=allow_none,
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
