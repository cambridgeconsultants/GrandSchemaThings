import pytest

from grandschemathings.grandschemathings import (
    _convert_from_jsonlike,
    _prepare_for_json,
)

from .example_classes import (
    IntEnumDictGst,
    IntEnumGst,
    NestedGst,
    Number,
    PathologicalStringEnum,
    SampleEnum,
    SampleGst,
    StrEnumGst,
)


@pytest.mark.parametrize(
    "data, expected",
    [
        # Empty containers and strings
        ("", ""),
        ([], []),
        ({}, {}),
        ({"": ""}, {"": ""}),
        ({"nested": {"": ""}}, {"nested": {"": ""}}),
        # If Enums aren't involved, everything should come out the same as long as it's
        # a valid type
        (42, 42),
        ("hello", "hello"),
        (3.14, 3.14),
        (True, True),
        ([1, 2, 3], [1, 2, 3]),
        ({"key": "value"}, {"key": "value"}),
        # Nested structures should also come out the same as they went in
        (
            {"key1": [1, 2, 3], "key2": [4, 5, 6]},
            {"key1": [1, 2, 3], "key2": [4, 5, 6]},
        ),
        (
            {
                "key1": [{"subkey1": "value1"}, {"subkey2": "value2"}],
                "key2": [{"subkey3": "value3"}],
            },
            {
                "key1": [{"subkey1": "value1"}, {"subkey2": "value2"}],
                "key2": [{"subkey3": "value3"}],
            },
        ),
        # Enums should be converted to strings
        (SampleEnum.OPTION_A, "OPTION_A"),
        # Enums should be converted when they are dict keys
        (
            {SampleEnum.OPTION_A: "value1", SampleEnum.OPTION_B: "value2"},
            {"OPTION_A": "value1", "OPTION_B": "value2"},
        ),
        # Enums should be converted when they are dict values
        (
            {"key1": SampleEnum.OPTION_A, "key2": SampleEnum.OPTION_B},
            {"key1": "OPTION_A", "key2": "OPTION_B"},
        ),
        # Enums should be converted when they are in a list
        (
            {"key1": [SampleEnum.OPTION_A, SampleEnum.OPTION_B]},
            {"key1": ["OPTION_A", "OPTION_B"]},
        ),
    ],
)
def test_prepare_for_json(data, expected):
    assert _prepare_for_json(data) == expected


def test_prepare_for_json_invalid_dict_keys():
    with pytest.raises(
        TypeError,
        match=r"Dictionary \(object\) keys must be str or Enum for conversion to JSON",
    ):
        _prepare_for_json({1: "value"})
    with pytest.raises(
        TypeError,
        match=r"Type 'tuple' is not supported.",
    ):
        _prepare_for_json({(1, 2): "value"})


def test_prepare_for_json_unsupported_types():
    class UnsupportedType:
        pass

    with pytest.raises(TypeError):
        _prepare_for_json(UnsupportedType())  # type: ignore
    with pytest.raises(TypeError):
        _prepare_for_json((1, 2, 3))  # type: ignore


