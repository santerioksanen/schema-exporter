import unittest
import marshmallow as ma

#from marshmallow_export.ts_utils import _get_ts_mapping
from marshmallow_export.languages import Typescript
from marshmallow_export.types import SchemaInfo


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


TEST_SCHEMA_TS = '''export interface Test {
  load_only?: number;
  dump_only?: number;
  required: number;
  allow_none?: number | null;
  required_allow_none: number | null;
  nested?: Nested;
  nested_many?: Nested[];
};
'''

TEST_SCHEMA_TS_NOT_LOAD_ONLY = '''export interface Test {
  dump_only?: number;
  required: number;
  allow_none?: number | null;
  required_allow_none: number | null;
  nested?: Nested;
  nested_many?: Nested[];
};
'''

TEST_SCHEMA_TS_NOT_DUMP_ONLY = '''export interface Test {
  load_only?: number;
  required: number;
  allow_none?: number | null;
  required_allow_none: number | null;
  nested?: Nested;
  nested_many?: Nested[];
};
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

        exp = exporter._export_schema(
            TestSchema,
            True,
            True,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_TS)
        exp = exporter._export_schema(
            TestSchema,
            True,
            False,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_TS_NOT_DUMP_ONLY)
        exp = exporter._export_schema(
            TestSchema,
            True,
            True,
            False,
        )
        self.assertEqual(exp, TEST_SCHEMA_TS_NOT_LOAD_ONLY)