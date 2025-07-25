from __future__ import annotations
import dataclasses
import typing

from mojito import types
from mojito import parser


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


@dataclasses.dataclass(frozen=True, slots=True)
class Closure:
    body: types.Quotation
    vocab: Vocab


class Executor:
    def __init__(self, vocab: Vocab):
        self.vocab = vocab
        self.state = InternalState([])

    def run(self, source):
        ast = types.Quotation(parser.parse(source).items)
        closure = Closure(ast, self.vocab)
        return self.execute(closure)

    def execute(self, closure):
        def reader(ws):
            i = 0

            def aux():
                nonlocal i
                if i < len(ws):
                    r = ws[i]
                    i += 1
                    return r
                return None

            return aux

        read_word = reader(closure.body.items)
        while word := read_word():
            match word:
                case types.Number() | types.String():
                    self.state.push(word)
                case types.Quotation():
                    closure = Closure(word, closure.vocab)
                    self.state.push(closure)
                case types.Word(name=name):
                    func = closure.vocab.lookup(name)
                    if not func:
                        raise RuntimeError(f"I don't know the word: {name}")

                    if isinstance(func, Closure):
                        self.execute(func)
                    else:
                        func(word, self.state, closure.vocab, read_word, self.execute)
