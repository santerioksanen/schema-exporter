from marshmallow import Schema
from enum import Enum

from pathlib import Path

from .types import SchemaInfo
from .languages import Typescript
from .languages.abstract import AbstractLanguage
from .type_mappings import Languages
from .type_mappings import type_mappings

from .ts_utils import _get_ts_mapping

from typing import List, Dict, Type


__schemas = dict()
__enums = dict()
__languages: Dict[str, Type[AbstractLanguage]] = dict()


def _register_language(language: Type[AbstractLanguage]):
    __languages[language.__name__.lower()] = language


# Register languages
_register_language(Typescript)


def export_schema(
        namespace: str = 'default',
        **kwargs
):
    if not isinstance(namespace, str):
        raise ValueError('Namespace should be a string containing one or more comma separated values')

    namespace = namespace.split(',')

    def decorate(cls):
        if issubclass(cls, Schema):
            for n in namespace:
                if n not in __schemas:
                    __schemas[n] = dict()

                __schemas[n][cls] = SchemaInfo()
        elif issubclass(cls, Enum):
            for n in namespace:
                if n not in __enums:
                    __enums[n] = set()

                __enums[n].add(cls)

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

    lng_class = __languages[language]
    exporter = lng_class(
        schemas=__schemas,
        enums=__enums,
        strip_schema_keyword=strip_schema_keyword,
        expand_nested=expand_nested,
        ordered_output=ordered_output
    )

    return exporter.export_namespace(
        namespace=namespace,
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

