import unittest
import marshmallow as ma

from marshmallow_enum import EnumField

from enum import Enum, auto

from marshmallow_export.languages import Typescript
from marshmallow_export.types import SchemaInfo, EnumInfo


class TestEnum(Enum):
    A = 'a'
    B = 2
    C = 'C'


TEST_ENUM_TS = '''export enum TestEnum {
  A = "a",
  B = 2,
  C = "C",
}
'''


class TestEnumAuto(Enum):
    A = auto()
    B = auto()
    C = auto()


TEST_ENUM_AUTO_TS = '''export enum TestEnumAuto {
  A = 1,
  B = 2,
  C = 3,
}
'''


class NestedSchema(ma.Schema):
    foo = ma.fields.Integer()


class TestSchema(ma.Schema):
    load_only = ma.fields.Integer(load_only=True)
    dump_only = ma.fields.Integer(dump_only=True)
    required = ma.fields.Integer(required=True)
    allow_none = ma.fields.Integer(allow_none=True)
    required_allow_none = ma.fields.Integer(required=True, allow_none=True)
    nested = ma.fields.Nested(NestedSchema)
    nested_many = ma.fields.Nested(NestedSchema, many=True)
    enum_field = EnumField(TestEnum)


TEST_SCHEMA_TS = '''export interface Test {
  load_only?: number;
  dump_only?: number;
  required: number;
  allow_none?: number | null;
  required_allow_none: number | null;
  nested?: Nested;
  nested_many?: Nested[];
  enum_field?: TestEnum;
}
'''

TEST_SCHEMA_TS_NOT_LOAD_ONLY = '''export interface Test {
  dump_only?: number;
  required: number;
  allow_none?: number | null;
  required_allow_none: number | null;
  nested?: Nested;
  nested_many?: Nested[];
  enum_field?: TestEnum;
}
'''

TEST_SCHEMA_TS_NOT_DUMP_ONLY = '''export interface Test {
  load_only?: number;
  required: number;
  allow_none?: number | null;
  required_allow_none: number | null;
  nested?: Nested;
  nested_many?: Nested[];
  enum_field?: TestEnum;
}
'''


class TsTests(unittest.TestCase):

    def test_basic(self):

        schemas = {
            'default': {
                NestedSchema: SchemaInfo(),
                TestSchema: SchemaInfo(),
            }
        }
        enums = dict()

        exporter = Typescript(schemas, enums, True)

        exp = exporter.format_schema(
            TestSchema,
            SchemaInfo(),
            True,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_TS)
        exp = exporter.format_schema(
            TestSchema,
            SchemaInfo(),
            False,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_TS_NOT_DUMP_ONLY)
        exp = exporter.format_schema(
            TestSchema,
            SchemaInfo(),
            True,
            False,
        )
        self.assertEqual(exp, TEST_SCHEMA_TS_NOT_LOAD_ONLY)

    def test_enum(self):
        schemas = dict()
        enums = dict()

        ts = Typescript(schemas, enums, True)

        exp = ts.format_enum(TestEnum, EnumInfo)
        self.assertEqual(exp, TEST_ENUM_TS)

        exp = ts.format_enum(TestEnumAuto, EnumInfo)
        self.assertEqual(exp, TEST_ENUM_AUTO_TS)
