from __future__ import annotations
import dataclasses
import typing

from mojito import types


@dataclasses.dataclass(frozen=True, slots=True)
class InternalState:
    data_stack: list[typing.Union[types.Number, types.String, Closure]]

    def push(self, element):
        self.data_stack.append(element)

    def pop(self):
        if not self.data_stack:
            raise RuntimeError("Stack underflow")
        return self.data_stack.pop()

    def dup(self):
        if not self.data_stack:
            raise RuntimeError("Stack underflow")
        self.data_stack.append(self.data_stack[-1])

    def __repr__(self):
        outputs = []

        for v in self.data_stack:
            match v:
                case types.String():
                    outputs.append(f'"{v.value}"')
                case types.Number():
                    str_value = str(v.value)

                    for i in reversed(range(len(str_value))):
                        if str_value[i] != "0":
                            break

                    if str_value[i] == ".":
                        border = i
                    else:
                        border = i + 1

                    outputs.append(str_value[:border])
                case Closure():
                    outputs.append("quotation")

        return f"stack: < {' '.join(outputs)} >"


@dataclasses.dataclass(frozen=True, slots=True)
class Vocab:
    parent_vocab: typing.Optional[Vocab]
    builtins: dict[str, typing.Callable[[InternalState, Vocab], None]]
    user_defined: dict[str, Closure]

    def is_builtin(self, name: str) -> bool:
        return name in self.builtins

    def builtin(self, name: str):
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

    def child(self):
        return Vocab(
            parent_vocab=self,
            builtins=self.builtins,
            user_defined={},
        )

    def define_word(self, word_name, closure):
        self.user_defined[word_name] = closure


@dataclasses.dataclass(frozen=True, slots=True)
class Closure:
    body: types.Quotation
    vocab: Vocab
