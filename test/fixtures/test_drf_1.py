from enum import Enum, auto
from pathlib import Path

# from marshmallow import Schema, fields
# from marshmallow_enum import EnumField
from rest_framework import serializers

from marshmallow_export import export_mappings, export_serializer


# class TestEnum1(Enum):
#    A = "a"
#    B = "b"
#    C = "c"
#
#
# class TestEnum2(Enum):
#    A = auto()
#    B = auto()
#    C = auto()


class LeafSerializer(serializers.Serializer):
    bool_1 = serializers.BooleanField()
    datetime_1 = serializers.DateTimeField()
    decimal_1 = serializers.DecimalField(decimal_places=2, max_digits=5)
    int_1 = serializers.IntegerField()


class LeafSerializer2(serializers.Serializer):
    datetime_1 = serializers.DateTimeField(required=False)
    integer_1 = serializers.IntegerField(required=False)
    many_1 = serializers.ListField(child=serializers.CharField())


class MiddleSerializer(serializers.Serializer):
    # test_enum_2 = fields.List(EnumField(TestEnum2))
    leaf_schema = LeafSerializer()


@export_serializer(namespace="default")
class RootSerializer(serializers.Serializer):
    nested_leaf_1 = MiddleSerializer()
    nested_leaf_2 = MiddleSerializer(many=True)
    list_leaf_1 = MiddleSerializer(many=True)
    # test_enum_1 = EnumField(TestEnum1)
    # test_enum_1_marshmallow = fields.Enum(TestEnum1)


@export_serializer(namespace="default")
class RootSerializer2(serializers.Serializer):
    nested_leaf_1 = LeafSerializer2(
        required=True
    )  # fields.Nested(LeafSchema2, required=True)


p = Path().cwd() / "test_drf_1.ts.export"

export_mappings(p, "typescript")
p = Path().cwd() / "test_drf_1.rs.export"
export_mappings(p, "rust")
