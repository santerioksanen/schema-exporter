from typing import Dict, Type

from marshmallow import fields

from schema_exporter.types import PythonDatatypes

marshmallow_mappings: Dict[Type[fields.Field], PythonDatatypes] = {
    fields.AwareDateTime: PythonDatatypes.DATETIME,
    fields.Bool: PythonDatatypes.BOOL,
    fields.Constant: PythonDatatypes.CONSTANT,
    fields.Date: PythonDatatypes.DATE,
    fields.DateTime: PythonDatatypes.DATETIME,
    fields.Decimal: PythonDatatypes.DECIMAL,
    fields.Dict: PythonDatatypes.DICT,
    fields.Email: PythonDatatypes.EMAIL,
    fields.Float: PythonDatatypes.FLOAT,
    fields.Function: PythonDatatypes.FUNCTION,
    fields.IP: PythonDatatypes.IP_ADDRESS,
    fields.IPInterface: PythonDatatypes.IP_INTERFACE,
    fields.IPv4: PythonDatatypes.IPv4_ADDRESS,
    fields.IPv4Interface: PythonDatatypes.IPv4_INTERFACE,
    fields.IPv6: PythonDatatypes.IPv6_ADDRESS,
    fields.IPv6Interface: PythonDatatypes.IPv6_INTERFACE,
    fields.Int: PythonDatatypes.INT,
    fields.Integer: PythonDatatypes.INT,
    fields.Mapping: PythonDatatypes.MAPPING,
    fields.Method: PythonDatatypes.METHOD,
    fields.NaiveDateTime: PythonDatatypes.DATETIME,
    fields.Number: PythonDatatypes.FLOAT,
    fields.Str: PythonDatatypes.STRING,
    fields.String: PythonDatatypes.STRING,
    fields.Time: PythonDatatypes.TIME,
    fields.URL: PythonDatatypes.URL,
    fields.UUID: PythonDatatypes.UUID,
    fields.Url: PythonDatatypes.URL,
    fields.TimeDelta: PythonDatatypes.TIMEDELTA,
}
