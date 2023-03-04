from typing import Type

from rest_framework import serializers

from marshmallow_export.types import PythonDatatypes

drf_mappings: dict[Type[serializers.Field], PythonDatatypes] = {
    serializers.BooleanField: PythonDatatypes.BOOL,
    serializers.CharField: PythonDatatypes.STRING,
    serializers.EmailField: PythonDatatypes.EMAIL,
    serializers.RegexField: PythonDatatypes.UNDEFINED,
    serializers.SlugField: PythonDatatypes.UNDEFINED,
    serializers.URLField: PythonDatatypes.URL,
    serializers.UUIDField: PythonDatatypes.UUID,
    serializers.FilePathField: PythonDatatypes.UNDEFINED,
    serializers.IPAddressField: PythonDatatypes.IP_ADDRESS,
    serializers.IntegerField: PythonDatatypes.INT,
    serializers.FloatField: PythonDatatypes.FLOAT,
    serializers.DecimalField: PythonDatatypes.DECIMAL,
    serializers.DateTimeField: PythonDatatypes.DATETIME,
    serializers.DateField: PythonDatatypes.DATE,
    serializers.TimeField: PythonDatatypes.TIME,
    serializers.DurationField: PythonDatatypes.DURATION,
    serializers.FileField: PythonDatatypes.UNDEFINED,
    serializers.ImageField: PythonDatatypes.UNDEFINED,
    serializers.DictField: PythonDatatypes.DICT,
    serializers.HStoreField: PythonDatatypes.UNDEFINED,
    serializers.JSONField: PythonDatatypes.JSON,

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
