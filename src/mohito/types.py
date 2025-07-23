from __future__ import annotations
import dataclasses
import enum


@enum.unique
class MohitoTokenKind(enum.Enum):
    LEFT_SQUARE_BRACKET = enum.auto()
    RIGHT_SQUARE_BRACKET = enum.auto()
    INTEGER_NUMBER = enum.auto()
    FLOAT_NUMBER = enum.auto()
    STRING = enum.auto()
    WORD = enum.auto()
    INVALID_STRING = enum.auto()


@dataclasses.dataclass(frozen=True)
class Number:
    value: float

    def __eq__(self, other_number) -> bool:
        if isinstance(other_number, (int, float)):
            return self.value == other_number
        return self.value == other_number.value


@dataclasses.dataclass(frozen=True)
class String:
    value: str


@dataclasses.dataclass(frozen=True)
class Word:
    name: str

    def __eq__(self, other_word) -> bool:
        if isinstance(other_word, str):
            return self.name == other_word
        return self.name == other_word.name


@dataclasses.dataclass(frozen=True)
class Sequence:
    items: list[Number | String | Word] = dataclasses.field(default_factory=list)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, index):
        return self.items[index]

    def head(self):
        return self.items[0]

    def tail(self):
        return Sequence(self.items[1:])

    def append(self, element): ...

    def __iter__(self):
        return iter(self.items)
