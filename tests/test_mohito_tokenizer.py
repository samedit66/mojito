import pytest

from mohito import tokenizer


@pytest.fixture
def mohito_tok():
    return tokenizer.mohito_tokenizer()


def test_brackets_and_punctuation(mohito_tok):
    s = "[]{},->"
    expected = [
        tokenizer.Token(tokenizer.MohitoTokenKind.LEFT_SQUARE_BRACKET, "[", 0, 0),
        tokenizer.Token(tokenizer.MohitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 1, 1),
        tokenizer.Token(tokenizer.MohitoTokenKind.LEFT_CURLY_BRACKET, "{", 2, 2),
        tokenizer.Token(tokenizer.MohitoTokenKind.RIGHT_CURLY_BRACKET, "}", 3, 3),
        tokenizer.Token(tokenizer.MohitoTokenKind.COMMA, ",", 4, 4),
        tokenizer.Token(tokenizer.MohitoTokenKind.ARROW, "->", 5, 6),
    ]
    result = list(mohito_tok(s))
    assert result == expected


@pytest.mark.parametrize("s,kind,value", [
    ("123", tokenizer.MohitoTokenKind.INTEGER_NUMBER, "123"),
    ("3.14",tokenizer.MohitoTokenKind.FLOAT_NUMBER, "3.14"),
    ('"hello\\"world"', tokenizer.MohitoTokenKind.STRING, '"hello\\"world"'),
    ("foo", tokenizer.MohitoTokenKind.WORD, "foo"),
    ("prime?", tokenizer.MohitoTokenKind.WORD, "prime?"),
    ("x'", tokenizer.MohitoTokenKind.WORD, "x'"),
    ("change!", tokenizer.MohitoTokenKind.WORD, "change!"),
])
def test_valid_literals(s, kind, value, mohito_tok):
    result = list(mohito_tok(s))
    assert len(result) == 1
    expected = tokenizer.Token(kind, value, 0, len(value) - 1)
    assert result[0] == expected


@pytest.mark.parametrize("s,kind,value", [
    ("123a", tokenizer.MohitoTokenKind.INVALID_INTEGER_NUMBER, "123a"),
    ("3.14.5", tokenizer.MohitoTokenKind.INVALID_FLOAT_NUMBER, "3.14.5"),
    ("12.a", tokenizer.MohitoTokenKind.INVALID_FLOAT_NUMBER, "12.a"),
    ('"abc', tokenizer.MohitoTokenKind.INVALID_STRING, '"abc'),
])
def test_invalid_literals(s, kind, value, mohito_tok):
    result = list(mohito_tok(s))
    assert len(result) == 1
    expected = tokenizer.Token(kind, value, 0, len(value) - 1)
    assert result[0] == expected


def test_sequence_mixed(mohito_tok):
    s = " [ foo , 42 ->bar!? 'baz'] "
    expected = [
        tokenizer.Token(tokenizer.MohitoTokenKind.LEFT_SQUARE_BRACKET, "[", 1, 1),
        tokenizer.Token(tokenizer.MohitoTokenKind.WORD, "foo", 3, 5),
        tokenizer.Token(tokenizer.MohitoTokenKind.COMMA, ",", 7, 7),
        tokenizer.Token(tokenizer.MohitoTokenKind.INTEGER_NUMBER, "42", 9, 10),
        tokenizer.Token(tokenizer.MohitoTokenKind.ARROW, "->", 12, 13),
        tokenizer.Token(tokenizer.MohitoTokenKind.WORD, "bar!?", 14, 18),
        tokenizer.Token(tokenizer.MohitoTokenKind.WORD, "'baz'", 20, 24),
        tokenizer.Token(tokenizer.MohitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 25, 25),
    ]
    result = list(mohito_tok(s))
    assert result == expected
