import unittest
from copy import copy

from common import TestEnum, TestEnumAuto
from common import test_schema as base_test_schema

from schema_exporter.languages import Rust
from schema_exporter.types import EnumInfo, Mapping, SchemaInfo

mappings = [
    Mapping(mapping="Clone"),
    Mapping(mapping="Copy"),
    Mapping(mapping="Debug"),
    Mapping(mapping="Serialize", imports={"serde": ["Serialize"]}),
    Mapping(mapping="Deserialize", imports={"serde": ["Deserialize"]}),
]
test_enum_info = EnumInfo(
    kwargs={
        "rust_enum_derives": mappings,
    }
)
test_schema_info = SchemaInfo(
    kwargs={
        "rust_schema_derives": mappings,
    }
)
test_schema = copy(base_test_schema)
test_schema.kwargs = {
    "rust_schema_derives": mappings,
}

TEST_ENUM_RUST = """#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub enum TestEnum {
    A,
    B,
    C,
}
"""

TEST_ENUM_AUTO_RUST = """#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub enum TestEnumAuto {
    A,
    B,
    C,
}
"""

TEST_SCHEMA_RUST = """#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub struct Test {
    pub load_only: Option<i64>,
    pub dump_only: Option<i64>,
    pub required: i64,
    pub allow_none: Option<i64>,
    pub required_allow_none: Option<i64>,
    pub nested: Option<Nested>,
    pub nested_many: Option<Vec<Nested>>,
    pub enum_field: Option<TestEnum>,
    pub datetime_field: Option<DateTime<Utc>>,
    pub uuid_field: Option<Uuid>,
}
"""

TEST_SCHEMA_RUST_NOT_LOAD_ONLY = """#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub struct Test {
    pub dump_only: Option<i64>,
    pub required: i64,
    pub allow_none: Option<i64>,
    pub required_allow_none: Option<i64>,
    pub nested: Option<Nested>,
    pub nested_many: Option<Vec<Nested>>,
    pub enum_field: Option<TestEnum>,
    pub datetime_field: Option<DateTime<Utc>>,
    pub uuid_field: Option<Uuid>,
}
"""

TEST_SCHEMA_RUST_NOT_DUMP_ONLY = """#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub struct Test {
    pub load_only: Option<i64>,
    pub required: i64,
    pub allow_none: Option<i64>,
    pub required_allow_none: Option<i64>,
    pub nested: Option<Nested>,
    pub nested_many: Option<Vec<Nested>>,
    pub enum_field: Option<TestEnum>,
    pub datetime_field: Option<DateTime<Utc>>,
    pub uuid_field: Option<Uuid>,
}
"""

TEST_HEADER = """use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use uuid::Uuid;
"""


class RustTests(unittest.TestCase):
    def test_basic(self):
        exporter = Rust([test_schema], [])

        exp = exporter.format_header(True, True)
        self.assertEqual(exp, TEST_HEADER)

        exp = exporter.format_schema(
            test_schema,
            True,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_RUST)
        exp = exporter.format_schema(
            test_schema,
            False,
            True,
        )
        self.assertEqual(exp, TEST_SCHEMA_RUST_NOT_DUMP_ONLY)
        exp = exporter.format_schema(
            test_schema,
            True,
            False,
        )
        self.assertEqual(exp, TEST_SCHEMA_RUST_NOT_LOAD_ONLY)

    def test_enum(self):
        ts = Rust([], [])

        exp = ts.format_enum(TestEnum, test_enum_info)
        self.assertEqual(exp, TEST_ENUM_RUST)

        exp = ts.format_enum(TestEnumAuto, test_enum_info)
        self.assertEqual(exp, TEST_ENUM_AUTO_RUST)
