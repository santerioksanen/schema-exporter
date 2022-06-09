from marshmallow import Schema

from pathlib import Path

from .type_mappings import Languages
from .type_mappings import type_mappings

from .ts_utils import _get_ts_mapping

from typing import List


__schemas = dict()
__enums = dict()


def export_schema(
        namespace: str = 'default'
):
    if isinstance(namespace, str):
        namespace = [namespace]

    if not isinstance(namespace, list):
        raise ValueError('Namespace should be string or list of strings')

    def decorate(cls):
        if issubclass(cls, Schema):
            for n in namespace:
                if n not in __schemas:
                    __schemas[n] = list()

                __schemas[n].append(cls)

    return decorate


def _get_export(
        language: Languages,
        namespaces: List[str],
        include_dump_only: bool,
        include_load_only: bool,
        strip_schema_keyword: bool,
):
    schemas = list()
    for n in namespaces:
        schemas += __schemas[n]

    if language == Languages.TS:
        output = [_get_ts_mapping(
            schema=schema,
            strip_schema_keyword=strip_schema_keyword,
            include_load_only=include_load_only,
            include_dump_only=include_dump_only,
        ) for schema in schemas]

    return '\n'.join(output)


def export_mappings(
        export_to: Path,
        language: str,
        namespace: str = 'default',
        include_dump_only: bool = True,
        include_load_only: bool = True,
        strip_schema_keyword: bool = True,
):
    try:
        language = Languages[language]
    except KeyError as e:
        raise NotImplementedError(
            f'Language {e} not implemented, supported are: {", ".join([l.value for l in Languages])}'
        )

    if isinstance(export_to, str):
        export_to = Path(export_to)

    if isinstance(namespace, str):
        namespace = [namespace]

    if not isinstance(export_to, Path):
        raise ValueError(f'Export to should be string or path, was: {type(export_to)}')

    with open(export_to, 'w') as f:
        f.write(
            _get_export(
                language=language,
                namespaces=namespace,
                include_dump_only=include_dump_only,
                include_load_only=include_load_only,
                strip_schema_keyword=strip_schema_keyword,
            )
        )

