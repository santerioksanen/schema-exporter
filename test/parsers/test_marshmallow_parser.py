import unittest
from enum import Enum
from marshmallow_export.parsers.marshmallow_parser import MarshmallowParser
from marshmallow_export.types import SchemaInfo

from marshmallow import Schema, fields
from marshmallow_enum import EnumField


class FooSchema(Schema):
    pass


class NestedSchema(Schema):
    pass


class NestingSchema(Schema):
    nested = fields.Nested(NestedSchema)


class DeeplyNestedSchema(Schema):
    nested = fields.Nested(NestingSchema)


class ListNestingSchema(Schema):
    nested = fields.List(fields.Nested(NestedSchema))


class DeeplyNestedListSchema(Schema):
    nested = fields.List(fields.Nested(ListNestingSchema))


class BarEnum(Enum):
    BAR = "bar"


class EnumSchema(Schema):
    bar = EnumField(BarEnum)


class ListEnumSchema(Schema):
    bar = fields.List(EnumField(BarEnum))


class MarshmallowParserTests(unittest.TestCase):
    def test_get_schema_name_no_strip_schema(self):
        parser = MarshmallowParser(
            default_info_kwargs=dict(), strip_schema_from_name=False
        )

        self.assertEqual(parser._get_schema_export_name(FooSchema), "FooSchema")

    def test_get_schema_name_strip_schema(self):
        parser = MarshmallowParser(
            default_info_kwargs=dict(), strip_schema_from_name=True
        )

        self.assertEqual(parser._get_schema_export_name(FooSchema), "Foo")

    def test_expand_nested(self):
        schemas = {NestingSchema: SchemaInfo()}

        parser = MarshmallowParser(
            default_info_kwargs=dict(), strip_schema_from_name=True
        )
        for schema, schema_info in schemas.items():
            parser.parse_and_add_schema(schema, schema_info.kwargs)

        parser.parse_nested()
        result_schemas = list(parser.schemas)
