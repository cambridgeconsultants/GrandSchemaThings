from dataclasses import dataclass
from enum import Enum, IntEnum, StrEnum

from grandschemathings.grandschemathings import GrandSchemaThings


class SampleEnum(Enum):
    OPTION_A = "Option A"
    OPTION_B = "Option B"


class Number(IntEnum):
    ONE = 1
    TWO = 2
    THREE = 3


class PathologicalStringEnum(StrEnum):
    ONE = "TWO"
    TWO = "ONE"


@dataclass
class SampleGst(GrandSchemaThings):
    name: str
    value: int
    flag: bool


@dataclass
class NestedGst(GrandSchemaThings):
    nested: SampleGst
    items: list[int]
    mapping: dict[str, SampleGst]


@dataclass
class IntEnumGst(GrandSchemaThings):
    value: Number


@dataclass
class IntEnumDictGst(GrandSchemaThings):
    value: dict[Number, int]


@dataclass
class StrEnumGst(GrandSchemaThings):
    value: PathologicalStringEnum
