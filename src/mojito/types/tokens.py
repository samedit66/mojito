import dataclasses
import enum
import typing
import re


@dataclasses.dataclass(frozen=True)
class Token:
    """
    Represents a token produced by the tokenizer.

    Attributes:
        kind: The type or category of the token.
        value: The substring matched for this token.
        start: The start index of the token in the input string.
        end: The end index (inclusive) of the token in the input string.
    """

    kind: typing.Any
    value: str
    start: int
    end: int


@dataclasses.dataclass(frozen=True)
class TokenWithLineNumber(Token):
    line_number: int


@dataclasses.dataclass(frozen=True)
class TokenRule:
    """
    Defines a rule for matching tokens based on a regular expression.

    Attributes:
        regex_rule: The regular expression pattern to apply.
        kind: The type or category assigned to tokens matching this rule.
    """

    regex_rule: str
    kind: typing.Any

    def try_match(
        self,
        s: str,
        *,
        start_index: int = 0,
    ) -> typing.Optional[Token]:
        """
        Attempts to match the rule against the input string at a given position.

        Args:
            s: The full input string.
            start_index: The index in `s` at which to start matching.

        Returns:
            A Token if the pattern matches at `start_index`, otherwise None.
        """
        substring = s[start_index:]
        match = re.match(self.regex_rule, substring)
        if not match:
            return None

        return Token(
            kind=self.kind,
            value=match.group(),
            start=match.start() + start_index,
            end=match.end() + start_index - 1,
        )


@enum.unique
class MojitoTokenKind(enum.Enum):
    LEFT_SQUARE_BRACKET = enum.auto()
    RIGHT_SQUARE_BRACKET = enum.auto()
    INTEGER_NUMBER = enum.auto()
    FLOAT_NUMBER = enum.auto()
    STRING = enum.auto()
    WORD = enum.auto()
    INVALID_STRING = enum.auto()
