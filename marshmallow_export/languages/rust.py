from enum import Enum
from typing import Any, Dict, List, Type

from marshmallow_export.types import (
    EnumInfo,
    Mapping,
    ParsedField,
    ParsedSchema,
    PythonDatatypes,
)

from .base_language import BaseLanguage

DEFAULT_ENUM_DERIVES = [
    Mapping(mapping="Debug"),
    Mapping(mapping="Clone"),
    Mapping(mapping="Copy"),
    Mapping(mapping="Serialize", imports={"serde_derive": ["Serialize"]}),
    Mapping(mapping="Deserialize", imports={"serde_derive": ["Deserialize"]}),
    Mapping(mapping="EnumString", imports={"strum_macros": ["EnumString"]}),
    Mapping(mapping="Display", imports={"strum_macros": ["Display"]}),
    Mapping(mapping="AsStaticStr", imports={"strum_macros": ["AsStaticStr"]}),
]

DEFAULT_SCHEMA_DERIVES = [
    Mapping(mapping="Debug"),
    Mapping(mapping="Clone"),
    Mapping(mapping="Serialize", imports={"serde_derive": ["Serialize"]}),
    Mapping(mapping="Deserialize", imports={"serde_derive": ["Deserialize"]}),
]


class Types(Enum):
    BOOL = Mapping(mapping="bool")
    INTEGER = Mapping(mapping="i64")
    FLOAT = Mapping(mapping="f64")
    DECIMAL = Mapping(mapping="Decimal", imports={"rust_decimal": ["Decimal"]})
    STRING = Mapping(mapping="String")
    DATE_TIME_AWARE = Mapping(
        mapping="DateTime<Utc>", imports={"chrono": ["DateTime", "Utc"]}
    )
    UUID = Mapping(mapping="Uuid", imports={"uuid": ["Uuid"]})


type_mappings: dict[PythonDatatypes, Mapping] = {
    PythonDatatypes.BOOL: Types.BOOL.value,
    PythonDatatypes.CONSTANT: Types.STRING.value,
    PythonDatatypes.DATETIME: Types.DATE_TIME_AWARE.value,
    PythonDatatypes.DECIMAL: Types.DECIMAL.value,
    # PythonDatatypes.DICT: None,
    PythonDatatypes.EMAIL: Types.STRING.value,
    # PythonDatatypes.FIELD: None,
    PythonDatatypes.FLOAT: Types.FLOAT.value,
    # PythonDatatypes.FUNCTION: None,
    PythonDatatypes.INT: Types.INTEGER.value,
    # PythonDatatypes.MAPPING: None,
    # PythonDatatypes.METHOD: None,
    PythonDatatypes.STRING: Types.STRING.value,
    # PythonDatatypes.TIMEDELTA: None,
    PythonDatatypes.URL: Types.STRING.value,
    PythonDatatypes.UUID: Types.UUID.value,
}


class Rust(BaseLanguage):
    @property
    def type_mappings(self) -> Dict[PythonDatatypes, Mapping]:
        return type_mappings

    @staticmethod
    def get_default_kwargs() -> Dict[str, Any]:
        return {
            "rust_enum_derives": DEFAULT_ENUM_DERIVES,
            "rust_schema_derives": DEFAULT_SCHEMA_DERIVES,
        }

    @staticmethod
    def _format_enum_field(field_name: str, value: Enum) -> str:
        return f"    {field_name},"

    @staticmethod
    def _format_enum(e: Type[Enum], enum_fields: List[str], enum_info: EnumInfo) -> str:
        enum_fields_formatted = "\n".join(enum_fields)
        derives = ""
        if (
            "rust_enum_derives" in enum_info.kwargs
            and len(enum_info.kwargs["rust_enum_derives"]) > 0
        ):
            derive_str = sorted(
                [m.mapping for m in enum_info.kwargs["rust_enum_derives"]],
                key=lambda e: e.lower(),
            )
            derives = f'#[derive({", ".join([m for m in derive_str])})]\n'

        return f"{derives}pub enum {e.__name__} {{\n{enum_fields_formatted}\n}}\n"

    def format_header(self, include_dump_only: bool, include_load_only: bool) -> str:
        imports: dict[str, set[str]] = dict()
        for _, enum_info in self.enums:
            if "rust_enum_derives" in enum_info.kwargs:
                for rust_derive in enum_info.kwargs["rust_enum_derives"]:
                    if isinstance(rust_derive.imports, dict):
                        for lib, imp in rust_derive.imports.items():
                            if lib not in imports:
                                imports[lib] = set()

                            imports[lib].update(imp)

        for schema in self.schemas:
            if "rust_schema_derives" in schema.kwargs:
                for rust_derive in schema.kwargs["rust_schema_derives"]:
                    if isinstance(rust_derive.imports, dict):
                        for lib, imp in rust_derive.imports.items():
                            if lib not in imports:
                                imports[lib] = set()

                            imports[lib].update(imp)

            for field in schema.fields:
                if not include_dump_only and field.dump_only:
                    continue

                if not include_load_only and field.load_only:
                    continue

                if field.python_datatype not in self.type_mappings:
                    continue

                export_type = self.type_mappings[field.python_datatype]
                if not isinstance(export_type.imports, dict):
                    continue

                for lib, imp in export_type.imports.items():
                    if lib not in imports:
                        imports[lib] = set()

                    imports[lib].update(imp)

        imports_sorted = sorted(list(imports.items()), key=lambda e: e[0].lower())
        formatted = list()
        for lib, imp in imports_sorted:
            imp = sorted(imp, key=lambda e: e.lower())
            formatted_imp = ""
            if len(imp) > 1:
                formatted_imp = "{"

            formatted_imp += ", ".join(imp)
            if len(imp) > 1:
                formatted_imp += "}"

            formatted.append(f"use {lib}::{formatted_imp};")

        return "\n".join(formatted) + "\n"

    def _format_schema_field(
        self,
        field: ParsedField,
    ) -> str:
        export_type = self.map_schema_field(field)
        field_name = field.field_name

        if isinstance(export_type, Mapping):
            export_type = export_type.mapping

        if field.many:
            export_type = f"Vec<{export_type}>"

        if field.allow_none or not field.required:
            export_type = f"Option<{export_type}>"

        return f"    pub {field_name}: {export_type},"

    def _format_schema(
        self, schema: ParsedSchema, schema_fields: List[ParsedField]
    ) -> str:
        schema_fields_formatted = "\n".join(
            [self._format_schema_field(fld) for fld in schema_fields]
        )
        derives = ""

        if (
            "rust_schema_derives" in schema.kwargs
            and len(schema.kwargs["rust_schema_derives"]) > 0
        ):
            derive_str = sorted(
                [m.mapping for m in schema.kwargs["rust_schema_derives"]],
                key=lambda e: e.lower(),
            )
            derives = f'#[derive({", ".join([m for m in derive_str])})]\n'

        return f"{derives}pub struct {schema.name} {{\n{schema_fields_formatted}\n}}\n"
