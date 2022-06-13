from enum import Enum
import unittest
from marshmallow import fields
from marshmallow import Schema

from marshmallow_enum import EnumField

from marshmallow_export.languages._abstract import AbstractLanguage
from marshmallow_export.languages._abstract import Mapping

from typing import Tuple
from typing import Dict
from typing import List

class FooSchema(Schema):
    pass


class NestedSchema(Schema):
    pass


class NestingSchema(Schema):
    nested = fields.Nested(NestedSchema)


class ListNestingSchema(Schema):
    nested = fields.List(fields.Nested(NestedSchema))


class BarEnum(Enum):
    BAR = 'bar'


class EnumSchema(Schema):
    bar = EnumField(BarEnum)


class ListEnumSchema(Schema):
    bar = fields.List(EnumField(BarEnum))


class TestLanguage(AbstractLanguage):

    def _mappings(self) -> Dict[fields.Field, Mapping]:
        pass

    def _export_field(
        self,
        ma_field: fields.Field, 
        strip_schema_keyword: bool
    ) -> Tuple[str, str]:
        pass

    def _export_enum(enum: Enum):
        pass

    def _export_schema(
        schema: Schema,
        strip_schema_keyword: bool,
        include_dump_only: bool,
        include_load_only: bool
    ) -> str:
        pass


class AbstractLanguageTests(unittest.TestCase):

    def test_get_schma_name_no_strip_schema(self):

        self.assertEqual(
            AbstractLanguage._get_schema_export_name(FooSchema, False),
            'FooSchema'
        )

    def test_get_schema_name_strip_schema(self):

        self.assertEqual(
            AbstractLanguage._get_schema_export_name(FooSchema, True),
            'Foo'
        )
    
    def test_expand_nested(self):
        schemas = {
            'foo': set([NestingSchema]),
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
    
    def test_expand_list_nested(self):
        schemas = {
            'foo': set([ListNestingSchema]),
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
    
    def test_expand_enum(self):
        schemas = {
            'foo': set([EnumSchema]),
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
            'foo': set([ListEnumSchema]),
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
