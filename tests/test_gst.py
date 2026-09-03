import json
from pathlib import Path

import pytest

from grandschemathings.grandschemathings import _type_schema

from .example_classes import NestedGst, SampleGst


def test_schema():
    expected_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "integer"},
            "flag": {"type": "boolean"},
        },
        "additionalProperties": False,
        "required": ["name", "value", "flag"],
    }
    assert SampleGst.schema() == expected_schema


def test_schema_to_file(tmp_path: Path):
    schema_file = tmp_path / "schema.json"
    SampleGst.schema_to_file(schema_file)
    with open(schema_file, "r", encoding="utf-8") as file:
        schema = json.load(file)
    expected_schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "value": {"type": "integer"},
            "flag": {"type": "boolean"},
        },
        "additionalProperties": False,
        "required": ["name", "value", "flag"],
    }
    assert schema == expected_schema


def test_from_json_dict(sample_gst_json_dict, sample_gst_instance):
    instance = SampleGst.from_json_dict(sample_gst_json_dict)
    assert instance == sample_gst_instance


def test_to_json_dict(sample_gst_instance, sample_gst_json_dict):
    assert sample_gst_instance.to_json_dict() == sample_gst_json_dict


def test_from_file(sample_gst_json_file, sample_gst_instance):
    instance = SampleGst.from_file(sample_gst_json_file)
    assert instance == sample_gst_instance


def test_to_file(sample_gst_instance, sample_gst_json_dict, tmp_path: Path):
    json_file = tmp_path / "data.json"
    sample_gst_instance.to_file(json_file, pretty=True)
    with open(json_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    assert json_data == sample_gst_json_dict


def test_list_from_file(tmp_path: Path):
    json_file = tmp_path / "data.json"
    json_data = [
        {"name": "test1", "value": 123, "flag": True},
        {"name": "test2", "value": 456, "flag": False},
    ]
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(json_data, file)
    instances = SampleGst.list_from_file(json_file)
    expected_instances = [
        SampleGst(name="test1", value=123, flag=True),
        SampleGst(name="test2", value=456, flag=False),
    ]
    assert instances == expected_instances


def test_list_to_file(tmp_path: Path):
    json_file = tmp_path / "data.json"
    instances = [
        SampleGst(name="test1", value=123, flag=True),
        SampleGst(name="test2", value=456, flag=False),
    ]
    SampleGst.list_to_file(json_file, instances, pretty=True)
    with open(json_file, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    expected_data = [
        {"name": "test1", "value": 123, "flag": True},
        {"name": "test2", "value": 456, "flag": False},
    ]
    assert json_data == expected_data


def test_nested_from_json_dict(nested_gst_json_dict, nested_gst_instance):
    instance = NestedGst.from_json_dict(nested_gst_json_dict)
    assert instance == nested_gst_instance


def test_nested_to_json_dict(nested_gst_instance, nested_gst_json_dict):
    assert nested_gst_instance.to_json_dict() == nested_gst_json_dict


@pytest.mark.parametrize(
    "attr_type, expected_schema",
    [
        (int, {"type": "integer"}),
        (str, {"type": "string"}),
        (float, {"type": "number"}),
        (bool, {"type": "boolean"}),
        (
            SampleGst,
            {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "value": {"type": "integer"},
                    "flag": {"type": "boolean"},
                },
                "additionalProperties": False,
                "required": ["name", "value", "flag"],
            },
        ),
        (list[int], {"type": "array", "items": {"type": "integer"}}),
        (
            dict[str, int],
            {"type": "object", "additionalProperties": {"type": "integer"}},
        ),
        (
            NestedGst,
            {
                "type": "object",
                "properties": {
                    "nested": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "value": {"type": "integer"},
                            "flag": {"type": "boolean"},
                        },
                        "additionalProperties": False,
                        "required": ["name", "value", "flag"],
                    },
                    "items": {"type": "array", "items": {"type": "integer"}},
                    "mapping": {
                        "type": "object",
                        "additionalProperties": {
                            "type": "object",
                            "properties": {
                                "name": {"type": "string"},
                                "value": {"type": "integer"},
                                "flag": {"type": "boolean"},
                            },
                            "additionalProperties": False,
                            "required": ["name", "value", "flag"],
                        },
                    },
                },
                "additionalProperties": False,
                "required": ["nested", "items", "mapping"],
            },
        ),
    ],
)
def test_type_schema(attr_type, expected_schema):
    assert _type_schema(attr_type) == expected_schema


def test_empty_string():
    instance = SampleGst(name="", value=0, flag=False)
    json_dict = {"name": "", "value": 0, "flag": False}
    assert instance.to_json_dict() == json_dict
    assert SampleGst.from_json_dict(json_dict) == instance


def test_empty_list():
    instance = NestedGst(
        nested=SampleGst(name="nested", value=456, flag=False), items=[], mapping={}
    )
    json_dict = {
        "nested": {"name": "nested", "value": 456, "flag": False},
        "items": [],
        "mapping": {},
    }
    assert instance.to_json_dict() == json_dict
    assert NestedGst.from_json_dict(json_dict) == instance
