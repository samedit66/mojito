import pytest

import mojito.tokenizer as t
from mojito import types


def make_token(kind, value, line_number, start, end):
    return types.TokenWithLineNumber(
        kind=kind,
        value=value,
        line_number=line_number,
        start=start,
        end=end,
    )


def tokens(*tuples):
    return [make_token(*args) for args in tuples]


def test_square_brackets():
    s = "[ [] ]"
    expected = tokens(
        (types.MojitoTokenKind.LEFT_SQUARE_BRACKET, "[", 1, 0, 0),
        (types.MojitoTokenKind.LEFT_SQUARE_BRACKET, "[", 1, 2, 2),
        (types.MojitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 1, 3, 3),
        (types.MojitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 1, 5, 5),
    )

    assert list(t.tokenize(s)) == expected


@pytest.mark.parametrize(
    "input_str, kind, literal",
    [
        ("123", types.MojitoTokenKind.INTEGER_NUMBER, "123"),
        ("-42", types.MojitoTokenKind.INTEGER_NUMBER, "-42"),
        ("3.14", types.MojitoTokenKind.FLOAT_NUMBER, "3.14"),
        ("+.5", types.MojitoTokenKind.FLOAT_NUMBER, "+.5"),
        ('"hello\\"world"', types.MojitoTokenKind.STRING, '"hello\\"world"'),
        ("foo_bar", types.MojitoTokenKind.WORD, "foo_bar"),
        ("answer?", types.MojitoTokenKind.WORD, "answer?"),
        ("a..b", types.MojitoTokenKind.WORD, "a..b"),
    ],
)
def test_valid_literals(input_str, kind, literal):
    tokens = list(t.tokenize(input_str))

    assert len(tokens) == 1
    assert tokens[0] == make_token(kind, literal, 1, 0, len(literal) - 1)


@pytest.mark.parametrize(
    "input_str, literal",
    [
        ('"unterminated', '"unterminated'),
        ('"bad\\', '"bad\\'),
    ],
)
def test_invalid_string(input_str, literal):
    tokens = list(t.tokenize(input_str))

    assert len(tokens) == 1
    assert tokens[0] == make_token(
        types.MojitoTokenKind.INVALID_STRING, literal, 1, 0, len(literal) - 1
    )


def test_mixed_sequence():
    s = "[ foo 123 4.56 bar!? 'baz']"
    expected = tokens(
        (types.MojitoTokenKind.LEFT_SQUARE_BRACKET, "[", 1, 0, 0),
        (types.MojitoTokenKind.WORD, "foo", 1, 2, 4),
        (types.MojitoTokenKind.INTEGER_NUMBER, "123", 1, 6, 8),
        (types.MojitoTokenKind.FLOAT_NUMBER, "4.56", 1, 10, 13),
        (types.MojitoTokenKind.WORD, "bar!?", 1, 15, 19),
        (types.MojitoTokenKind.WORD, "'baz'", 1, 21, 25),
        (types.MojitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 1, 26, 26),
    )

    assert list(t.tokenize(s)) == expected


def test_comment():
    s = "print // this is a comment, not a word sequence"
    expected = [
        make_token(types.MojitoTokenKind.WORD, "print", 1, 0, 4),
    ]

    assert list(t.tokenize(s)) == expected


def source_helper(lines):
    lines = iter(lines)
    return lambda: next(lines, "")


def test_multiline_text_with_line_numbers():
    source = source_helper([": two 1", "1 +", ";"])

    expected = tokens(
        (types.MojitoTokenKind.WORD, ":", 1, 0, 0),
        (types.MojitoTokenKind.WORD, "two", 1, 2, 4),
        (types.MojitoTokenKind.INTEGER_NUMBER, "1", 1, 6, 6),
        (types.MojitoTokenKind.INTEGER_NUMBER, "1", 2, 0, 0),
        (types.MojitoTokenKind.WORD, "+", 2, 2, 2),
        (types.MojitoTokenKind.WORD, ";", 3, 0, 0),
    )

    assert list(t.tokenize(source, line_number=1)) == expected


def test_multiline_text_is_string():
    source = ": two 1\n1 +\n;"

    expected = tokens(
        (types.MojitoTokenKind.WORD, ":", 1, 0, 0),
        (types.MojitoTokenKind.WORD, "two", 1, 2, 4),
        (types.MojitoTokenKind.INTEGER_NUMBER, "1", 1, 6, 6),
        (types.MojitoTokenKind.INTEGER_NUMBER, "1", 2, 0, 0),
        (types.MojitoTokenKind.WORD, "+", 2, 2, 2),
        (types.MojitoTokenKind.WORD, ";", 3, 0, 0),
    )

    assert list(t.tokenize(source, line_number=1)) == expected
