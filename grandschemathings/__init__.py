"""grandschemathings package.

This package provides utilities for easy JSON loading and saving for objects, with
validation using JSON schemas.

Usage:
    from grandschemathings import GrandSchemaThings

Example:
    @dataclass
    class MyData(GrandSchemaThings):
        name: str
        value: int

    # Create an instance
    data = MyData(name="example", value=42)

    # Convert to JSON dictionary
    json_dict = data.to_json_dict()

    # Save to file
    data.to_file(Path("data.json"))

    # Load from file
    loaded_data = MyData.from_file(Path("data.json"))
"""

from .grandschemathings import GrandSchemaThings
