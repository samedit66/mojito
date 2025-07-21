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


class NoMatchingRuleFoundError(Exception):
    """
    Raised when no token rule matches the input at the current position.
    """
    pass


def tokenize(
    s: str,
    rules: typing.Iterable[TokenRule],
) -> typing.Iterator[Token]:
    """
    Tokenizes the input string by applying a sequence of TokenRule instances.

    Args:
        s: The string to tokenize.
        rules: An iterable of TokenRule objects.

    Yields:
        Token instances for each match in the input string.

    Raises:
        NoMatchingRuleFoundError: If no rule matches at the current position.
    """
    rules_list = list(rules)
    index = 0

    while index < len(s):
        matched = False
        for rule in rules_list:
            token = rule.try_match(s, start_index=index)
            if token:
                matched = True
                index = token.end + 1
                yield token
                break

        if not matched:
            error_snippet = s[index:index + 3]
            msg = f"No rule matched at index {index}: '{error_snippet}'"
            raise NoMatchingRuleFoundError(msg)


class RegexTokenizer:
    """
    An extensible tokenizer that uses regular expression rules to split text into tokens.

    Example:
        tokenizer = (
            RegexTokenizer()
            .add_token(r"\\d+", "NUMBER")
            .add_token(r"\\w+", "IDENTIFIER")
            .ignore(r"\\s+")
        )
        for token in tokenizer("123 abc"):
            print(token)
    """

    def __init__(
        self,
    ) -> None:
        """
        Initializes the tokenizer with an empty rule set.
        """
        self.__rules: typing.List[TokenRule] = []

    def add_token(
        self,
        regex_rule: str,
        kind: typing.Any,
    ) -> 'RegexTokenizer':
        """
        Adds a token rule to the tokenizer.

        Args:
            regex_rule: The regex pattern for matching tokens.
            kind: The token type or label to assign on match.

        Returns:
            The RegexTokenizer instance (for method chaining).
        """
        self.__rules.append(TokenRule(regex_rule, kind))
        return self

    def ignore(
        self,
        regex_rule: str,
    ) -> 'RegexTokenizer':
        """
        Adds a rule to skip over certain patterns without producing tokens.

        Args:
            regex_rule: The regex pattern for text to ignore.

        Returns:
            The RegexTokenizer instance (for method chaining).
        """
        return self.add_token(regex_rule, None)

    def __call__(
        self,
        s: str,
    ) -> typing.Iterator[Token]:
        """
        Tokenizes the input text using the configured rules.

        Args:
            s: The string to tokenize.

        Yields:
            Tokens whose `kind` is not None.

        Raises:
            NoMatchingRuleFoundError: If a segment of text cannot be matched by any rule.
        """
        for token in tokenize(s, self.__rules):
            if token.kind is not None:
                yield token


@enum.unique
class MohitoTokenKind(enum.Enum):
    LEFT_SQUARE_BRACKET = enum.auto()
    RIGHT_SQUARE_BRACKET = enum.auto()
    LEFT_CURLY_BRACKET = enum.auto()
    RIGHT_CURLY_BRACKET = enum.auto()
    ARROW = enum.auto()
    COMMA = enum.auto()
    INTEGER_NUMBER = enum.auto()
    FLOAT_NUMBER = enum.auto()
    STRING = enum.auto()
    WORD = enum.auto()

    # Malformed integer (e.g., '123a')
    INVALID_INTEGER_NUMBER = enum.auto()
    # Malformed float (e.g., '3.14.5', '12.a')
    INVALID_FLOAT_NUMBER = enum.auto()
    # Unterminated or malformed string (e.g., '"abc')
    INVALID_STRING = enum.auto()


def mohito_tokenizer() -> RegexTokenizer:
    """
    Constructs a RegexTokenizer configured for the Mohito language.

    The tokenizer will recognize:
      - Square and curly brackets, arrows, and commas.
      - Valid integers and floats.
      - Valid double-quoted strings with escape support.
      - Identifiers (words).
      - Invalid tokens: malformed integers, floats, and unterminated strings.

    Returns:
        A RegexTokenizer instance with all Mohito token rules added.
    """
    return (
        RegexTokenizer()

        # Whitespace to ignore
        .ignore(r"\s+")

        # Invalid variants (checked after valid patterns):
        # INVALID_FLOAT_NUMBER: numbers with extra letters or multiple dots (e.g., '3.14.5', '12.a')
        .add_token(r"(\d+\.)+[^\d\s\[\]\{\}]+", MohitoTokenKind.INVALID_FLOAT_NUMBER)
        # INVALID_INTEGER_NUMBER: digits followed by letters (e.g., '123a')
        .add_token(r"\d+[^\d\s\[\]\{\}\.\"]+", MohitoTokenKind.INVALID_INTEGER_NUMBER)
        # INVALID_STRING: a string start without closing quote (e.g., '"abc')
        .add_token(r'"(?:[^"\\]|\\.)*$', MohitoTokenKind.INVALID_STRING)

        # Delimiters and punctuation
        .add_token(r"\[", MohitoTokenKind.LEFT_SQUARE_BRACKET)
        .add_token(r"\]", MohitoTokenKind.RIGHT_SQUARE_BRACKET)
        .add_token(r"\{", MohitoTokenKind.LEFT_CURLY_BRACKET)
        .add_token(r"\}", MohitoTokenKind.RIGHT_CURLY_BRACKET)
        .add_token(r"->", MohitoTokenKind.ARROW)
        .add_token(r",", MohitoTokenKind.COMMA)
        # Valid number literals
        .add_token(r"[\d]*\.\d+", MohitoTokenKind.FLOAT_NUMBER)
        .add_token(r"\d+", MohitoTokenKind.INTEGER_NUMBER)
        # Valid strings: double quotes with escapes
        .add_token(r'"(?:[^"\\]|\\.)*"', MohitoTokenKind.STRING)
        # Identifiers / words: allow letters, digits, underscores,
        # and trailing punctuation like !, ?, or apostrophe
        .add_token(r"[^\s\[\]\{\}\"]+", MohitoTokenKind.WORD)
    )
