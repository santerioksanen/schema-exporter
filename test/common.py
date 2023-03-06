from enum import Enum, auto

from schema_exporter.types import ParsedField, ParsedSchema, PythonDatatypes


class TestEnum(Enum):
    A = "a"
    B = 2
    C = "C"


class TestEnumAuto(Enum):
    A = auto()
    B = auto()
    C = auto()


test_schema = ParsedSchema(
    name="Test",
    fields=[
        ParsedField(
            python_datatype=PythonDatatypes.INT,
            export_name=None,
            field_name="load_only",
            load_only=True,
        ),
        ParsedField(
            python_datatype=PythonDatatypes.INT,
            export_name=None,
            field_name="dump_only",
            dump_only=True,
        ),
        ParsedField(
            python_datatype=PythonDatatypes.INT,
            export_name=None,
            field_name="required",
            required=True,
        ),
        ParsedField(
            python_datatype=PythonDatatypes.INT,
            export_name=None,
            field_name="allow_none",
            allow_none=True,
        ),
        ParsedField(
            python_datatype=PythonDatatypes.INT,
            export_name=None,
            field_name="required_allow_none",
            required=True,
            allow_none=True,
        ),
        ParsedField(python_datatype=None, export_name="Nested", field_name="nested"),
        ParsedField(
            python_datatype=None,
            export_name="Nested",
            field_name="nested_many",
            many=True,
        ),
        ParsedField(
            python_datatype=None, export_name="TestEnum", field_name="enum_field"
        ),
        ParsedField(
            python_datatype=PythonDatatypes.DATETIME,
            export_name=None,
            field_name="datetime_field",
        ),
        ParsedField(
            python_datatype=PythonDatatypes.UUID,
            export_name=None,
            field_name="uuid_field",
        ),
    ],
)