@pytest.mark.parametrize(
    "data, target_type, expected",
    [
        ("", str, ""),
        ([], list[str], []),
        ({}, dict[str, int], {}),
        ({"": ""}, dict[str, str], {"": ""}),
        ({"nested": {"": ""}}, dict[str, dict[str, str]], {"nested": {"": ""}}),
        (42, int, 42),
        ("hello", str, "hello"),
        (3.14, float, 3.14),
        (True, bool, True),
        ([1, 2, 3], list[int], [1, 2, 3]),
        ({"key": "value"}, dict[str, str], {"key": "value"}),
        ("OPTION_A", SampleEnum, SampleEnum.OPTION_A),
        (
            {"name": "test", "value": 123, "flag": True},
            SampleGst,
            SampleGst(name="test", value=123, flag=True),
        ),
        (
            {
                "nested": {"name": "nested", "value": 456, "flag": False},
                "items": [10, 9, 8],
                "mapping": {
                    "key1": {"name": "test1", "value": 123, "flag": True},
                    "key2": {"name": "test2", "value": 456, "flag": False},
                },
            },
            NestedGst,
            NestedGst(
                nested=SampleGst(name="nested", value=456, flag=False),
                items=[10, 9, 8],
                mapping={
                    "key1": SampleGst(name="test1", value=123, flag=True),
                    "key2": SampleGst(name="test2", value=456, flag=False),
                },
            ),
        ),
        (
            [
                {"name": "test1", "value": 123, "flag": True},
                {"name": "test2", "value": 456, "flag": False},
            ],
            list[SampleGst],
            [
                SampleGst(name="test1", value=123, flag=True),
                SampleGst(name="test2", value=456, flag=False),
            ],
        ),
        (
            {
                "key1": [{"name": "test1", "value": 123, "flag": True}],
                "key2": [{"name": "test2", "value": 456, "flag": False}],
            },
            dict[str, list[SampleGst]],
            {
                "key1": [SampleGst(name="test1", value=123, flag=True)],
                "key2": [SampleGst(name="test2", value=456, flag=False)],
            },
        ),
        (
            [
                {
                    "nested": {"name": "nested1", "value": 123, "flag": True},
                    "items": [4, 3, 2],
                    "mapping": {
                        "key1": {"name": "test1", "value": 123, "flag": True},
                        "key2": {"name": "test2", "value": 456, "flag": False},
                    },
                },
                {
                    "nested": {"name": "nested2", "value": 456, "flag": False},
                    "items": [4, 9, 7],
                    "mapping": {
                        "key3": {"name": "test3", "value": 789, "flag": True},
                        "key4": {"name": "test4", "value": 101, "flag": False},
                    },
                },
            ],
            list[NestedGst],
            [
                NestedGst(
                    nested=SampleGst(name="nested1", value=123, flag=True),
                    items=[4, 3, 2],
                    mapping={
                        "key1": SampleGst(name="test1", value=123, flag=True),
                        "key2": SampleGst(name="test2", value=456, flag=False),
                    },
                ),
                NestedGst(
                    nested=SampleGst(name="nested2", value=456, flag=False),
                    items=[4, 9, 7],
                    mapping={
                        "key3": SampleGst(name="test3", value=789, flag=True),
                        "key4": SampleGst(name="test4", value=101, flag=False),
                    },
                ),
            ],
        ),
    ],
)
def test_convert_from_jsonlike(data, target_type, expected):
    assert _convert_from_jsonlike(data, target_type) == expected


def test_prepare_for_json_intenum_uses_name():
    assert _prepare_for_json(Number.ONE) == "ONE"


def test_prepare_for_json_strenum_uses_name():
    assert _prepare_for_json(PathologicalStringEnum.ONE) == "ONE"


def test_convert_from_jsonlike_intenum():
    assert _convert_from_jsonlike("ONE", Number) is Number.ONE


def test_convert_from_jsonlike_strenum():
    assert (
        _convert_from_jsonlike("ONE", PathologicalStringEnum)
        is PathologicalStringEnum.ONE
    )


def test_intenum_round_trip():
    instance = IntEnumGst(Number.ONE)

    json_dict = instance.to_json_dict()

    assert json_dict == {"value": "ONE"}
    assert IntEnumGst.from_json_dict(json_dict) == instance


def test_intenum_dict_round_trip():
    instance = IntEnumDictGst({Number.ONE: 2})

    json_dict = instance.to_json_dict()

    assert json_dict == {"value": {"ONE": 2}}
    assert IntEnumDictGst.from_json_dict(json_dict) == instance


def test_strenum_round_trip():
    instance = StrEnumGst(PathologicalStringEnum.ONE)

    json_dict = instance.to_json_dict()

    assert json_dict == {"value": "ONE"}
    assert StrEnumGst.from_json_dict(json_dict) == instance


def test_prepare_for_json_intenum_dict_keys():
    assert _prepare_for_json({Number.ONE: "foo"}) == {
        "ONE": "foo",
    }
