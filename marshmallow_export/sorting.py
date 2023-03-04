from .types import ParsedSchema


def mark_nested_schemas(schemas: list[ParsedSchema]):
    changed = True
    while changed:
        changed = False
        for parsed_schema in schemas:
            for nested_schema in parsed_schema.nests:
                if parsed_schema not in nested_schema.nested_by:
                    changed = True
                    nested_schema.nested_by.add(parsed_schema)

            for nested_by_schema in parsed_schema.nested_by:
                if parsed_schema not in nested_by_schema.nests:
                    changed = True
                    nested_by_schema.nests.add(parsed_schema)


def add_ordering_to_schemas(schemas: list[ParsedSchema]):
    changed = True
    while changed:
        changed = False
        for parsed_schema in schemas:
            for nested_by in parsed_schema.nested_by:
                new_ordering = max(nested_by.ordering, parsed_schema.ordering + 1)
                if new_ordering != nested_by.ordering:
                    changed = True
                    nested_by.ordering = new_ordering
