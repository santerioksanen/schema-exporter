from typing import Type
from marshmallow import fields

from marshmallow_export.types import PythonDatatypes


marshmallow_mappings: dict[Type[fields.Field], PythonDatatypes] = {
    fields.Bool: PythonDatatypes.BOOL,
    fields.Boolean: PythonDatatypes.BOOL,
    fields.Constant: PythonDatatypes.CONSTANT,
    fields.DateTime: PythonDatatypes.DATETIME,
    fields.Decimal: PythonDatatypes.DECIMAL,
    fields.Dict: PythonDatatypes.DICT,
    fields.Email: PythonDatatypes.EMAIL,
    fields.Field: PythonDatatypes.FIELD,
    fields.Float: PythonDatatypes.FLOAT,
    fields.Function: PythonDatatypes.FUNCTION,
    fields.Int: PythonDatatypes.INT,
    fields.Integer: PythonDatatypes.INT,
    fields.Mapping: PythonDatatypes.MAPPING,
    fields.Method: PythonDatatypes.METHOD,
    fields.Number: PythonDatatypes.NUMBER,
    fields.Raw: PythonDatatypes.RAW,
    fields.Str: PythonDatatypes.STRING,
    fields.String: PythonDatatypes.STRING,
    fields.TimeDelta: PythonDatatypes.TIMEDELTA,
    fields.Url: PythonDatatypes.URL,
    fields.UUID: PythonDatatypes.UUID,
}
