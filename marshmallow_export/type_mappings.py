import enum

from dataclasses import dataclass
from marshmallow import fields

from typing import Dict
from typing import List


@dataclass
class RustMapping:
    """ A dataclass containing mapping information to autogenerate Rust files
    """
    mapping: str
    requires: Dict[str, List[str]]


class Languages(enum.Enum):
    TS = 'ts'
    RUST = 'rust'


class TsTypes(enum.Enum):
    BOOL = 'boolean'
    NUMBER = 'number'
    STRING = 'string'
    DATE = 'Date'
    OBJECT = 'object'
    ANY = 'any'


class RustTypes(enum.Enum):
    BOOL = 'bool'
    INTEGER = 'i64'
    FLOAT = 'f64'
    DECIMAL = RustMapping(mapping='Decimal', requires={'rust_decimal': ['Decimal']})
    STRING = 'String'
    DATE_AWARE = RustMapping(mapping='DateTime<Utc>', requires={'chrono': ['DateTime', 'Utc']})
    DATE_NAIVE = RustMapping(mapping='NaiveDateTime', requires={'chrono': ['NaiveDateTime']})
    UUID = RustMapping(mapping='UUID', requires={'uuid': ['UUID']})


NOT_IMPLEMENTED_TYPE = None


type_mappings = {
    fields.Bool:
        {
            Languages.TS: TsTypes.BOOL,
            Languages.RUST: RustTypes.BOOL,
        },
    fields.Boolean:
        {
            Languages.TS: TsTypes.BOOL,
            Languages.RUST: RustTypes.BOOL,
        },
    fields.Constant:
        {
            Languages.TS: TsTypes.STRING,
            Languages.RUST: RustTypes.STRING,
        },
    fields.DateTime:
        {
            Languages.TS: TsTypes.DATE,
            Languages.RUST: RustTypes.DATE_AWARE,
        },
    fields.Decimal:
        {
            Languages.TS: TsTypes.NUMBER,
            Languages.RUST: RustTypes.DECIMAL,
        },
    fields.Dict:
        {
            Languages.TS: TsTypes.OBJECT,
            Languages.RUST: NOT_IMPLEMENTED_TYPE,
        },
    fields.Email:
        {
            Languages.TS: TsTypes.STRING,
            Languages.RUST: RustTypes.STRING,
        },
    fields.Field:
        {
            Languages.TS: TsTypes.ANY,
            Languages.RUST: NOT_IMPLEMENTED_TYPE,
        },
    fields.Float:
        {
            Languages.TS: TsTypes.NUMBER,
            Languages.RUST: RustTypes.FLOAT,
        },
    fields.Function:
        {
            Languages.TS: TsTypes.ANY,
            Languages.RUST: NOT_IMPLEMENTED_TYPE,
        },
    fields.Int:
        {
            Languages.TS: TsTypes.NUMBER,
            Languages.RUST: RustTypes.INTEGER,
        },
    fields.Integer:
        {
            Languages.TS: TsTypes.NUMBER,
            Languages.RUST: RustTypes.INTEGER,
        },
    fields.List:
        {
            Languages.TS: f'{TsTypes.ANY}[]',
            Languages.RUST: NOT_IMPLEMENTED_TYPE,
        },
    fields.Mapping:
        {
            Languages.TS: TsTypes.ANY,
            Languages.RUST: NOT_IMPLEMENTED_TYPE,
        },
    fields.Method:
        {
            Languages.TS: TsTypes.ANY,
            Languages.RUST: NOT_IMPLEMENTED_TYPE,
        },
    fields.Number:
        {
            Languages.TS: TsTypes.NUMBER,
            Languages.RUST: RustTypes.FLOAT,
        },
    fields.Raw:
        {
            Languages.TS: TsTypes.ANY,
            Languages.RUST: NOT_IMPLEMENTED_TYPE,
        },
    fields.Str:
        {
            Languages.TS: TsTypes.STRING,
            Languages.RUST: RustTypes.STRING,
        },
    fields.String:
        {
            Languages.TS: TsTypes.STRING,
            Languages.RUST: RustTypes.STRING,
        },
    fields.TimeDelta:
        {
            Languages.TS: TsTypes.ANY,
            Languages.RUST: NOT_IMPLEMENTED_TYPE,
        },
    fields.Url:
        {
            Languages.TS: TsTypes.STRING,
            Languages.RUST: RustTypes.STRING,
        },
    fields.UUID:
        {
            Languages.TS: TsTypes.STRING,
            Languages.RUST: RustTypes.UUID,
        }
}
