import unittest
import marshmallow as ma

from marshmallow_enum import EnumField

from enum import Enum, auto

from marshmallow_export.languages import Rust
from marshmallow_export.types import EnumInfo, Mapping


class TestEnum(Enum):
    A = 'a'
    B = 2
    C = 'C'


test_enum_info = EnumInfo(kwargs={
    'rust_enum_derives': [
        Mapping(mapping='Clone'),
        Mapping(mapping='Copy'),
        Mapping(mapping='Debug'),
        Mapping(mapping='Serialize', imports={'serde': ['Serialize']}),
        Mapping(mapping='Deserialize', imports={'serde': ['Deserialize']}),
    ]
})


TEST_ENUM_RUST = '''#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub enum TestEnum {
    A,
    B,
    C,
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


class RustTests(unittest.TestCase):

#    def test_basic(self):
#
#        schemas = {
#            'default': {
#                NestedSchema: SchemaInfo(),
#                TestSchema: SchemaInfo(),
#            }
#        }
#        enums = dict()
#
#        exporter = Typescript(schemas, enums, True)
#
#        exp = exporter._export_schema(
#            TestSchema,
#            True,
#            True,
#        )
#        self.assertEqual(exp, TEST_SCHEMA_TS)
#        exp = exporter._export_schema(
#            TestSchema,
#            False,
#            True,
#        )
#        self.assertEqual(exp, TEST_SCHEMA_TS_NOT_DUMP_ONLY)
#        exp = exporter._export_schema(
#            TestSchema,
#            True,
#            False,
#        )
#        self.assertEqual(exp, TEST_SCHEMA_TS_NOT_LOAD_ONLY)

    def test_enum(self):
        schemas = dict()
        enums = dict()

        ts = Rust(schemas, enums, True)

        exp = ts.format_enum(TestEnum, test_enum_info)
        self.assertEqual(exp, TEST_ENUM_RUST)
