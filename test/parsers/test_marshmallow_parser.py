from enum import Enum

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from marshmallow_export.parsers.marshmallow_mappings import marshmallow_mappings
from marshmallow_export.parsers.marshmallow_parser import MarshmallowParser
from marshmallow_export.types import PythonDatatypes

from ._common import BaseParserTests

NOT_DEFINED = "NOT_DEFINED"

field_mappings = {
    fields.AwareDateTime: PythonDatatypes.DATETIME,
    fields.Bool: PythonDatatypes.BOOL,
    fields.Constant: PythonDatatypes.CONSTANT,
    fields.Date: PythonDatatypes.DATE,
    fields.DateTime: PythonDatatypes.DATETIME,
    fields.Decimal: PythonDatatypes.DECIMAL,
    fields.Dict: PythonDatatypes.DICT,
    fields.Email: PythonDatatypes.EMAIL,
    fields.Enum: NOT_DEFINED,
    fields.Field: NOT_DEFINED,
    fields.Float: PythonDatatypes.FLOAT,
    fields.Function: PythonDatatypes.FUNCTION,
    fields.IP: PythonDatatypes.IP_ADDRESS,
    fields.IPInterface: PythonDatatypes.IP_INTERFACE,
    fields.IPv4: PythonDatatypes.IPv4_ADDRESS,
    fields.IPv4Interface: PythonDatatypes.IPv4_INTERFACE,
    fields.IPv6: PythonDatatypes.IPv6_ADDRESS,
    fields.IPv6Interface: PythonDatatypes.IPv6_INTERFACE,
    fields.Int: PythonDatatypes.INT,
    fields.Integer: PythonDatatypes.INT,
    fields.List: NOT_DEFINED,
    fields.Mapping: PythonDatatypes.MAPPING,
    fields.Method: PythonDatatypes.METHOD,
    fields.NaiveDateTime: PythonDatatypes.DATETIME,
    fields.Nested: NOT_DEFINED,
    fields.Number: PythonDatatypes.FLOAT,
    fields.Pluck: NOT_DEFINED,
    fields.Raw: NOT_DEFINED,
    fields.Str: PythonDatatypes.STRING,
    fields.String: PythonDatatypes.STRING,
    fields.Time: PythonDatatypes.TIME,
    fields.Tuple: NOT_DEFINED,
    fields.URL: PythonDatatypes.URL,
    fields.UUID: PythonDatatypes.UUID,
    fields.Url: PythonDatatypes.URL,
}


class TestEnum(Enum):
    a = 1
    b = 2


class FooSchema(Schema):
    pass


class BasicSchema(Schema):
    integer_field = fields.Integer()
    float_field = fields.Float()


class NestingSchema(Schema):
    basic = fields.Nested(BasicSchema)


class RootSchema(Schema):
    nested = fields.Nested(NestingSchema)


class MarshmallowParserTests(BaseParserTests):
    def setUp(self):
        self.parser_default = MarshmallowParser(
            default_info_kwargs=dict(), strip_schema_from_name=True
        )
        self.parser_dont_strip_name = MarshmallowParser(
            default_info_kwargs=dict(), strip_schema_from_name=False
        )

    def test_verify_field_mappings(self) -> None:
        for key, value in field_mappings.items():
            if value == NOT_DEFINED:
                self.assertNotIn(key, marshmallow_mappings)
            else:
                self.assertEqual(marshmallow_mappings[key], value)

    def test_parse_native_enum_field(self) -> None:
        field = fields.Enum(TestEnum)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "export_name": "TestEnum",
                "field_name": "field",
            },
        )
        self.assertIn(TestEnum, self.parser_default.enums.keys())

    def test_parse_non_native_enum_field(self) -> None:
        field = EnumField(TestEnum)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "export_name": "TestEnum",
                "field_name": "field",
            },
        )
        self.assertIn(TestEnum, self.parser_default.enums.keys())

    def test_get_schema_name_no_strip_schema(self) -> None:
        self.assertEqual(
            self.parser_dont_strip_name._get_schema_export_name(FooSchema), "FooSchema"
        )

    def test_get_schema_name_strip_schema(self):
        self.assertEqual(self.parser_default._get_schema_export_name(FooSchema), "Foo")

    def test_parse_read_only_field(self):
        field = fields.Integer(dump_only=True)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "python_datatype": PythonDatatypes.INT,
                "field_name": "field",
                "dump_only": True,
            },
        )

    def test_parse_load_only_field(self):
        field = fields.Integer(load_only=True)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "python_datatype": PythonDatatypes.INT,
                "field_name": "field",
                "load_only": True,
            },
        )

    def test_parse_required_field(self):
        field = fields.Integer(required=True)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "python_datatype": PythonDatatypes.INT,
                "field_name": "field",
                "required": True,
            },
        )

    def test_parse_allow_none_field(self):
        field = fields.Integer(allow_none=True)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "python_datatype": PythonDatatypes.INT,
                "field_name": "field",
                "allow_none": True,
            },
        )

    def test_parse_nested_field(self):
        field = fields.Nested(FooSchema)
        parsed, nested = self.parser_default.parse_field("field", field)
        self.assert_parsed_field(
            parsed,
            {
                "export_name": "Foo",
                "field_name": "field",
            },
        )
        self.assertTrue("Foo" in nested)

    def test_parse_nested_field_many(self):
        field = fields.Nested(FooSchema, many=True)
        parsed, nested = self.parser_default.parse_field("field", field)
        self.assert_parsed_field(
            parsed,
            {
                "export_name": "Foo",
                "field_name": "field",
                "many": True,
            },
        )
        self.assertTrue("Foo" in nested)

    def test_parse_list_field(self):
        field = fields.List(fields.Integer)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "python_datatype": PythonDatatypes.INT,
                "field_name": "field",
                "many": True,
            },
        )

    def test_parse_basic_schema(self):
        self.parser_default.parse_and_add_schema(BasicSchema, {})
        parsed_schemas = list(self.parser_default.schemas.values())
        parsed_schema = parsed_schemas[0]
        self.assertEqual(len(parsed_schemas), 1)
        self.assertEqual(len(parsed_schema.fields), 2)
        self.assertEqual(parsed_schema.name, "Basic")

    def test_parse_nested_schema(self):
        self.parser_default.parse_and_add_schema(RootSchema)
        self.parser_default.parse_nested()
        self.assertEqual(len(self.parser_default.schemas.values()), 3)


#    def test_expand_nested(self):
#        schemas = {NestingSchema: SchemaInfo()}
#
#        parser = MarshmallowParser(
#            default_info_kwargs=dict(), strip_schema_from_name=True
#        )
#        for schema, schema_info in schemas.items():
#            parser.parse_and_add_schema(schema, schema_info.kwargs)
#
#        parser.parse_nested()
#        result_schemas = list(parser.schemas)
