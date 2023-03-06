![tests](https://github.com/santerioksanen/marshmallow-export/actions/workflows/run_tests.yml/badge.svg?branch=main)

# Marshmallow-export
_Generates Typescript and Rust interfaces/structs from Marshmallow schemas and DRF serializers_

## Installation
Install with `pip install git+https://github.com/santerioksanen/schema-exporter.git`

## Usage
## Basic
Decorate marshmallow-schemas to export with `@export_marshmallow_schema()`. With default settings all nested schemas and Enum fields are automatically loaded as well. Furthermore, with default settings Schema is stripped from the schema name.

For Django Rest Framework serializers use the `@export_drf_serializer()` decorator in similar fashion. Here as well the Serializer is stripped from the serializer name.

And to export plain Enums, you can use the `@export_enum()` decorator similarly.

Generate interfaces/structs with `export_mappings(path: Path, language: str = ("typescript"|"rust"))`

Please note that with default export settings all nested schemas/serializers/enums are added to the export as well. So no need to explicitly add the decorator to any leaf nodes.

## DRF caveats
* DRF ChoiceFields are treated as Enums
* Same goes for MultipleChoiceFields, which are treated as list of Enums

# DRF example
_serializers.py_
```python
from rest_framework import serializers

from schema_exporter import export_drf_serializer

class LeafSerializer(serializers.Serializer):
    bool_1 = serializers.BooleanField()
    datetime_1 = serializers.DateTimeField()
    decimal_1 = serializers.DecimalField(decimal_places=2, max_digits=5)
    int_1 = serializers.IntegerField()


class LeafSerializer2(serializers.Serializer):
    datetime_1 = serializers.DateTimeField(required=False)
    integer_1 = serializers.IntegerField(required=False)
    many_1 = serializers.ListField(child=serializers.CharField())


class MiddleSerializer(serializers.Serializer):
    test_enum_1 = serializers.ChoiceField(choices=[("A", "a"), ("B", "b"), ("C", "c")])
    leaf_schema = LeafSerializer()


@export_drf_serializer(namespace="default")
class RootSerializer(serializers.Serializer):
    nested_leaf_1 = MiddleSerializer()
    nested_leaf_2 = MiddleSerializer(many=True)
    list_leaf_1 = MiddleSerializer(many=True)


@export_drf_serializer(namespace="default")
class RootSerializer2(serializers.Serializer):
    nested_leaf_1 = LeafSerializer2(
        required=True
    ) 
```
Django management command:
_export_serializers.py_
```python
from pathlib import Path
from django.core.management.base import BaseCommand
from schema_exporter import export_mappings


class Command(BaseCommand):
    help = "Exports serializers as typescript and rust"

    def handle(self, *args, **options):
        ts_export_to = Path.cwd() / "output.ts"
        rust_export_to = Path.cwd() / "output.rs"
        export_mappings(
            ts_export_to,
            "typescript"
        )
        export_mappings(
            rs_export_to,
            "rust"
        )
```

_output.ts_
```typescript
export enum TestEnum1 {
  A = "a",
  B = "b",
  C = "c",
}

export interface Leaf {
  bool_1: boolean;
  datetime_1: Date;
  decimal_1: number;
  int_1: number;
}

export interface Leaf2 {
  datetime_1?: Date;
  integer_1?: number;
  many_1: string[];
}

export interface Middle {
  test_enum_1: TestEnum1;
  leaf_schema: Leaf;
}

export interface Root2 {
  nested_leaf_1: Leaf2;
}

export interface Root {
  nested_leaf_1: Middle;
  nested_leaf_2: Middle[];
  list_leaf_1: Middle[];
}
```
_output.rs_
```rust
use chrono::{DateTime, Utc};
use rust_decimal::Decimal;
use serde_derive::{Deserialize, Serialize};
use strum_macros::{AsStaticStr, Display, EnumString};

#[derive(AsStaticStr, Clone, Copy, Debug, Deserialize, Display, EnumString, Serialize)]
pub enum TestEnum1 {
    A,
    B,
    C,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Leaf {
    pub bool_1: bool,
    pub datetime_1: DateTime<Utc>,
    pub decimal_1: Decimal,
    pub int_1: i64,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Leaf2 {
    pub datetime_1: Option<DateTime<Utc>>,
    pub integer_1: Option<i64>,
    pub many_1: Vec<String>,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Middle {
    pub test_enum_1: TestEnum1,
    pub leaf_schema: Leaf,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Root2 {
    pub nested_leaf_1: Leaf2,
}

#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Root {
    pub nested_leaf_1: Middle,
    pub nested_leaf_2: Vec<Middle>,
    pub list_leaf_1: Vec<Middle>,
}

```

# Marshmallow example
Example:
_schemas.py_

```python
from enum import Enum
from marshmallow import Schema, fields
from marshmallow_enum import EnumField
from schema_exporter import export_marshmallow_schema


class TestEnum(Enum):
    A = 'a'


class LeafSchema(Schema):
    enum_field = EnumField(TestEnum)
    integer_field = fields.Integer(dump_only=True)
    date_time_field = fields.DateTime(required=True)
    uuid_field = fields.UUID(required=True, dump_only=True)


@export_marshmallow_schema()
class RootSchema(Schema):
    leaf_field = fields.Nested(LeafSchema, required=True)
    leaf_list_1 = fields.Nested(LeafSchema, many=True, required=True)
    leaf_list_2 = fields.List(fields.Nested(LeafSchema))
```

_export_schemas.py_

```python
from schema_exporter import export_mappings
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
from schema_exporter import export_marshmallow_schema
from schema_exporter.types import Mapping


@export_marshmallow_schema(namespace='import,export',
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

# Implemented types for DRF fields:
| DRF field                                                 | Internal datatype          |
|-----------------------------------------------------------|----------------------------|
| serializers.BooleanField                                  | PythonDatatypes.BOOL       |
| serializers.CharField                                     | PythonDatatypes.STRING     |
| serializers.EmailField                                    | PythonDatatypes.EMAIL      |                               
| serializers.RegexField                                    | PythonDatatypes.STRING     |
| serializers.SlugField                                     | PythonDatatypes.STRING     | 
| serializers.URLField                                      | PythonDatatypes.URL        |                           
| serializers.UUIDField                                     | PythonDatatypes.UUID       |               
| serializers.FilePathField                                 | PythonDatatypes.UNDEFINED  |
| serializers.IPAddressField                                | PythonDatatypes.IP_ADDRESS |    
| serializers.IntegerField                                  | PythonDatatypes.INT        |
| serializers.FloatField                                    | PythonDatatypes.FLOAT      |             
| serializers.DecimalField                                  | PythonDatatypes.DECIMAL    |         
| serializers.DateTimeField                                 | PythonDatatypes.DATETIME   |       
| serializers.DateField                                     | PythonDatatypes.DATE       |     
| serializers.TimeField                                     | PythonDatatypes.TIME       |               
| serializers.DurationField                                 | PythonDatatypes.DURATION   |       
| serializers.FileField                                     | PythonDatatypes.UNDEFINED  |     
| serializers.ImageField                                    | PythonDatatypes.UNDEFINED  |         
| serializers.DictField                                     | PythonDatatypes.DICT       |       
| serializers.HStoreField                                   | PythonDatatypes.DICT       |             
| serializers.JSONField                                     | PythonDatatypes.JSON_FIELD |         
| serializers.SlugRelatedField                              | PythonDatatypes.STRING     |      
| serializers.StringRelatedField                            | PythonDatatypes.STRING     |    
| serializers.PrimaryKeyRelatedField                        | PythonDatatypes.INT        |   
| serializers.HyperlinkedRelatedField                       | PythonDatatypes.URL        |  
| serializers.HyperlinkedIdentityField                      | PythonDatatypes.URL        | 
| serializers.SerializerMethodField |  PythonDatatypes.STRING    | 
| serializers.HiddenField | PythonDatatypes.STRING |          

# Implemented types for Marshmallow fields:
| Marshmallow field               | Internal datatype              |
|---------------------------------|--------------------------------|
| fields.AwareDateTime            | PythonDatatypes.DATETIME       |
| fields.Bool                     | PythonDatatypes.BOOL           |
| fields.Constant                 | PythonDatatypes.CONSTANT       |            
| fields.Date                     | PythonDatatypes.DATE           |          
| fields.DateTime                 | PythonDatatypes.DATETIME       |            
| fields.Decimal                  | PythonDatatypes.DECIMAL        |          
| fields.Dict                     | PythonDatatypes.DICT           |                    
| fields.Email                    | PythonDatatypes.EMAIL          |                  
| fields.Float                    | PythonDatatypes.FLOAT          |                  
| fields.Function                 | PythonDatatypes.FUNCTION       |            
| fields.IP                       | PythonDatatypes.IP_ADDRESS     |                
| fields.IPInterface              | PythonDatatypes.IP_INTERFACE   |     
| fields.IPv4                     | PythonDatatypes.IPv4_ADDRESS   |            
| fields.IPv4Interface            | PythonDatatypes.IPv4_INTERFACE |
| fields.IPv6                     | PythonDatatypes.IPv6_ADDRESS   |            
| fields.IPv6Interface            | PythonDatatypes.IPv6_INTERFACE | 
| fields.Int                      | PythonDatatypes.INT            |                     
| fields.Integer                  | PythonDatatypes.INT            |                 
| fields.Mapping                  | PythonDatatypes.MAPPING        |        
| fields.Method                   | PythonDatatypes.METHOD         |      
| fields.NaiveDateTime            | PythonDatatypes.DATETIME       | 
| fields.Number                   | PythonDatatypes.FLOAT          |
| fields.Str                      | PythonDatatypes.STRING         |    
| fields.String                   | PythonDatatypes.STRING         | 
| fields.Time                     | PythonDatatypes.TIME           |    
| fields.URL                      | PythonDatatypes.URL            |  
| fields.UUID                     | PythonDatatypes.UUID           | 
| fields.Url |  PythonDatatypes.URL           |
| fields.TimeDelta | PythonDatatypes.TIMEDELTA |

# Typescript implementations
| Internal datatype                              | Typescript          |
|------------------------------------------------|---------------------|
| PythonDatatypes.BOOL                           | Types.BOOL.value    |
| PythonDatatypes.CONSTANT                       | Types.STRING.value  |       
| PythonDatatypes.DATETIME                       | Types.DATE.value    |     
| PythonDatatypes.DATE                           | Types.DATE.value    |             
| PythonDatatypes.TIME                           | Types.STRING.value  |           
| PythonDatatypes.DECIMAL                        | Types.NUMBER.value  |        
| PythonDatatypes.DICT                           | Types.OBJECT.value  |       
| PythonDatatypes.EMAIL                          | Types.STRING.value  |          
| PythonDatatypes.FIELD                          | Types.ANY.value     |        
| PythonDatatypes.FLOAT                          | Types.NUMBER.value  |          
| PythonDatatypes.FUNCTION                       | Types.ANY.value     |        
| PythonDatatypes.INT                            | Types.NUMBER.value  |            
| PythonDatatypes.MAPPING                        | Types.ANY.value     |          
| PythonDatatypes.METHOD                         | Types.ANY.value     |
| PythonDatatypes.STRING                         | Types.STRING.value  |         
| PythonDatatypes.TIMEDELTA                      | Types.NUMBER.value  |      
| PythonDatatypes.URL                            | Types.STRING.value  |    
| PythonDatatypes.UUID                           | Types.STRING.value  |           
| PythonDatatypes.IP_ADDRESS                     | Types.STRING.value  |     
| PythonDatatypes.IP_INTERFACE                   | Types.STRING.value  |   
| PythonDatatypes.IPv4_ADDRESS                   | Types.STRING.value  |  
| PythonDatatypes.IPv4_INTERFACE                 | Types.STRING.value  | 
| PythonDatatypes.IPv6_ADDRESS                   | Types.STRING.value  |
| PythonDatatypes.IPv6_INTERFACE                 | Types.STRING.value  | 
| PythonDatatypes.JSON_FIELD |  Types.OBJECT.value |
