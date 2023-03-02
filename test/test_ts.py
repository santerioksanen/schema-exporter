import unittest

from marshmallow_export.languages import Typescript
from marshmallow_export.types import EnumInfo

from common import test_schema, TestEnum, TestEnumAuto


TEST_ENUM_TS = '''export enum TestEnum {
  A = "a",
  B = 2,
  C = "C",
}
'''

TEST_ENUM_AUTO_TS = '''export enum TestEnumAuto {
  A = 1,
  B = 2,
  C = 3,
}
'''

TEST_SCHEMA_TS = '''export interface Test {
  load_only?: number;
  dump_only?: number;
  required: number;
  allow_none?: number | null;
  required_allow_none: number | null;
  nested?: Nested;
  nested_many?: Nested[];
  enum_field?: TestEnum;
  datetime_field?: Date;
  uuid_field?: string;
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
  datetime_field?: Date;
  uuid_field?: string;
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
  datetime_field?: Date;
  uuid_field?: string;
}
'''


class TsTests(unittest.TestCase):

    def test_basic(self):

        enums = []

        exporter = Typescript([test_schema], enums)

        exp = exporter.format_schema(
            test_schema,
            True,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_TS)
        exp = exporter.format_schema(
            test_schema,
            False,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_TS_NOT_DUMP_ONLY)
        exp = exporter.format_schema(
            test_schema,
            True,
            False,
        )
        self.assertEqual(exp, TEST_SCHEMA_TS_NOT_LOAD_ONLY)

    def test_enum(self):
        ts = Typescript([], [])

        exp = ts.format_enum(TestEnum, EnumInfo)
        self.assertEqual(exp, TEST_ENUM_TS)

        exp = ts.format_enum(TestEnumAuto, EnumInfo)
        self.assertEqual(exp, TEST_ENUM_AUTO_TS)
