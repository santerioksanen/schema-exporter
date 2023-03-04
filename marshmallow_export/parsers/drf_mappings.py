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
}
