from typing import Dict, Type

from django.db import models

from schema_exporter.types import PythonDatatypes

django_mappings: Dict[Type[models.Field], PythonDatatypes] = {
    models.AutoField: PythonDatatypes.INT,
    models.BigAutoField: PythonDatatypes.INT,
    models.BigIntegerField: PythonDatatypes.INT,
    models.BinaryField: PythonDatatypes.STRING,
    models.BooleanField: PythonDatatypes.BOOL,
    models.CharField: PythonDatatypes.STRING,
    models.DateField: PythonDatatypes.DATE,
    models.DateTimeField: PythonDatatypes.DATETIME,
    models.DecimalField: PythonDatatypes.DECIMAL,
    models.DurationField: PythonDatatypes.DURATION,
    models.EmailField: PythonDatatypes.EMAIL,
    models.FileField: PythonDatatypes.STRING,
    models.FilePathField: PythonDatatypes.STRING,
    models.FloatField: PythonDatatypes.FLOAT,
    models.GenericIPAddressField: PythonDatatypes.IP_ADDRESS,
    models.ImageField: PythonDatatypes.STRING,
    models.IntegerField: PythonDatatypes.INT,
    models.JSONField: PythonDatatypes.JSON_FIELD,
    models.PositiveBigIntegerField: PythonDatatypes.INT,
    models.PositiveIntegerField: PythonDatatypes.INT,
    models.PositiveSmallIntegerField: PythonDatatypes.INT,
    models.SlugField: PythonDatatypes.STRING,
    models.SmallAutoField: PythonDatatypes.INT,
    models.SmallIntegerField: PythonDatatypes.INT,
    models.TextField: PythonDatatypes.STRING,
    models.TimeField: PythonDatatypes.TIME,
    models.URLField: PythonDatatypes.URL,
    models.UUIDField: PythonDatatypes.UUID,
}
