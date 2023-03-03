![tests](https://github.com/santerioksanen/marshmallow-export/actions/workflows/run_tests.yml/badge.svg?branch=main)

# Marshmallow-export
_Generates Typescript and Rust interfaces/structs from Marshmallow schemas_

## Installation
Install with `pip install marshmallow-export`

## Usage
## Basic
Decorate schemas to export wit `@export_schema()`. With default settings all nested schemas and Enum fields are automatically loaded as well. Furthermore, with default settings Schema is stripped from the schema name.

Generate interfaces/structs with `export_mappings(path: Path, language: str = ("typescript"|"rust"))`

Example:
_schemas.py_
```python
from enum import Enum
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from marshmallow_export import export_schema


class TestEnum(Enum):
    A = 'a'


class LeafSchema(Schema):
    enum_field = EnumField(TestEnum)
    integer_field = fields.Integer(dump_only=True)
    date_time_field = fields.DateTime(required=True)
    uuid_field = fields.UUID(required=True, dump_only=True)


@export_schema()
class RootSchema(Schema):
    leaf_field = fields.Nested(LeafSchema, required=True)
    leaf_list_1 = fields.Nested(LeafSchema, many=True, required=True)
    leaf_list_2 = fields.List(fields.Nested(LeafSchema))
```

_export_schemas.py_
```python
from marshmallow_export import export_mappings
from pathlib import Path


path = Path().cwd() / 'output.ts'
export_mappings(path, 'typescript')
path = Path().cwd() / 'output.rs'
export_mappings(path, 'rust')
path = Path().cwd() / 'output_no_dump_only.ts'
export_mappings(path, 'typescript', include_load_only=False)
```

_output.ts_
```typescript
export enum TestEnum {
    A = 'a',
}

export interface Leaf {
    enum_field?: TestEnum;
    integer_field?: number;
    date_time_field: Date;
    uuid_field: String;
}

export interface Root {
    leaf_field: Leaf;
    leaf_list_1: Leaf[];
    leaf_lsit_2?: Leaf[];
}
```

_output.rs_
```rust
use chrono::{DateTime, Utc};
use serde::{Deserialize, Serialize};
use strum_macros::EnumString;
use uuid::Uuid;

#[derive(Clone, Copy, Debug, Deserialize, EnumString, Serialize)]
pub enum TestEnum {
    A,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub struct Leaf {
    pub enum_field: Option<TestEnum>,
    pub integer_field: Option<i64>,
    pub date_time_field: DateTime<Utc>,
    pub uuid_field: Uuid,
}

#[derive(Clone, Copy, Debug, Deserialize, Serialize)]
pub struct Root {
    pub leaf_field: Leaf,
    pub leaf_list_1: Vec<Leaf>,
    pub leaf_list_2: Option<Vec<Leaf>>,
}
```

_output_no_dump_only.ts_
```typescript
export enum TestEnum {
    A = 'a',
}

export interface Leaf {
    enum_field?: TestEnum;
    date_field: Date;
}

export interface Root {
    leaf_field: Leaf;
    leaf_list_1?: Leaf[];
    leaf_lsit_2?: Leaf[];
}
```

#### Default derives for Rust
##### Enum:
Clone, Copy, Debug, Deserialize, EnumString, Serialize
##### Struct:
Clone, Copy, Debug, Deserialize, Serialize

### Advanced
The `@export_schema()` decorator takes two optional arguments. Namespace may be provided for using different namespaces, for example @export_schema(namespace='default,dump'), and the schema will be added to default and dump namespaces. Keyword arguments may also be provided:

```python
from marshmallow import Schema, fields
from marshmallow_export import export_schema
from marshmallow_export.types import Mapping


@export_schema(namespace='import,export',
               rust_enum_derives=[
                   Mapping(mapping='Debug'),
                   Mapping(mapping='Serialize', imports={'serde': ['Clone']})
               ],
               rust_struct_derives=[
                   Mapping(mapping='Debug'),
                   Mapping(mapping='Deserialize', imports={'serde': ['Deserialize']})
               ])
class FooSchema(Schema):
    bar = fields.Integer()
```

Also the `export_mappings` function takes optional parameters:
* path: Path (required, path to save file in)
* language: str (required, language to export to)
* namespace: str = 'default', Schemas included in this namespace will be exported
* include_dump_only: bool = True, whether to include fields marked with dump_only=True
* include_load_only: bool = True, whether to include fields marked with load_only=True
* strip_schema_keyword: bool = True, whether to remove Schema from name of exported definitions
* expand_nested: bool = True, whether to add nested schemas and definitions in the exported file without being explicitly decorated
* ordered_output: bool = True, whether to sort output file so that all nested schemas are defined prior to root schema

## Contributing
* Clone project
* Create a virtual env and intall package in development mode
```concole
$ python3 -m venv env
$ source env/bin/activate
$ pip install -e .[dev]
```
* Test using test.py:
```console
$ python test.py
```