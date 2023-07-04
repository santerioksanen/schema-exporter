from django.db import models
from rest_framework import serializers

from schema_exporter.parsers.drf_parser import DRFParser
from schema_exporter.types import PythonDatatypes

from ._common import BaseParserTests


class TestModel(models.Model):
    __test__ = False

    class Meta:
        app_label = "tests"
        abstract = True


class IntModel(TestModel):
    int_field = models.IntegerField()


class IntNestedModel(TestModel):
    child = models.ForeignKey(IntModel, on_delete=models.CASCADE, null=False)


class StringPrimaryKeyModel(TestModel):
    guid = models.CharField(primary_key=True)


class StringNestedModel(TestModel):
    child = models.ForeignKey(
        StringPrimaryKeyModel, on_delete=models.CASCADE, null=False
    )


class PropertyModel(TestModel):
    @property
    def prop_str(self) -> str:
        return "ABBA"

    @property
    def opt_prop_str(self) -> str | None:
        return "ABBA"

    @property
    def prop_int(self) -> int:
        return 15

    @property
    def opt_prop_int(self) -> int | None:
        return 15


class IntSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntModel
        fields = "__all__"


class IntNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = IntNestedModel
        fields = "__all__"


class StringPrimaryKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = StringPrimaryKeyModel
        fields = "__all__"


class StringNestedSerializer(serializers.ModelSerializer):
    class Meta:
        model = StringNestedModel
        fields = "__all__"


class PropertySerializer(serializers.ModelSerializer):
    class Meta:
        model = PropertyModel
        fields = ("id", "prop_str", "opt_prop_str", "prop_int", "opt_prop_int")


class ModelSerializerTestCase(BaseParserTests):
    def setUp(self):
        self.parser = DRFParser(default_info_kwargs=dict(), strip_schema_from_name=True)

    def test_parse_int_serializer(self):
        self.parser.parse_and_add_schema(IntSerializer())
        parsed_schema = self.parser.schemas["Int"]
        id_field = parsed_schema.fields[0]
        self.assert_parsed_field(
            id_field,
            {
                "field_name": "id",
                "required": False,
                "python_datatype": PythonDatatypes.INT,
                "dump_only": True,
            },
        )

        parsed_field = parsed_schema.fields[1]
        self.assert_parsed_field(
            parsed_field,
            {
                "field_name": "int_field",
                "required": True,
                "python_datatype": PythonDatatypes.INT,
            },
        )

    def test_parse_string_primary_key_serializer(self):
        self.parser.parse_and_add_schema(StringPrimaryKeySerializer())
        parsed_schema = self.parser.schemas["StringPrimaryKey"]
        self.assertEqual(len(parsed_schema.fields), 1)

        parsed_field = parsed_schema.fields[0]
        self.assert_parsed_field(
            parsed_field,
            {
                "field_name": "guid",
                "required": True,
                "python_datatype": PythonDatatypes.STRING,
                "dump_only": False,
            },
        )

    def test_int_nested_serializer(self):
        self.parser.parse_and_add_schema(IntNestedSerializer())
        parsed_schema = self.parser.schemas["IntNested"]
        self.assertEqual(len(parsed_schema.fields), 2)

        parsed_field = parsed_schema.fields[1]
        self.assert_parsed_field(
            parsed_field,
            {
                "field_name": "child",
                "required": True,
                "python_datatype": PythonDatatypes.INT,
                "dump_only": False,
            },
        )

    def test_string_nested_serializer(self):
        self.parser.parse_and_add_schema(StringNestedSerializer())
        parsed_schema = self.parser.schemas["StringNested"]
        self.assertEqual(len(parsed_schema.fields), 2)

        parsed_field = parsed_schema.fields[1]
        self.assert_parsed_field(
            parsed_field,
            {
                "field_name": "child",
                "required": True,
                "python_datatype": PythonDatatypes.STRING,
                "dump_only": False,
            },
        )

    def test_property_serializer(self):
        self.parser.parse_and_add_schema(PropertySerializer())
        parsed_schema = self.parser.schemas["Property"]
        self.assertEqual(len(parsed_schema.fields), 5)

        prop_str_field = parsed_schema.fields[1]
        self.assert_parsed_field(
            prop_str_field,
            {
                "field_name": "prop_str",
                "required": False,
                "dump_only": True,
                "python_datatype": PythonDatatypes.STRING,
            },
        )

        opt_prop_str_field = parsed_schema.fields[2]
        self.assert_parsed_field(
            opt_prop_str_field,
            {
                "field_name": "opt_prop_str",
                "required": False,
                "dump_only": True,
                "python_datatype": PythonDatatypes.STRING,
                "allow_none": True,
            },
        )

        prop_int_field = parsed_schema.fields[3]
        self.assert_parsed_field(
            prop_int_field,
            {
                "field_name": "prop_int",
                "required": False,
                "dump_only": True,
                "python_datatype": PythonDatatypes.INT,
            },
        )

        opt_prop_int_field = parsed_schema.fields[4]
        self.assert_parsed_field(
            opt_prop_int_field,
            {
                "field_name": "opt_prop_int",
                "required": False,
                "dump_only": True,
                "python_datatype": PythonDatatypes.INT,
                "allow_none": True,
            },
        )
