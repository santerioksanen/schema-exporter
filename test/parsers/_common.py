import unittest

from schema_exporter.types import ParsedField


class BaseParserTests(unittest.TestCase):
    def assert_parsed_field(self, parsed_field: ParsedField, expected: dict) -> None:
        args = {
            "python_datatype": None,
            "export_name": None,
            "field_name": "",
            "required": False,
            "allow_none": False,
            "many": False,
            "dump_only": False,
            "load_only": False,
        }
        args.update(expected)
        for key, value in args.items():
            self.assertEqual(
                getattr(parsed_field, key),
                value,
                f"Key: {key} mismatch, expected: {value}, was: {getattr(parsed_field, key)}",
            )
