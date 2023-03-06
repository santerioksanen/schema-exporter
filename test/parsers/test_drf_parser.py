from rest_framework import serializers

from schema_exporter.parsers.drf_parser import DRFParser, _create_enum_from_choices
from schema_exporter.types import PythonDatatypes

from ._common import BaseParserTests


class FooSerializer(serializers.Serializer):
    pass


class DRFParserTests(BaseParserTests):
    def setUp(self):
        self.parser_default = DRFParser(
            default_info_kwargs=dict(), strip_schema_from_name=True
        )
        self.parser_dont_strip_name = DRFParser(
            default_info_kwargs=dict(), strip_schema_from_name=False
        )

    def test_parse_enum(self):
        field = serializers.ChoiceField([("A", "a"), ("B", "b"), ("C", "c")])

        en, many = _create_enum_from_choices("test_field", field)
        self.assertFalse(many)
        self.assertEqual(en.__name__, "TestField")
        self.assertDictEqual(
            {key: val.value for key, val in en._member_map_.items()},
            {"A": "a", "B": "b", "C": "c"},
        )

    def test_parse_enum_multiple(self):
        field = serializers.MultipleChoiceField(
            choices=[("A", "a"), ("B", "b"), ("C", "c")]
        )

        en, many = _create_enum_from_choices("test_field", field)
        self.assertTrue(many)
        self.assertEqual(en.__name__, "TestField")
        self.assertDictEqual(
            {key: val.value for key, val in en._member_map_.items()},
            {"A": "a", "B": "b", "C": "c"},
        )

    def test_parse_enum_list(self):
        field = serializers.ChoiceField(["A", "B", "C"])

        en, many = _create_enum_from_choices("test_field", field)
        self.assertFalse(many)
        self.assertEqual(en.__name__, "TestField")
        self.assertDictEqual(
            {key: val.value for key, val in en._member_map_.items()},
            {"A": "A", "B": "B", "C": "C"},
        )

    def test_parse_choice_field(self):
        field = serializers.ChoiceField([("A", "a"), ("B", "b"), ("C", "c")])
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "export_name": "Field",
                "field_name": "field",
                "required": True,
            },
        )

    def test_parse_multiple_choice_field(self):
        field = serializers.MultipleChoiceField(
            choices=[("A", "a"), ("B", "b"), ("C", "c")]
        )
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "export_name": "Field",
                "field_name": "field",
                "required": True,
                "many": True,
            },
        )

    def test_get_schema_name_no_strip_schema(self) -> None:
        self.assertEqual(
            self.parser_dont_strip_name._get_schema_export_name(FooSerializer()),
            "FooSerializer",
        )

    def test_get_schema_name_strip_schema(self):
        self.assertEqual(
            self.parser_default._get_schema_export_name(FooSerializer()), "Foo"
        )

    def test_parse_read_only_field(self):
        field = serializers.IntegerField(read_only=True)
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
        field = serializers.IntegerField(write_only=True)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "python_datatype": PythonDatatypes.INT,
                "field_name": "field",
                "load_only": True,
                "required": True,
            },
        )

    def test_parse_not_required_field(self):
        field = serializers.IntegerField(required=False)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "python_datatype": PythonDatatypes.INT,
                "field_name": "field",
                "required": False,
            },
        )

    def test_parse_allow_none_field(self):
        field = serializers.IntegerField(allow_null=True)
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "python_datatype": PythonDatatypes.INT,
                "field_name": "field",
                "required": True,
                "allow_none": True,
            },
        )

    def test_parse_list_field(self):
        field = serializers.ListField(child=serializers.IntegerField())
        parsed = self.parser_default.parse_field("field", field)[0]
        self.assert_parsed_field(
            parsed,
            {
                "python_datatype": PythonDatatypes.INT,
                "field_name": "field",
                "required": True,
                "many": True,
            },
        )


# TODO: Tester for nested fields, slug fields, whole schema
