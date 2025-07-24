from __future__ import annotations

import mohito.tokenizer as t
from mohito import types


class ProgramBuilder:
    """
    Helper to form a `types.Sequence`.
    """

    def __init__(self):
        self.stack = [[]]
        self.context = self.stack[-1]

    def program(self):
        return types.Program(self.stack[-1])

    def append(self, element):
        self.context.append(element)

    def enter(self):
        self.stack.append([])
        self.context = self.stack[-1]

    def leave(self):
        sub = types.Quotation(self.stack.pop())
        self.stack[-1].append(sub)
        self.context = self.stack[-1]


class MohitoSyntaxError(Exception):
    pass


class Parser:
    def __init__(self):
        self.builder = ProgramBuilder()
        self.left_brackets = []

    def consume(self, token: types.TokenWithLineNumber):
        match token.kind:
            case (
                types.MohitoTokenKind.FLOAT_NUMBER
                | types.MohitoTokenKind.INTEGER_NUMBER
                | types.MohitoTokenKind.STRING
                | types.MohitoTokenKind.WORD
            ):
                term = convert_token_to_term(token)
                self.builder.append(term)
            case types.MohitoTokenKind.LEFT_SQUARE_BRACKET:
                self.left_brackets.append(token)
                self.builder.enter()
            case types.MohitoTokenKind.RIGHT_SQUARE_BRACKET:
                if not self.left_brackets:
                    raise MohitoSyntaxError(
                        error(
                            "unexpected quotation end",
                            (token.line_number, token.start, token.end),
                        )
                    )

                self.left_brackets.pop()
                self.builder.leave()
            case types.MohitoTokenKind.INVALID_STRING:
                raise MohitoSyntaxError(
                    error(
                        "invalid string literal",
                        (token.line_number, token.start, token.end),
                    )
                )
            case _:
                raise MohitoSyntaxError(
                    error(
                        f"token '{token.value}' is not supported by parser",
                        (token.line_number, token.start, token.end),
                    )
                )

    def ast(self) -> types.Program:
        if self.left_brackets:
            last = self.left_brackets.pop()
            raise MohitoSyntaxError(
                error(
                    "quotation was not closed",
                    (last.line_number, last.start, last.end),
                )
            )

        return self.builder.program()


def convert_token_to_term(token: types.TokenWithLineNumber):
    loc = types.Location(
        line_number=token.line_number,
        start=token.start,
        end=token.end,
    )
    match token.kind:
        case types.MohitoTokenKind.FLOAT_NUMBER | types.MohitoTokenKind.INTEGER_NUMBER:
            return types.Number(loc, float(token.value))
        case types.MohitoTokenKind.STRING:
            return types.String(loc, token.value)
        case types.MohitoTokenKind.WORD:
            return types.Word(loc, token.value)


def parse(source) -> types.Program:
    parser = Parser()

    try:
        for token in t.tokenize(source):
            parser.consume(token)
    except t.NoMatchingRuleFoundError as err:
        raise MohitoSyntaxError(
            error("parser is unable to continue: uncrecognozied character found")
        ) from err

    return parser.ast()


def error(msg, loc=None):
    error_msg = f"\x1b[31merror: \x1b[0m{msg}"
    if loc:
        line_number, start, end = loc
        loc_msg = f"\033[1m{location(line_number, start, end)}"
        return f"{loc_msg}: {error_msg}"
    return error_msg


def location(line_number, start, end):
    if start == end:
        return f"Line {line_number}:{start}"
    return f"Line {line_number}:{start}-{end}"
