from abc import ABCMeta, abstractmethod

from marshmallow import Schema, fields

from marshmallow_enum import EnumField
from enum import Enum

from typing import Tuple, Dict, List, Set

from marshmallow_export.types import Mapping, SchemaInfo


class AbstractLanguage(metaclass = ABCMeta):

    def __init__(
        self,
        schemas: Dict[str, Dict[Schema, SchemaInfo]],
        enums: Dict[str, Set[Enum]],
        expand_nested: bool
    ) -> None:

        self.schemas = schemas
        self.enums = enums

        if expand_nested:
            self._expand_nested()
        
        self._add_dependencies_for_schemas()
        self._add_ordering_to_schemas()

    def _expand_schema(
        self,
        schema: Schema
    ) -> Tuple[Set[Schema], Set[Enum]]:
        """ If given schema has nested schemas or enums, returns a set 
            with all chained schemas as well. 
        """
        
        schemas_to_add = set()
        enums_to_add = set()

        for field in schema._declared_fields.values():
            recurse_field = None
            if isinstance(field, fields.Nested):
                schemas_to_add.add(field.nested)
                recurse_field = field.nested

            elif isinstance(field, fields.List):
                if isinstance(field.inner, fields.Nested):
                    schemas_to_add.add(field.inner.nested)
                    recurse_field = field.inner.nested
                elif isinstance(field.inner, EnumField):
                    enums_to_add.add(field.inner.enum)

            elif isinstance(field, EnumField):
                enums_to_add.add(field.enum)
            
            if recurse_field is not None:
                tmp = self._expand_schema(recurse_field)
                schemas_to_add.update(tmp[0])
                enums_to_add.update(tmp[1])
        
        return schemas_to_add, enums_to_add

    def _expand_nested(self) -> None:
        """ Iterates through all schemas, and adds nested schemas and enums
            to be included in formatted output
        """
        for namespace, schema_list in self.schemas.items():
            for schema in schema_list.keys():
                schemas_to_add, enums_to_add = self._expand_schema(schema)
            
            for schema in schemas_to_add:
                if schema not in self.schemas[namespace]:
                    self.schemas[namespace][schema] = SchemaInfo()

            if not namespace in self.enums:
                self.enums[namespace] = set()
            
            self.enums[namespace].update(enums_to_add)
    
    def _add_dependencies_for_schema(
        self,
        namespace: str,
        schema: Schema,
        schema_info: SchemaInfo
    ) -> bool:

        changed = False

        for field in schema._declared_fields.values():
            nested_schema = None

            if isinstance(field, fields.Nested):
                nested_schema = field.nested
            
            elif isinstance(field, fields.List):
                if isinstance(field.inner, fields.Nested):
                    nested_schema = field.inner.nested
            
            if nested_schema is not None:
                nested_schema_info = self.schemas[namespace][nested_schema]
                
                if not nested_schema in schema_info.nests:
                    changed = True
                    schema_info.nests.add(nested_schema)
                
                if not schema in nested_schema_info.nested_by:
                    changed = True
                    nested_schema_info.nested_by.add(schema)

                for deeply_nested_schema in nested_schema_info.nests:
                    if not deeply_nested_schema in schema_info.nests:
                        changed = True
                        schema_info.nests.add(deeply_nested_schema)
                    
                    deeply_nested_schema_info = self.schemas[namespace][deeply_nested_schema]
                    if not schema in deeply_nested_schema_info.nested_by:
                        changed = True
                        deeply_nested_schema_info.nested_by.add(schema)
        
        return changed
    
    def _add_dependencies_for_schemas(self) -> None:
        while True:
            changed = False
            for namespace, schema_list in self.schemas.items():
                for schema, schema_info in schema_list.items():
                    _changed = self._add_dependencies_for_schema(
                        namespace,
                        schema,
                        schema_info
                    )

                    if _changed:
                        changed = True
            
            if not changed:
                break
    
    def _add_ordering_to_schemas(self) -> None:
        while True:
            changed = False
            
            for namespace, schema_list in self.schemas.items():
                schemas = sorted(list(schema_list.values()), key=lambda e: len(e.nests))

                for schema_info in schemas:
                    for nested_by in schema_info.nested_by:
                        nested_by_schema_info = self.schemas[namespace][nested_by]
                        nested_by_schema_info.ordering = max(
                            nested_by_schema_info.ordering,
                            schema_info.ordering + 1
                        )
            
            if not changed:
                break

    @staticmethod
    def _get_schema_export_name(
        schema: Schema,
        strip_schema_keyword: bool
    ) -> str:
        """ Returns a name for the exportable struct. Optionally strips Schema from the name

            Examples: ::

                class TestSchema(Schema):
                    pass

                _get_schema_export_name(
                    TestSchema,
                    strip_schema_keyword=True
                ) 
                > 'Test'

                _get_schema_export_name(
                    TestSchema,
                    strip_schema_keyword=False
                )
                > 'TestSchema'
        """
        name = schema.__name__

        if strip_schema_keyword:
            name = name.replace('Schema', '')
        
        return name
    
    @staticmethod
    @property
    @abstractmethod
    def _mappings() -> Dict[fields.Field, Mapping]:
        pass

    @abstractmethod
    def _export_field(
        self,
        ma_field: fields.Field,
        strip_schema_keyword: bool
    ) -> Tuple[str, str]:
        pass
    
    @staticmethod
    @abstractmethod 
    def _export_schema(
        schema: Schema,
        strip_schema_keyword: bool,
        include_dump_only: bool,
        include_load_only: bool
    ) -> str:
        pass

    @staticmethod
    @abstractmethod
    def _export_enum(enum: Enum):
        pass

    def export_namespaces(
        self,
        namespaces: List[str],
        strip_schema_keyword: bool,
        include_dump_only: bool,
        include_load_only: bool
    ) -> str:
        pass
