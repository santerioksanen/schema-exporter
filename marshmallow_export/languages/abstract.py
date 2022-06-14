from abc import ABCMeta, abstractmethod

from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from enum import Enum, EnumMeta

from typing import Tuple, Dict, List, Set, Any

from marshmallow_export.types import SchemaInfo, EnumInfo


class AbstractLanguage(metaclass=ABCMeta):

    def __init__(
            self,
            schemas: Dict[str, Dict[Schema, SchemaInfo]],
            enums: Dict[str, Dict[Enum, EnumInfo]],
            strip_schema_keyword: bool = True,
            expand_nested: bool = True,
            ordered_output: bool = True,
    ) -> None:

        self.schemas = schemas
        self.enums = enums
        self.strip_schema_keyword = strip_schema_keyword
        self.imports = dict()

        if expand_nested:
            self._expand_nested()

        if ordered_output:
            self._add_dependencies_for_schemas()
            self._add_ordering_to_schemas()

    @staticmethod
    @abstractmethod
    def get_default_kwargs() -> Dict[str, Any]:
        pass

    def _expand_schema(
            self,
            namespace: str,
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
                if field.nested not in self.schemas[namespace]:
                    schemas_to_add.add(field.nested)
                    recurse_field = field.nested

            elif isinstance(field, fields.List):
                if isinstance(field.inner, fields.Nested):
                    if field.inner.nested not in self.schemas[namespace]:
                        schemas_to_add.add(field.inner.nested)
                        recurse_field = field.inner.nested
                elif isinstance(field.inner, EnumField):
                    if namespace not in self.enums or field.inner not in self.enums[namespace]:
                        enums_to_add.add(field.inner.enum)

            elif isinstance(field, EnumField):
                if namespace not in self.enums or field not in self.enums[namespace]:
                    enums_to_add.add(field.enum)

            if recurse_field is not None:
                tmp = self._expand_schema(namespace, recurse_field)
                schemas_to_add.update(tmp[0])
                enums_to_add.update(tmp[1])

        return schemas_to_add, enums_to_add

    def _expand_nested(self) -> None:
        """ Iterates through all schemas, and adds nested schemas and enums
            to be included in formatted output
        """
        for namespace, schema_list in self.schemas.items():
            for schema in schema_list.keys():
                schemas_to_add, enums_to_add = self._expand_schema(namespace, schema)

            for schema in schemas_to_add:
                if schema not in self.schemas[namespace]:
                    self.schemas[namespace][schema] = SchemaInfo()

            if namespace not in self.enums:
                self.enums[namespace] = dict()

            for en in enums_to_add:
                self.enums[namespace][en] = EnumInfo()

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

    def get_schema_export_name(
            self,
            schema: Schema
    ) -> str:
        """ Returns a name for the exportable struct. Optionally strips Schema from the name

            Examples: ::

                class TestSchema(Schema):
                    pass

                get_schema_export_name(
                    TestSchema,
                    strip_schema_keyword=True
                ) 
                > 'Test'

                get_schema_export_name(
                    TestSchema,
                    strip_schema_keyword=False
                )
                > 'TestSchema'
        """
        name = schema.__name__

        if self.strip_schema_keyword:
            name = name.replace('Schema', '')

        return name

    @staticmethod
    @abstractmethod
    def _format_enum_field(field_name: str, value: Enum) -> str:
        pass

    @staticmethod
    @abstractmethod
    def _format_enum(e: EnumMeta, enum_fields: List[str], enum_info: EnumInfo) -> str:
        pass

    @abstractmethod
    def _export_field(
            self,
            field_name: str,
            ma_field: fields.Field,
    ) -> Tuple[str, str]:
        pass

    @abstractmethod
    def _export_schema(
            self,
            schema: Schema,
            include_dump_only: bool,
            include_load_only: bool
    ) -> str:
        pass

    def format_enum(self, e: EnumMeta, enum_info: EnumInfo) -> str:
        enum_fields = [self._format_enum_field(
            field_name,
            value
        ) for field_name, value in e._member_map_.items()]

        return self._format_enum(e, enum_fields, enum_info)

    @abstractmethod
    def _export_header(self, namespace: str) -> str:
        pass

    def export_namespace(
            self,
            namespace: str,
            include_dump_only: bool,
            include_load_only: bool
    ) -> str:

        schemas = self.schemas[namespace]
        enums: List[Enum] = sorted(list(self.enums[namespace].items()), key=lambda e: e[0].__name__)

        # Sort schemas first by name, second by ordering
        schemas = list(schemas.items())
        schemas.sort(key=lambda e: self.get_schema_export_name(e[0]))
        schemas.sort(key=lambda e: e[1].ordering)

        header = self._export_header(namespace)
        output = [header] if len(header) > 0 else list()
        output += [self.format_enum(e, enum_info) for e, enum_info in enums]
        output += [self._export_schema(
            schema=schema[0],
            include_dump_only=include_dump_only,
            include_load_only=include_load_only
        ) for schema in schemas]

        return '\n'.join(output)
