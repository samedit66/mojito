from __future__ import annotations
import typing
import itertools as it

from mojito import types


class NoMatchingRuleFoundError(Exception):
    """
    Raised when no token rule matches the input at the current position.
    """


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
        self.__rules: typing.List[types.TokenRule] = []

    def add_token(
        self,
        regex_rule: str,
        kind: typing.Any,
    ) -> RegexTokenizer:
        """
        Adds a token rule to the tokenizer.

        Args:
            regex_rule: The regex pattern for matching tokens.
            kind: The token type or label to assign on match.

        Returns:
            The RegexTokenizer instance (for method chaining).
        """
        self.__rules.append(types.TokenRule(regex_rule, kind))
        return self

    def ignore(
        self,
        regex_rule: str,
    ) -> RegexTokenizer:
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
    ) -> typing.Iterator[types.Token]:
        """
        Tokenizes the input text using the configured rules.

        Args:
            s: The string to tokenize.

        Yields:
            Tokens whose `kind` is not None.

        Raises:
            NoMatchingRuleFoundError: If a segment of text cannot be matched by any rule.
        """
        for token in simple_tokenize(s, self.__rules):
            if token.kind is not None:
                yield token


def simple_tokenize(
    s: str,
    rules: typing.Iterable[types.TokenRule],
) -> typing.Iterator[types.Token]:
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
            error_snippet = s[index : index + 3]
            msg = f"No rule matched at index {index}: '{error_snippet}'"
            raise NoMatchingRuleFoundError(msg)


def mojito_tokenizer() -> RegexTokenizer:
    return (
        RegexTokenizer()
        # Whitespace to ignore
        .ignore(r"\s+")
        .ignore(r"//.*\n?")
        # Valid string
        .add_token(r'"([^"\n\\]|\\n|\\"|\\t|\\\\)*"', types.MojitoTokenKind.STRING)
        # Invalid string
        .add_token(r'".*\n?$', types.MojitoTokenKind.INVALID_STRING)
        # Quotes
        .add_token(r"\[", types.MojitoTokenKind.LEFT_SQUARE_BRACKET)
        .add_token(r"\]", types.MojitoTokenKind.RIGHT_SQUARE_BRACKET)
        # Numbers
        .add_token(r"[\-+]?\d*\.\d+", types.MojitoTokenKind.FLOAT_NUMBER)
        .add_token(r"[\-+]?\d+", types.MojitoTokenKind.INTEGER_NUMBER)
        # Any other non-space identifier is a word
        .add_token(r"[^\s\[\]\"]+", types.MojitoTokenKind.WORD)
    )


def tokenize(source, line_number: int = 1):
    """
    Tokenizes the input using the Mojito tokenizer.

    The input can be either:
    - A string, which will be split into lines using `str.splitlines()`.
    - A callable that returns one line of text per call. Tokenization stops when the callable returns an empty string or `None`.

    Args:
        source: A string to be tokenized or a callable returning lines of text.
        line_number: The initial line number to associate with the generated tokens.

    Yields:
        Token (`mojito.types.TokenWithLineNumber`) objects as defined by the Mojito language specification.
    """
    tokenizer = mojito_tokenizer()

    if isinstance(source, str):
        lines = iter(source.splitlines() + [""])

        def source():
            return next(lines)

    i = line_number
    while line := source():
        for line_number, token in zip(it.repeat(i), tokenizer(line)):
            yield types.TokenWithLineNumber(
                kind=token.kind,
                line_number=line_number,
                start=token.start,
                end=token.end,
                value=token.value,
            )
        i += 1
