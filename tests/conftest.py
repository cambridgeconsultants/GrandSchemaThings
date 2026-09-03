import json
from pathlib import Path

import pytest

from .example_classes import NestedGst, SampleGst


@pytest.fixture
def sample_gst_json_dict():
    return {"name": "test", "value": 123, "flag": True}


@pytest.fixture
def sample_gst_instance():
    return SampleGst(name="test", value=123, flag=True)


@pytest.fixture
def nested_gst_json_dict():
    return {
        "nested": {"name": "nested", "value": 456, "flag": False},
        "items": [1, 2, 3],
        "mapping": {
            "key1": {"name": "test1", "value": 123, "flag": True},
            "key2": {"name": "test2", "value": 456, "flag": False},
        },
    }


@pytest.fixture
def nested_gst_instance():
    return NestedGst(
        nested=SampleGst(name="nested", value=456, flag=False),
        items=[1, 2, 3],
        mapping={
            "key1": SampleGst(name="test1", value=123, flag=True),
            "key2": SampleGst(name="test2", value=456, flag=False),
        },
    )


@pytest.fixture
def sample_gst_json_file(tmp_path: Path, sample_gst_json_dict):
    json_file = tmp_path / "data.json"
    with open(json_file, "w", encoding="utf-8") as file:
        json.dump(sample_gst_json_dict, file)
    return json_file
