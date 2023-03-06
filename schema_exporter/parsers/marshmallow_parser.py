from inspect import isclass
from typing import Any, Dict, List, Set, Tuple, Type, Union

from marshmallow import Schema, fields

from schema_exporter.parsers.marshmallow_mappings import marshmallow_mappings
from schema_exporter.types import ParsedField, ParsedSchema

from .base_parser import BaseParser

class_enum_field = None
class_marshamallow_enum_field = None
try:
    from marshmallow_enum import EnumField  # type: ignore

    class_enum_field = EnumField
except ImportError:
    pass
try:
    from marshmallow.fields import Enum as MarshmallowEnumField

    class_marshamallow_enum_field = MarshmallowEnumField
except ImportError:
    pass


class MarshmallowParser(BaseParser[Type[Schema], fields.Field]):
    def _get_schema_export_name(
        self,
        schema: Type[Schema],
    ):
        name = schema.__name__
        if self.strip_schema_from_name:
            name = name.replace("Schema", "")

        return name

    def parse_field(
        self, field_name: str, field: fields.Field
    ) -> Tuple[ParsedField, Set[str]]:
        ma_field = field
        many = False
        python_datatype = None
        export_name = None
        nested_schemas: Set[str] = set()

        if isinstance(ma_field, fields.List):
            ma_field = ma_field.inner
            many = True

        if isinstance(ma_field, fields.Nested):
            if not isclass(ma_field.nested) or not issubclass(ma_field.nested, Schema):
                raise ValueError(
                    f"Trying to parse nested field of type: {type(ma_field.nested)}"
                )

            self.schemas_to_parse.add(ma_field.nested)
            export_name = self._get_schema_export_name(ma_field.nested)
            nested_schemas.add(export_name)
            if ma_field.many:
                many = True
        elif class_enum_field is not None and isinstance(ma_field, class_enum_field):
            export_name = ma_field.enum.__name__
            self.add_enum(ma_field.enum)
        elif class_marshamallow_enum_field is not None and isinstance(
            ma_field, class_marshamallow_enum_field
        ):
            export_name = ma_field.enum.__name__
            self.add_enum(ma_field.enum)
        elif issubclass(type(ma_field), fields.Field):
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
        self, schema: Type[Schema], schema_kwargs: Union[Dict[str, Any], None] = None
    ) -> None:
        if schema_kwargs is None:
            schema_kwargs = self.default_info_kwargs

        name = self._get_schema_export_name(schema)
        if name in self.schemas:
            return

        nested_schemas = set()
        fields: List[ParsedField] = []
        for field_name, field in schema._declared_fields.items():
            parsed_field, _nested_schemas = self.parse_field(field_name, field)
            nested_schemas.update(_nested_schemas)
            fields.append(parsed_field)

        parsed_schema = ParsedSchema(name=name, fields=fields, kwargs=schema_kwargs)
        self.schema_nests[parsed_schema] = nested_schemas
        self.schemas[name] = parsed_schema
