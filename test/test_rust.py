import unittest
import marshmallow as ma

from marshmallow_enum import EnumField

from enum import Enum

from marshmallow_export.languages import Rust
from marshmallow_export.types import EnumInfo, SchemaInfo, Mapping


class TestEnum(Enum):
    A = 'a'
    B = 2
    C = 'C'


mappings = [
    Mapping(mapping='Clone'),
    Mapping(mapping='Copy'),
    Mapping(mapping='Debug'),
    Mapping(mapping='Serialize', imports={'serde': ['Serialize']}),
    Mapping(mapping='Deserialize', imports={'serde': ['Deserialize']}),
]
test_enum_info = EnumInfo(kwargs={
    'rust_enum_derives': mappings,
})
test_schema_info = SchemaInfo(kwargs={
    'rust_schema_derives': mappings,
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


TEST_SCHEMA_RUST = '''#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Test {
    pub load_only: Option<i64>,
    pub dump_only: Option<i64>,
    pub required: i64,
    pub allow_none: Option<i64>,
    pub required_allow_none: Option<i64>,
    pub nested: Option<Nested>,
    pub nested_many: Option<Vec<Nested>>,
    pub enum_field: Option<TestEnum>,
}
'''

TEST_SCHEMA_RUST_NOT_LOAD_ONLY = '''#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Test {
    pub dump_only: Option<i64>,
    pub required: i64,
    pub allow_none: Option<i64>,
    pub required_allow_none: Option<i64>,
    pub nested: Option<Nested>,
    pub nested_many: Option<Vec<Nested>>,
    pub enum_field: Option<TestEnum>,
}
'''

TEST_SCHEMA_RUST_NOT_DUMP_ONLY = '''#[derive(Clone, Copy, Debug, Serialize, Deserialize)]
pub struct Test {
    pub load_only: Option<i64>,
    pub required: i64,
    pub allow_none: Option<i64>,
    pub required_allow_none: Option<i64>,
    pub nested: Option<Nested>,
    pub nested_many: Option<Vec<Nested>>,
    pub enum_field: Option<TestEnum>,
}
'''


class RustTests(unittest.TestCase):

    def test_basic(self):

        schemas = {
            'default': {
                NestedSchema: SchemaInfo(),
                TestSchema: SchemaInfo(),
            }
        }
        enums = dict()

        exporter = Rust(schemas, enums, dict(), True)

        exp = exporter.format_schema(
            TestSchema,
            test_schema_info,
            True,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_RUST)
        exp = exporter.format_schema(
            TestSchema,
            test_schema_info,
            False,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_RUST_NOT_DUMP_ONLY)
        exp = exporter.format_schema(
            TestSchema,
            test_schema_info,
            True,
            False,
        )
        self.assertEqual(exp, TEST_SCHEMA_RUST_NOT_LOAD_ONLY)

    def test_enum(self):
        schemas = dict()
        enums = dict()

        ts = Rust(schemas, enums, True)

        exp = ts.format_enum(TestEnum, test_enum_info)
        self.assertEqual(exp, TEST_ENUM_RUST)
