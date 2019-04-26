import sys

from dffml.df import Definition

definitions = [
    Definition(
        name="URL",
        primitive="string",
    ),
    Definition(
        name="binary",
        primitive="str",
        lock=True
    ),
    Definition(
        name="binary_is_PIE",
        primitive="bool",
    )
]

for definition in definitions:
    setattr(sys.modules[__name__], definition.name, definition)
