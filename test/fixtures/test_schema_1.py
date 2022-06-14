from enum import Enum, auto

from marshmallow import fields, Schema
from marshmallow_enum import EnumField

from marshmallow_export import export_schema, export_mappings

from pathlib import Path


class TestEnum1(Enum):
    A = 'a'
    B = 'b'
    C = 'c'


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


@export_schema(namespace='default')
class RootSchema(Schema):
    nested_leaf_1 = fields.Nested(LeafSchema)
    nested_leaf_2 = fields.Nested(LeafSchema, many=True)
    list_leaf_1 = fields.List(fields.Nested(LeafSchema))
    test_enum_1 = EnumField(TestEnum1)
    test_enum_2 = fields.List(EnumField(TestEnum2))


p = Path().cwd() / 'test_schema_1.ts.export'


export_mappings(
    p,
    'typescript'
)
p = Path().cwd() / 'test_schema_1.rs.export'
export_mappings(
    p,
    'rust'
)
