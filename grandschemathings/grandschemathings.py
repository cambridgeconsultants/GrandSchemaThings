"""Provides easy JSON loading and saving for objects."""

import json
from dataclasses import asdict, dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Self, TypeVar, cast, get_type_hints, overload

from jsonschema import validate

ScalarType = TypeVar("ScalarType", int, str, float, bool)


@dataclass
class GrandSchemaThings:
    """Base class for instances that can be represented as JSON with validation."""

    @classmethod
    def _schema_version_string(cls) -> str:
        """The JSON schema version string, as used by the $schema keyword.

        Returns:
            str: The version string.
        """
        return "https://json-schema.org/draft/2020-12/schema"

    @classmethod
    def schema(
        cls, include_version: bool = True
    ) -> dict[str, str | list | dict | bool]:
        """A full schema for the object, optionally including schema version.

        Args:
            include_version (bool, optional): Whether to include the schema version
                (i.e. "$schema": <schema version string>). Defaults to True.

        Returns:
            dict[str, str | list | dict | bool]: The object's JSON schema, as a Python
                dict.
        """
        type_hints = get_type_hints(cls)
        schema: dict[str, str | list | dict | bool] = {}
        if include_version:
            schema["$schema"] = cls._schema_version_string()
        schema["type"] = "object"
        schema["properties"] = {
            name: _type_schema(ann_type) for name, ann_type in type_hints.items()
        }

        schema["additionalProperties"] = False
        schema["required"] = list(type_hints.keys())
        return schema

    @classmethod
    def schema_to_file(cls, filepath: Path, include_version: bool = True) -> None:
        """Save a schema for the object to file.

        Args:
            filepath (Path): The file to save to.
            include_version (bool, optional): Whether to include the schema version
                (i.e. "$schema": <schema version string>). Defaults to True.
        """
        with open(filepath, "w", encoding="utf-8") as file:
            json.dump(cls.schema(include_version), file, indent=4)

    @classmethod
    def from_json_dict(cls, json_dict: dict[str, Any]) -> Self:
        """Create an instance of the class from JSON data in dict form.

        Raises:
            jsonschema.exceptions.ValidationError: If the data does not conform to the
                schema.
            jsonschema.exceptions.SchemaError: If the schema defined by the class is
                invalid.

        Args:
            json_dict (dict[str, Any]): The JSON object converted to a Python dict.

        Returns:
            Self: The class instance.
        """
        validate(json_dict, cls.schema(include_version=True))
        converted = {
            name: _convert_from_jsonlike(json_dict[name], attr_type)
            for name, attr_type in get_type_hints(cls).items()
        }
        return cls(**converted)

    def to_json_dict(self) -> dict[str, Any]:
        """Create a JSON dictionary representing the instance.

        Returns:
            dict[str, Any]: The JSON-style dictionary.
        """
        return _prepare_for_json(asdict(self))

    @classmethod
    def from_file(
        cls,
        filepath: Path,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> Self:
        """Creates an instance from a JSON file.

        Args:
            filepath (Path): Path to the JSON file.
            encoding (str | None, optional): Text encoding passed to
                pathlib.Path.read_text(). Defaults to None.
            errors (str | None, optional): Error handling strategy passed to
                pathlib.Path.read_text(). Defaults to None.
            newline (str | None, optional): Newline handling mode passed to
                pathlib.Path.read_text(). Defaults to None.

        Returns:
            Self: An instance of the class.
        """
        return cls.from_json_dict(
            json.loads(filepath.read_text(encoding, errors, newline))
        )

    def to_file(
        self,
        filepath: Path,
        pretty: bool = False,
        encoding: str | None = None,
        errors: str | None = None,
        newline: str | None = None,
    ) -> None:
        """Write the object to a JSON file.

        Args:
            filepath (Path): The file to create.
            pretty (bool, optional): Whether to make a multi-line, indented string.
                Defaults to False.
            encoding (str | None, optional): Text encoding passed to
                pathlib.Path.write_text(). Defaults to None.
            errors (str | None, optional): Error handling strategy passed to
                pathlib.Path.write_text(). Defaults to None.
            newline (str | None, optional): Newline handling mode passed to
                pathlib.Path.write_text(). Defaults to None.
        """
        filepath.write_text(
            json.dumps(self.to_json_dict(), indent=4 if pretty else None),
            encoding,
            errors,
            newline,
        )

    @classmethod
    def list_from_file(cls, filepath: Path) -> list[Self]:
        """Load a list of objects from a JSON file.

        Args:
            filepath (Path): Path to the JSON file.

        Returns:
            list[Self]: A list of instances loaded from file.
        """
        schema = {
            "$schema": cls._schema_version_string(),
            "type": "array",
            "items": cls.schema(include_version=False),
        }
        with open(filepath, "r", encoding="utf-8") as file:
            json_array = json.load(file)
            validate(json_array, schema)
            return [cls.from_json_dict(obj) for obj in json_array]

    @classmethod
    def list_to_file(
        cls, filepath: Path, items: list[Self], pretty: bool = False
    ) -> None:
        """Write a list of instances to file.

        Args:
            filepath (Path): The path to write to.
            items (list[Self]): The list of instances to write.
            pretty (bool, optional): Whether to make a multi-line, indented string.
                Defaults to False.
        """
        filepath.write_text(
            json.dumps(
                [item.to_json_dict() for item in items], indent=4 if pretty else None
            ),
            encoding="utf-8",
        )


@overload
def _type_schema(
    attr_type: type[int | str | float | bool | Enum],
) -> dict[str, str]: ...


@overload
def _type_schema(
    attr_type: type[list | dict | GrandSchemaThings],
) -> dict[str, Any]: ...


def _type_schema(
    attr_type: type[int | str | float | bool | Enum | list | dict | GrandSchemaThings],
) -> dict[str, Any]:
    """Creates a JSON schema, in dict form, for a GrandSchemaThings-compatible type.

    Args:
        attr_type (type[int | str | float | bool | Enum | list | dict |
            GrandSchemaThings]): The type to generate a schema for.

    Raises:
        NotImplementedError: If an iterable type other than dict or list is passed in.
        ValueError: If an unsupported type is passed in.

    Returns:
        dict[str, Any]: The JSON schema in dict form.
    """
    if any(attr_type is t for t in [int, str, float, bool]):
        json_names = {
            "int": "integer",
            "str": "string",
            "float": "number",
            "bool": "boolean",
        }
        return {"type": json_names[str(attr_type.__name__)]}
    if hasattr(attr_type, "__origin__") and hasattr(attr_type, "__args__"):
        iter_type = attr_type.__origin__
        iter_arg_types = attr_type.__args__
        if iter_type is list:
            return {"type": "array", "items": _type_schema(iter_arg_types[0])}
        if iter_type is dict:
            key_type, value_type = iter_arg_types
            if key_type is str:
                return {
                    "type": "object",
                    "additionalProperties": _type_schema(value_type),
                }
            if issubclass(key_type, Enum):
                return {
                    "type": "object",
                    "properties": {e.name: _type_schema(value_type) for e in key_type},
                    "additionalProperties": False,
                }
            raise ValueError(
                "JSON can only represent dictionaries with keys that are of type "
                "str or Enum"
            )
        raise NotImplementedError(
            f"Iterable type {iter_type} not currently implemented"
        )
    if issubclass(attr_type, Enum):
        return {"type": "string", "enum": [e.name for e in attr_type]}
    if issubclass(attr_type, GrandSchemaThings):
        return attr_type.schema(include_version=False)
    raise ValueError(f"Unrecognised type '{attr_type}'")


@overload
def _prepare_for_json(data: ScalarType) -> ScalarType: ...


@overload
def _prepare_for_json(data: list[Any]) -> list[Any]: ...


@overload
def _prepare_for_json(data: dict[Any, Any]) -> dict[str, Any]: ...


@overload
def _prepare_for_json(data: Enum) -> str: ...


def _prepare_for_json(
    data: ScalarType | list[Any] | dict[Any, Any] | Enum,
) -> ScalarType | list | dict[str, Any] | str:
    """Recursively convert values to JSON-like, converting Enums and checking dict keys.

    Args:
        data (ScalarType | list[Any] | dict[Any, Any] | Enum): The value to convert.

    Returns:
        ScalarType | list | dict[str, Any] | str: The converted value.
    """

    def prepare_key(key: str | Enum) -> str:
        k = _prepare_for_json(key)
        if not isinstance(k, str):
            raise TypeError(
                "Dictionary (object) keys must be str or Enum for conversion to JSON"
            )
        return k

    if isinstance(data, Enum):
        return data.name

    if isinstance(data, (int, str, float, bool)):
        return data

    if isinstance(data, list):
        return [_prepare_for_json(v) for v in data]

    if isinstance(data, dict):
        return {prepare_key(k): _prepare_for_json(v) for k, v in data.items()}

    raise TypeError(f"Type '{type(data).__name__}' is not supported.")


@overload
def _convert_from_jsonlike(
    data: ScalarType, target_type: type[ScalarType]
) -> ScalarType: ...


@overload
def _convert_from_jsonlike(data: list, target_type: type[list]) -> list: ...


@overload
def _convert_from_jsonlike(data: dict, target_type: type[dict]) -> dict: ...


@overload
def _convert_from_jsonlike(data: str, target_type: type[Enum]) -> Enum: ...


@overload
def _convert_from_jsonlike(
    data: dict, target_type: type[GrandSchemaThings]
) -> GrandSchemaThings: ...


def _convert_from_jsonlike(
    data: ScalarType | list | dict | str,
    target_type: type[ScalarType | list | dict | Enum | GrandSchemaThings],
) -> ScalarType | list | dict | Enum | GrandSchemaThings:
    """Convert a JSON-like value to a Python/GrandSchemaThings value.

    Args:
        data (ScalarType | list | dict | str): The value to convert.
        target_type (type[ScalarType | list | dict | Enum | GrandSchemaThings]): The
            target type.

    Returns:
        ScalarType | list | dict | Enum | GrandSchemaThings: The converted data.
    """
    # Get the actual type indicated by the target type, even if it's a container
    target_type_raw = getattr(target_type, "__origin__", target_type)
    target_type_args: tuple = getattr(target_type, "__args__", tuple())

    # Convert enums and instances of GrandSchemaThings
    if issubclass(target_type_raw, Enum):
        if not isinstance(data, str):
            raise TypeError(
                "Expected data of type 'str' for conversion to Enum "
                f"'{target_type_raw.__name__}', but got '{type(data).__name__}'"
            )
        try:
            return cast(type[Enum], target_type_raw)[data]
        except KeyError:
            raise ValueError(f"Enum '{target_type_raw}' has no member '{data}'")
    if issubclass(target_type_raw, GrandSchemaThings):
        if not isinstance(data, dict):
            raise TypeError(
                "Expected data of type 'dict[str, Any]' for conversion to "
                f"'{target_type_raw.__name__}', but got '{type(data).__name__}'"
            )
        target_type_raw = cast(type[GrandSchemaThings], target_type_raw)
        return target_type_raw.from_json_dict(data)

    # If we've not returned by this point, the data should be an instance of the raw
    # type. Make sure it is.
    if not isinstance(data, target_type_raw):
        raise TypeError(
            f"Target type is '{target_type_raw.__name__}' but data is of type "
            f"'{type(data).__name__}'"
        )
    # If it's a scalar type, we just return it
    if target_type_raw in {int, str, float, bool}:
        return cast(ScalarType, data)
    # If it's a list or dict, iterate through it, converting each key/value
    if target_type_raw is list:
        (item_type,) = target_type_args
        return [_convert_from_jsonlike(v, item_type) for v in cast(list, data)]
    if target_type_raw is dict:
        key_type, value_type = target_type_args
        return {
            _convert_from_jsonlike(k, key_type): _convert_from_jsonlike(v, value_type)
            for k, v in cast(dict, data).items()
        }

    raise ValueError(f"Unrecognised type '{target_type_raw}'")
