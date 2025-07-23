from __future__ import annotations

from mohito import tokenizer as t
from mohito import types


class SequenceBuilder:
    """
    Helper to form a `types.Sequence`.
    """

    def __init__(self):
        self.stack = [[]]
        self.context = self.stack[-1]

    def sequence(self):
        return types.Sequence(self.stack[-1])

    def append(self, element):
        self.context.append(element)

    def enter(self):
        self.stack.append([])
        self.context = self.stack[-1]

    def leave(self):
        sub = types.Sequence(self.stack.pop())
        self.stack[-1].append(sub)
        self.context = self.stack[-1]


class MohitoSyntaxError(Exception):
    pass


def parse(code_line: str) -> types.Sequence:
    builder = SequenceBuilder()
    left_brackets = []

    for line_number, token in t.tokenize(code_line):
        match token:
            case (
                t.Token(kind=types.MohitoTokenKind.FLOAT_NUMBER)
                | t.Token(kind=types.MohitoTokenKind.INTEGER_NUMBER)
            ):
                n = parse_number(token)
                builder.append(n)
            case t.Token(kind=types.MohitoTokenKind.STRING):
                s = types.String(token.value)
                builder.append(s)
            case t.Token(kind=types.MohitoTokenKind.WORD):
                w = types.Word(token.value)
                builder.append(w)
            case t.Token(kind=types.MohitoTokenKind.LEFT_SQUARE_BRACKET):
                left_brackets.append(token)
                builder.enter()
            case t.Token(kind=types.MohitoTokenKind.RIGHT_SQUARE_BRACKET):
                if not left_brackets:
                    raise MohitoSyntaxError(
                        error_msg(
                            line_number,
                            token.start,
                            token.end,
                            "unexpected quotation end",
                        )
                    )

                left_brackets.pop()
                builder.leave()
            case t.Token(kind=types.MohitoTokenKind.INVALID_STRING):
                raise MohitoSyntaxError(
                    error_msg(
                        line_number, token.start, token.end, "invalid string literal"
                    )
                )

    if left_brackets:
        last = left_brackets.pop()
        raise MohitoSyntaxError(
            error_msg(line_number, last.start, last.end, "quotation was not closed")
        )

    return builder.sequence()


def parse_number(number_token: t.Token) -> types.Number:
    n = float(number_token.value)
    return types.Number(n)


def error_msg(line_number, start, end, msg):
    return f"\033[1m{location(line_number, start, end)}: \x1b[31merror: \x1b[0m{msg}"


def location(line_number, start, end):
    if start == end:
        return f"Line {line_number}:{start}"
    return f"Line {line_number}:{start}-{end}"
