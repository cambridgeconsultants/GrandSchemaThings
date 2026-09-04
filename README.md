# GrandSchemaThings

Repository: [GitHub](https://github.com/cambridgeconsultants/GrandSchemaThings)
PyPI: [GrandSchemaThings](https://pypi.org/project/grandschemathings/)

The GrandSchemaThings Python package provides automatic loading and saving of JSON for
Python objects, with validation against an automatically-generated schema. It is
designed to make it easy to serialize and deserialize objects to and from JSON.

## Why use GrandSchemaThings?

Compared to a simple `dataclasses.asdict()` approach, GrandSchemaThings:

- Reconstructs typed dataclass objects from JSON
- Automatically generates a matching [JSON Schema](https://json-schema.org/)
- Validates incoming data against that schema when loading
- Recursively handles nested GrandSchemaThings dataclasses, enums, lists and dictionaries
  - Supported field types are: int, str, float, bool, Enum, list[T], dict[str, T],
    dict[Enum, T], and nested GrandSchemaThings subclasses. JSON-compatible restrictions
    apply.
  - Enums are serialised using their name (for example, `Hobby.READING` becomes
    `"READING"`) and are represented in the schema as [JSON schema enums](https://json-schema.org/understanding-json-schema/reference/enum)
- Provides a single, consistent API for serialisation and deserialisation

## User Guide

### System Requirements

- Python >= 3.13

### Installation

Install from PyPI using pip:

```sh
pip install grandschemathings
```

Or, if you use uv or Poetry:
```sh
uv add grandschemathings
poetry add grandschemathings
```

### Usage

#### Simple Usage Example

Here's a simple example to illustrate how you can use GrandSchemaThings to serialize and
deserialize an object.

```python
from dataclasses import dataclass
from pathlib import Path

from grandschemathings import GrandSchemaThings


@dataclass
class MyData(GrandSchemaThings):
    name: str
    age: int


# Create an instance
data = MyData(name="Alice", age=30)

# Serialize to JSON file
data.to_file(Path("data.json"), pretty=True)

# Deserialize from JSON file
loaded_data = MyData.from_file(Path("data.json"))
print(loaded_data)
```

#### Complex Usage Example

This demonstrates how to handle nested objects and dictionaries with enum keys.

```python
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from grandschemathings import GrandSchemaThings


class Hobby(Enum):
    READING = "reading"
    CYCLING = "cycling"
    COOKING = "cooking"
    GARDENING = "gardening"


@dataclass
class Address(GrandSchemaThings):
    street: str
    city: str
    postcode: str


@dataclass
class User(GrandSchemaThings):
    name: str
    age: int
    address: Address
    hobbies: dict[Hobby, int]


# Create an instance
user = User(
    name="Bob",
    age=25,
    address=Address(street="456 Elm St", city="Faketown", postcode="AB12 3CD"),
    hobbies={Hobby.READING: 5, Hobby.CYCLING: 3, Hobby.COOKING: 4, Hobby.GARDENING: 1},
)

# Serialize to JSON file
user.to_file(Path("user.json"), pretty=True)

# Deserialize from JSON file
loaded_user = User.from_file(Path("user.json"))
print(loaded_user)
```

#### API Reference

The following instance and class methods are available for GrandSchemaThings objects.

| Method Name | Description | Type |
|-------------|-------------|------|
| `from_file(...)` | Creates an instance from a JSON file. | Class Method |
| `to_file(...)` | Writes the instance to a JSON file. | Instance Method |
| `from_json_dict(...)` | Creates an instance of the class from JSON data (in Python dict form). | Class Method |
| `to_json_dict()` | Creates a Python dict containing JSON-compatible data representing the instance. | Instance Method |
| `list_from_file(...)` | Loads a list of instances from a JSON file. | Class Method |
| `list_to_file(...)` | Writes a list of instances to a specified file. | Class Method |
| `schema(...)` | Generates a full schema for the class, optionally including the schema version. | Class Method |
| `schema_to_file(...)` | Saves the schema for the class to a specified file. | Class Method |

## Developer Guide

### Development Setup

To modify GrandSchemaThings, you can clone the repository and install the development
dependencies using Poetry:

1. **Install Poetry**: If you haven't already got Poetry installed, follow the
[instructions on their website](https://python-poetry.org/docs/#installation).
2. **Clone the repository**:
   ```sh
   git clone https://github.com/cambridgeconsultants/GrandSchemaThings.git
   cd grandschemathings
   ```
3. **Install dependencies**:
   ```sh
   poetry install
   ```

### Running Tests

Run the validation suite:

```sh
poetry run validate
```

## License

This project is licensed under the Apache License 2.0. See the LICENSE file for details.
