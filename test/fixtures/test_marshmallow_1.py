from enum import Enum, auto
from pathlib import Path

from marshmallow import Schema, fields
from marshmallow_enum import EnumField

from marshmallow_export import export_mappings, export_schema


class TestEnum1(Enum):
    A = "a"
    B = "b"
    C = "c"


class TestEnum2(Enum):
    A = auto()
    B = auto()
    C = auto()


class LeafSchema(Schema):
    bool_1 = fields.Bool()
    boolean_1 = fields.Boolean()
    datetime_1 = fields.DateTime()
    decimal_1 = fields.Decimal()
    int_1 = fields.Int()
    integer_1 = fields.Integer()


class LeafSchema2(Schema):
    datetime_1 = fields.DateTime(required=True)
    decimal_1 = fields.Decimal(required=True)


class MiddleSchema(Schema):
    test_enum_2 = fields.List(EnumField(TestEnum2))
    leaf_schema = fields.Nested(LeafSchema)


@export_schema(namespace="default")
class RootSchema(Schema):
    nested_leaf_1 = fields.Nested(MiddleSchema)
    nested_leaf_2 = fields.Nested(MiddleSchema, many=True)
    list_leaf_1 = fields.List(fields.Nested(MiddleSchema))
    test_enum_1 = EnumField(TestEnum1)
    test_enum_1_marshmallow = fields.Enum(TestEnum1)


@export_schema(namespace="default")
class RootSchema2(Schema):
    nested_leaf_1 = fields.Nested(LeafSchema2, required=True)


p = Path().cwd() / "test_marshmallow_1.ts.export"

export_mappings(p, "typescript")
p = Path().cwd() / "test_marshmallow_1.rs.export"
export_mappings(p, "rust")
