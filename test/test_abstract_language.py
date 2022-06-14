from enum import Enum
import unittest
from marshmallow import Schema, fields

from marshmallow_enum import EnumField

from marshmallow_export.languages.abstract import AbstractLanguage
from marshmallow_export.types import SchemaInfo

from typing import Tuple


class FooSchema(Schema):
    pass


class NestedSchema(Schema):
    pass


class NestingSchema(Schema):
    nested = fields.Nested(NestedSchema)


class DeeplyNestedSchema(Schema):
    nested = fields.Nested(NestingSchema)


class ListNestingSchema(Schema):
    nested = fields.List(fields.Nested(NestedSchema))


class DeeplyNestedListSchema(Schema):
    nested = fields.List(fields.Nested(ListNestingSchema))


class BarEnum(Enum):
    BAR = 'bar'


class EnumSchema(Schema):
    bar = EnumField(BarEnum)


class ListEnumSchema(Schema):
    bar = fields.List(EnumField(BarEnum))


class TestLanguage(AbstractLanguage):

    def _export_field(
            self,
            field_name: str,
            ma_field: fields.Field,
    ) -> Tuple[str, str]:
        pass

    def _export_enum(enum: Enum):
        pass

    def _export_schema(
            self,
            schema: Schema,
            include_dump_only: bool,
            include_load_only: bool
    ) -> str:
        pass
    
    def _export_header(self, namespace: str):
        pass


class AbstractLanguageTests(unittest.TestCase):

    def test_get_schema_name_no_strip_schema(self):

        tl = TestLanguage(
            schemas=dict(),
            enums=dict(),
            strip_schema_keyword=False
        )

        self.assertEqual(
            tl.get_schema_export_name(FooSchema),
            'FooSchema'
        )

    def test_get_schema_name_strip_schema(self):

        tl = TestLanguage(
            schemas=dict(),
            enums=dict(),
            strip_schema_keyword=True
        )

        self.assertEqual(
            tl.get_schema_export_name(FooSchema),
            'Foo'
        )
    
    def test_expand_nested(self):
        schemas = {
            'foo': {NestingSchema: SchemaInfo()},
        }
        enums = dict()

        tl = TestLanguage(
            schemas,
            enums,
            False,
        )

        tl._expand_nested()

        self.assertTrue(
            NestingSchema in tl.schemas['foo']
        )
        self.assertTrue(
            NestedSchema in tl.schemas['foo']
        )
        self.assertEqual(len(tl.schemas['foo']), 2)
        self.assertEqual(len(tl.enums['foo']), 0)

        tl._add_dependencies_for_schemas()
        tl._add_ordering_to_schemas()

        self.assertEqual(
            tl.schemas['foo'][NestingSchema].ordering,
            1
        )
        self.assertEqual(
            tl.schemas['foo'][NestedSchema].ordering,
            0
        )
        self.assertTrue(
            NestingSchema in tl.schemas['foo'][NestedSchema].nested_by
        )
        self.assertTrue(
            NestedSchema in tl.schemas['foo'][NestingSchema].nests
        )
    
    def test_expand_deeply_nested(self):
        schemas = {
            'foo': {DeeplyNestedSchema: SchemaInfo()},
        }
        enums = dict()

        tl = TestLanguage(
            schemas,
            enums,
            False,
        )

        tl._expand_nested()

        self.assertTrue(
            DeeplyNestedSchema in tl.schemas['foo']
        )
        self.assertTrue(
            NestingSchema in tl.schemas['foo']
        )
        self.assertTrue(
            NestedSchema in tl.schemas['foo']
        )
        self.assertEqual(len(tl.schemas['foo']), 3)
        self.assertEqual(len(tl.enums['foo']), 0)

        tl._add_dependencies_for_schemas()
        tl._add_ordering_to_schemas()

        self.assertEqual(
            tl.schemas['foo'][DeeplyNestedSchema].ordering,
            2
        )
        self.assertEqual(
            tl.schemas['foo'][NestingSchema].ordering,
            1
        )
        self.assertEqual(
            tl.schemas['foo'][NestedSchema].ordering,
            0
        )
        self.assertTrue(
            NestingSchema in tl.schemas['foo'][DeeplyNestedSchema].nests
        )
        self.assertTrue(
            NestedSchema in tl.schemas['foo'][DeeplyNestedSchema].nests
        )
        self.assertTrue(
            DeeplyNestedSchema in tl.schemas['foo'][NestingSchema].nested_by
        )
        self.assertTrue(
            DeeplyNestedSchema in tl.schemas['foo'][NestedSchema].nested_by
        )
        self.assertTrue(
            NestingSchema in tl.schemas['foo'][NestedSchema].nested_by
        )
        self.assertTrue(
            NestedSchema in tl.schemas['foo'][NestingSchema].nests
        )
    
    def test_expand_list_nested(self):
        schemas = {
            'foo': {ListNestingSchema: SchemaInfo()},
        }
        enums = dict()

        tl = TestLanguage(
            schemas,
            enums,
            False,
        )

        tl._expand_nested()

        self.assertTrue(
            ListNestingSchema in tl.schemas['foo']
        )
        self.assertTrue(
            NestedSchema in tl.schemas['foo']
        )
        self.assertEqual(len(tl.schemas['foo']), 2)
        self.assertEqual(len(tl.enums['foo']), 0)
    
    def test_expand_list_deeply_nested(self):
        schemas = {
            'foo': {DeeplyNestedListSchema: SchemaInfo()},
        }
        enums = dict()

        tl = TestLanguage(
            schemas,
            enums,
            False,
        )

        tl._expand_nested()

        self.assertTrue(
            DeeplyNestedListSchema in tl.schemas['foo']
        )
        self.assertTrue(
            ListNestingSchema in tl.schemas['foo']
        )
        self.assertTrue(
            NestedSchema in tl.schemas['foo']
        )
        self.assertEqual(len(tl.schemas['foo']), 3)
        self.assertEqual(len(tl.enums['foo']), 0)
    
    def test_expand_enum(self):
        schemas = {
            'foo': {EnumSchema: SchemaInfo()},
        }
        enums = dict()

        tl = TestLanguage(
            schemas,
            enums,
            False,
        )

        tl._expand_nested()

        self.assertTrue(
            EnumSchema in tl.schemas['foo']
        )
        self.assertTrue(
            BarEnum in tl.enums['foo']
        )
        self.assertEqual(len(tl.schemas['foo']), 1)
        self.assertEqual(len(tl.enums['foo']), 1)

    def test_expand_list_enum(self):
        schemas = {
            'foo': {ListEnumSchema: SchemaInfo()},
        }
        enums = dict()

        tl = TestLanguage(
            schemas,
            enums,
            False,
        )

        tl._expand_nested()

        self.assertTrue(
            ListEnumSchema in tl.schemas['foo']
        )
        self.assertTrue(
            BarEnum in tl.enums['foo']
        )
        self.assertEqual(len(tl.schemas['foo']), 1)
        self.assertEqual(len(tl.enums['foo']), 1)
