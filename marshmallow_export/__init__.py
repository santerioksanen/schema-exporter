from rest_framework.serializers import ModelSerializer
from marshmallow import Schema
from enum import Enum, EnumMeta

from pathlib import Path

from .types import EnumInfo, SchemaInfo
from .languages import Rust, Typescript
from .languages.abstract import AbstractLanguage
from ._parsers import _MarshmallowParser
from ._sorting import _mark_nested_schemas, _add_ordering_to_schemas

from typing import Dict, Type, List, Any


__schemas = dict()
__enums = dict()
__serializers = dict()
__languages: Dict[str, Type[AbstractLanguage]] = dict()
__kwargs_defaults = dict()


def _register_language(language: Type[AbstractLanguage]):
    __languages[language.__name__.lower()] = language
    lng_kwargs = language.get_default_kwargs()
    for key, value in lng_kwargs.items():
        __kwargs_defaults[key] = value


# Register languages
_register_language(Typescript)
_register_language(Rust)


def _add_schema(
        namespaces: List[str],
        cls: Type[Schema],
        parsed_args: Dict[str, Any]
) -> None:
    for n in namespaces:
        if n not in __schemas:
            __schemas[n] = dict()

        __schemas[n][cls] = SchemaInfo(kwargs=parsed_args)


def _add_serializer(
        namespaces: List[str],
        cls: Type[ModelSerializer],
        parsed_args: Dict[str, Any]
) -> None:
    for n in namespaces:
        if n not in __schemas:
            __schemas[n] = dict()
        
        __serializers[n][cls] = SchemaInfo(kwargs=parsed_args)


def _add_enum(namespaces: List[str], cls: EnumMeta, parsed_args: Dict[str, Any]) -> None:
    for n in namespaces:
        if n not in __enums:
            __enums[n] = dict()

        __enums[n][cls] = EnumInfo(kwargs=parsed_args)


def export_schema(
        namespace: str = 'default',
        **kwargs
):
    for kwarg in kwargs:
        if kwarg not in __kwargs_defaults:
            raise ValueError(f'Provided unknown keyword argument: {kwarg}')

    parsed_args = dict()
    for key, value in __kwargs_defaults.items():
        parsed_args[key] = value

    for key, value in kwargs:
        parsed_args[key] = value

    if not isinstance(namespace, str):
        raise ValueError('Namespace should be a string containing one or more comma separated values')

    namespaces = namespace.split(',')

    def decorate(cls):
        if issubclass(cls, Schema):
            _add_schema(namespaces, cls, parsed_args)
        elif issubclass(cls, ModelSerializer):
            _add_serializer(namespaces, cls, parsed_args)
        elif issubclass(cls, Enum):
            _add_enum(namespaces, cls, parsed_args)

        return cls

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

    # Parse schemas
    parser = _MarshmallowParser(
        default_info_kwargs=__kwargs_defaults,
        strip_schema_from_name=strip_schema_keyword
    )
    if namespace in __schemas:
        for schema, schema_info in __schemas[namespace].items():
            parser.parse_and_add_schema(schema, schema_info.kwargs)
    
    if namespace in __enums:
        for en, en_info in __enums[namespace].items():
            parser.add_enum(en, en_info.kwargs)
    if expand_nested:
        parser.parse_nested()

    schemas = list(parser.schemas.values())
    enums = list(parser.enums.values())

    if ordered_output:
        _mark_nested_schemas(schemas)
        _add_ordering_to_schemas(schemas)
        schemas.sort(key=lambda e: e.name.lower())
        schemas.sort(key=lambda e: e.ordering)
        enums.sort(key=lambda e: e[0].__name__.lower())
    
    lng_class = __languages[language]
    exporter = lng_class(
        schemas=schemas,
        enums=enums
    )

    # Export schemas
    return exporter.export(
        include_dump_only=include_dump_only,
        include_load_only=include_load_only
    )


def export_mappings(
        export_to: Path,
        language: str,
        namespace: str = 'default',
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
        raise ValueError(
            f'namespace must be of type str, {type(namespace)} provided'
        )

    if not isinstance(export_to, Path):
        raise ValueError(
            f'export_to must be a Path instance, {type(export_to)} provided'
        )

    if not isinstance(export_to, Path):
        raise ValueError(f'Export to should be string or path, was: {type(export_to)}')

    exp = _get_export(
        language=language,
        namespace=namespace,
        include_dump_only=include_dump_only,
        include_load_only=include_load_only,
        strip_schema_keyword=strip_schema_keyword,
        expand_nested=expand_nested,
        ordered_output=ordered_output
    )

    with open(export_to, 'w') as f:
        f.write(exp)
