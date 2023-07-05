from decimal import Decimal
from typing import Any, Dict

from schema_exporter.types import PythonDatatypes

python_native_mappings: Dict[Any, PythonDatatypes] = {
    bool: PythonDatatypes.BOOL,
    int: PythonDatatypes.INT,
    float: PythonDatatypes.FLOAT,
    Decimal: PythonDatatypes.DECIMAL,
    str: PythonDatatypes.STRING,
}
