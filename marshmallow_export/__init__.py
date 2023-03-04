from __future__ import annotations

from collections import defaultdict
from enum import Enum, EnumMeta
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, List, Type

from .sorting import add_ordering_to_schemas, mark_nested_schemas
from .languages import Rust, Typescript
from .languages.base_language import BaseLanguage
from .types import EnumInfo, SchemaInfo

if TYPE_CHECKING:
    from marshmallow import Schema
    from rest_framework.serializers import Serializer


__schemas = defaultdict(lambda: dict())
__enums = defaultdict(lambda: dict())
__serializers = defaultdict(lambda: dict())
__languages: Dict[str, Type[BaseLanguage]] = dict()
__kwargs_defaults = dict()


def _register_language(language: Type[BaseLanguage]):
    __languages[language.__name__.lower()] = language
    lng_kwargs = language.get_default_kwargs()
    for key, value in lng_kwargs.items():
        __kwargs_defaults[key] = value


# Register languages
_register_language(Typescript)
_register_language(Rust)


def _add_schema(
    namespaces: List[str], cls: Type[Schema], parsed_args: Dict[str, Any]
) -> None:
    for n in namespaces:
        __schemas[n][cls] = SchemaInfo(kwargs=parsed_args)


def _add_serializer(
    namespaces: List[str], cls: Type[Serializer], parsed_args: Dict[str, Any]
) -> None:
    for n in namespaces:
        __serializers[n][cls()] = SchemaInfo(kwargs=parsed_args)


def _add_enum(
    namespaces: List[str], cls: EnumMeta, parsed_args: Dict[str, Any]
) -> None:
    for n in namespaces:
        __enums[n][cls] = EnumInfo(kwargs=parsed_args)


def _parse_kwargs(kwargs: dict) -> dict:
    for kwarg in kwargs:
        if kwarg not in __kwargs_defaults:
            raise ValueError(f"Provided unknown keyword argument: {kwarg}")

    parsed_args = dict()
    for key, value in __kwargs_defaults.items():
        parsed_args[key] = value

    for key, value in kwargs:
        parsed_args[key] = value

    return parsed_args


def _validate_and_split_namespace(namespace: str) -> list[str]:
    if not isinstance(namespace, str):
        raise ValueError(
            "Namespace should be a string containing one or more comma separated values"
        )
    return namespace.split(",")


def export_schema(namespace: str = "default", **kwargs):
    """A simple wrapper to register a Marshmallow schema to be exported.
    With default export configurations the export functions adds
    all nested schemas to the export as well.

    Supports providing namespaces, which may be used during export
    phase to limit number of types exported.
    """
    from marshmallow import Schema

    parsed_args = _parse_kwargs(kwargs)
    namespaces = _validate_and_split_namespace(namespace)

    def decorate(cls):
        if not issubclass(cls, Schema):
            raise ValueError(
                f"Trying to export schema of type: {type(cls)}, which is not supported"
            )

        _add_schema(namespaces, cls, parsed_args)

        return cls

    return decorate


def export_enum(namespce: str = "default", **kwargs):
    """A simple wrapper to register an Enum to be exported.

    Supports providing namespaces, which may be used during export
    phase to limit number of types exported.
    """
    parsed_args = _parse_kwargs(kwargs)
    namespaces = _validate_and_split_namespace(namespce)

    def decorate(cls):
        if not issubclass(cls, Enum):
            raise ValueError(
                f"Trying to export enum, which is of type: {type(cls)}. Should be Enum"
            )
        _add_enum(namespaces, cls, parsed_args)
        return cls

    return decorate


def export_serializer(namespace: str = "default", **kwargs):
    """A simple wrapper to register a DRF serializer to be exported.
    With default export configurations the export functions adds
    all nested serializers to the export as well.

    Supports providing namespaces, which may be used during export
    phase to limit number of types exported.
    """
    from rest_framework.serializers import Serializer

    parsed_args = _parse_kwargs(kwargs)
    namespaces = _validate_and_split_namespace(namespace)

    def decorate(cls):
        if not issubclass(cls, Serializer):
            raise ValueError(
                f"Trying to export serializer of type: {type(cls)}, which is not supported"
            )

        _add_serializer(namespaces, cls, parsed_args)

    return decorate


def _get_export(
    language: str,
    namespace: str,
    include_dump_only: bool,
    include_load_only: bool,
    strip_schema_keyword: bool,
    expand_nested: bool,
    ordered_output: bool,
) -> str:
    schemas = []
    enums = {}
    if namespace in __enums:
        enums = __enums[namespace]

    # Parse schemas
    if namespace in __schemas and len(__schemas[namespace].keys()):
        from .parsers.marshmallow_parser import MarshmallowParser

        parser = MarshmallowParser(
            default_info_kwargs=__kwargs_defaults,
            strip_schema_from_name=strip_schema_keyword,
        )
        if namespace in __schemas:
            for schema, schema_info in __schemas[namespace].items():
                parser.parse_and_add_schema(schema, schema_info.kwargs)

        if expand_nested:
            parser.parse_nested()

        schemas += list(parser.schemas.values())
        enums.update(parser.enums)

    # Parse serializers
    if namespace in __serializers and len(__serializers[namespace].keys()):
        from .parsers.drf_parser import DRFParser

        parser = DRFParser(
            default_info_kwargs=__kwargs_defaults,
            strip_schema_from_name=strip_schema_keyword,
        )
        if namespace in __serializers:
            for serializer, schema_info in __serializers[namespace].items():
                parser.parse_and_add_schema(serializer, schema_info.kwargs)

        if expand_nested:
            parser.parse_nested()

        schemas += list(parser.schemas.values())
        enums.update(parser.enums)

    # Convert enums to list:
    enums = list(enums.items())

    if ordered_output:
        mark_nested_schemas(schemas)
        add_ordering_to_schemas(schemas)
        schemas.sort(key=lambda e: e.name.lower())
        schemas.sort(key=lambda e: e.ordering)
        enums.sort(key=lambda e: e[0].__name__.lower())

    lng_class = __languages[language]
    exporter = lng_class(schemas=schemas, enums=enums)

    # Export schemas
    return exporter.export(
        include_dump_only=include_dump_only, include_load_only=include_load_only
    )


def export_mappings(
    export_to: Path,
    language: str,
    namespace: str = "default",
    include_dump_only: bool = True,
    include_load_only: bool = True,
    strip_schema_keyword: bool = True,
    expand_nested: bool = True,
    ordered_output: bool = True,
):
    if language not in __languages:
        raise NotImplementedError(
            f'Language {language} not implemented, supported are: {", ".join([l for l in __languages.keys()])}'
        )

    if not isinstance(namespace, str):
        raise ValueError(f"namespace must be of type str, {type(namespace)} provided")

    if not isinstance(export_to, Path):
        raise ValueError(
            f"export_to must be a Path instance, {type(export_to)} provided"
        )

    if not isinstance(export_to, Path):
        raise ValueError(f"Export to should be string or path, was: {type(export_to)}")

    exp = _get_export(
        language=language,
        namespace=namespace,
        include_dump_only=include_dump_only,
        include_load_only=include_load_only,
        strip_schema_keyword=strip_schema_keyword,
        expand_nested=expand_nested,
        ordered_output=ordered_output,
    )

    with open(export_to, "w") as f:
        f.write(exp)
