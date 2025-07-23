import pytest

import mohito.tokenizer as t
from mohito import types


@pytest.fixture
def tokenizer():
    return t.mohito_tokenizer()


def test_square_brackets(tokenizer):
    s = "[ [] ]"
    expected = [
        types.Token(types.MohitoTokenKind.LEFT_SQUARE_BRACKET, "[", 0, 0),
        types.Token(types.MohitoTokenKind.LEFT_SQUARE_BRACKET, "[", 2, 2),
        types.Token(types.MohitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 3, 3),
        types.Token(types.MohitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 5, 5),
    ]

    assert list(tokenizer(s)) == expected


@pytest.mark.parametrize(
    "input_str, kind, literal",
    [
        ("123", types.MohitoTokenKind.INTEGER_NUMBER, "123"),
        ("-42", types.MohitoTokenKind.INTEGER_NUMBER, "-42"),
        ("3.14", types.MohitoTokenKind.FLOAT_NUMBER, "3.14"),
        ("+.5", types.MohitoTokenKind.FLOAT_NUMBER, "+.5"),
        ('"hello\\"world"', types.MohitoTokenKind.STRING, '"hello\\"world"'),
        ("foo_bar", types.MohitoTokenKind.WORD, "foo_bar"),
        ("answer?", types.MohitoTokenKind.WORD, "answer?"),
        ("a..b", types.MohitoTokenKind.WORD, "a..b"),
    ],
)
def test_valid_literals(input_str, kind, literal, tokenizer):
    tokens = list(tokenizer(input_str))

    assert len(tokens) == 1
    assert tokens[0] == types.Token(kind, literal, 0, len(literal) - 1)


@pytest.mark.parametrize(
    "input_str, literal",
    [
        ('"unterminated', '"unterminated'),
        ('"bad\\', '"bad\\'),
    ],
)
def test_invalid_string(input_str, literal, tokenizer):
    tokens = list(tokenizer(input_str))

    assert len(tokens) == 1
    assert tokens[0] == types.Token(
        types.MohitoTokenKind.INVALID_STRING, literal, 0, len(literal) - 1
    )


def test_mixed_sequence(tokenizer):
    s = "[ foo 123 4.56 bar!? 'baz']"
    expected = [
        types.Token(types.MohitoTokenKind.LEFT_SQUARE_BRACKET, "[", 0, 0),
        types.Token(types.MohitoTokenKind.WORD, "foo", 2, 4),
        types.Token(types.MohitoTokenKind.INTEGER_NUMBER, "123", 6, 8),
        types.Token(types.MohitoTokenKind.FLOAT_NUMBER, "4.56", 10, 13),
        types.Token(types.MohitoTokenKind.WORD, "bar!?", 15, 19),
        types.Token(types.MohitoTokenKind.WORD, "'baz'", 21, 25),
        types.Token(types.MohitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 26, 26),
    ]

    assert list(tokenizer(s)) == expected


def test_comment(tokenizer):
    s = "print // this is a comment, not a word sequence"
    expected = [
        types.Token(types.MohitoTokenKind.WORD, "print", 0, 4),
    ]

    assert list(tokenizer(s)) == expected


def source_helper(lines):
    lines = iter(lines)
    return lambda: next(lines, "")


def test_multiline_text_with_line_numbers():
    source = source_helper([": two 1", "1 +", ";"])

    expected = [
        (1, types.Token(types.MohitoTokenKind.WORD, ":", 0, 0)),
        (1, types.Token(types.MohitoTokenKind.WORD, "two", 2, 4)),
        (1, types.Token(types.MohitoTokenKind.INTEGER_NUMBER, "1", 6, 6)),
        (2, types.Token(types.MohitoTokenKind.INTEGER_NUMBER, "1", 0, 0)),
        (2, types.Token(types.MohitoTokenKind.WORD, "+", 2, 2)),
        (3, types.Token(types.MohitoTokenKind.WORD, ";", 0, 0)),
    ]

    assert list(t.tokenize(source, line_number=1)) == expected


def test_multiline_text_is_string():
    source = ": two 1\n1 +\n;"

    expected = [
        (1, types.Token(types.MohitoTokenKind.WORD, ":", 0, 0)),
        (1, types.Token(types.MohitoTokenKind.WORD, "two", 2, 4)),
        (1, types.Token(types.MohitoTokenKind.INTEGER_NUMBER, "1", 6, 6)),
        (2, types.Token(types.MohitoTokenKind.INTEGER_NUMBER, "1", 0, 0)),
        (2, types.Token(types.MohitoTokenKind.WORD, "+", 2, 2)),
        (3, types.Token(types.MohitoTokenKind.WORD, ";", 0, 0)),
    ]

    assert list(t.tokenize(source, line_number=1)) == expected
