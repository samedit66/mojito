from __future__ import annotations
import dataclasses
import functools
import re

from mojito import types


def as_string(literal) -> str:
    match literal:
        case types.String(value=value):
            return f'"{value}"'
        case types.Number(value=num_literal):
            return num_as_string(num_literal)
        case types.Closure() as quot:
            return quot_as_string(quot)


def num_as_string(num_literal: float) -> str:
    str_value = str(num_literal)

    match = re.match(r"^(\d+)\.[1-9]*0+$", str_value)
    if match:
        return match.group(1)

    return str_value


def quot_as_string(quot_literal) -> str:
    return "[...]"


class Stack:
    __slots__ = ("data",)

    def __init__(self):
        self.data = []

    def peek(self, at: int = 0):
        # Note about `at`:
        # at=0 -- we take the top of stack
        # at=1 -- we take the second element
        # and so on...
        return self.data[-(at + 1)]

    def push(self, v):
        self.data.append(v)

    def pop(self):
        return self.data.pop()

    def dup(self):
        self.push(self.peek())

    def swap(self):
        a = self.pop()
        b = self.pop()
        self.push(b)
        self.push(a)

    def depth(self) -> int:
        return len(self.data)

    def __repr__(self):
        outputs = [as_string(v) for v in self.data]
        return f"stack: < {' '.join(outputs)} >"


class Vocab:
    __slots__ = (
        "parent_vocab",
        "builtins",
        "user_defined",
    )

    def __init__(
        self,
        parent_vocab=None,
        builtins=None,
        user_defined=None,
    ):
        self.parent_vocab = parent_vocab
        self.builtins = builtins or {}
        self.user_defined = user_defined or {}

    def is_builtin(self, name: str) -> bool:
        return name in self.builtins

    def define(self, name: str, func=None):
        if callable(func):
            self.builtins[name] = func
            return

        if isinstance(func, types.Closure):
            self.user_defined[name] = func
            return

        @functools.wraps(func)
        def decorator(func):
            self.builtins[name] = func
            return func

        return decorator

    def lookup(self, name: str):
        # 1. Check user_defined
        if name in self.user_defined:
            return self.user_defined[name]
        # 2. Check parent vocab recursively
        if self.parent_vocab:
            found = self.parent_vocab.lookup(name)
            if found:
                return found
        # 3. Check builtins
        return self.builtins.get(name)

    def offspring(self):
        return Vocab(
            parent_vocab=self,
            builtins=self.builtins,
            user_defined={},
        )


@dataclasses.dataclass(frozen=True, slots=True)
class Closure:
    body: types.Quotation
    vocab: Vocab
