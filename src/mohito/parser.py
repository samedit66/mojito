from __future__ import annotations
import dataclasses
import typing

from mohito import tokenizer as t


"""
vocab = Vocabulary()


@vocab.register_builtin("dup")
def dup(data_stack):
    data_stack.dup()


@vocab.register_builtin("drop")
def drop(return_stack):
    data_stack.drop()




"""


class State: ...


@dataclasses.dataclass(frozen=True)
class Word:
    name: str


@dataclasses.dataclass(frozen=True)
class Number:
    value: float


@dataclasses.dataclass(frozen=True)
class String: ...


@dataclasses.dataclass(frozen=True)
class Sequence(typing.Sequence):
    sequence: list[Word | Number | Sequence]

    def __getitem__(self, i):
        return self.sequence[i]

    def __len__(self):
        return len(self.sequence)

    def __iter__(self):
        return iter(self.sequence)


def parse(code_line: str) -> Sequence:
    for token in t.tokenize(code_line):
        ...
