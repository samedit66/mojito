import pytest

from mohito import tokenizer as t


@pytest.fixture
def tokenizer():
    return t.mohito_tokenizer()


def test_square_brackets(tokenizer):
    s = "[ [] ]"
    expected = [
        t.Token(t.MohitoTokenKind.LEFT_SQUARE_BRACKET, "[", 0, 0),
        t.Token(t.MohitoTokenKind.LEFT_SQUARE_BRACKET, "[", 2, 2),
        t.Token(t.MohitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 3, 3),
        t.Token(t.MohitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 5, 5),
    ]

    assert list(tokenizer(s)) == expected


@pytest.mark.parametrize(
    "input_str, kind, literal",
    [
        ("123", t.MohitoTokenKind.INTEGER_NUMBER, "123"),
        ("-42", t.MohitoTokenKind.INTEGER_NUMBER, "-42"),
        ("3.14", t.MohitoTokenKind.FLOAT_NUMBER, "3.14"),
        ("+.5", t.MohitoTokenKind.FLOAT_NUMBER, "+.5"),
        ('"hello\\"world"', t.MohitoTokenKind.STRING, '"hello\\"world"'),
        ("foo_bar", t.MohitoTokenKind.WORD, "foo_bar"),
        ("answer?", t.MohitoTokenKind.WORD, "answer?"),
        ("a..b", t.MohitoTokenKind.WORD, "a..b")
    ]
)
def test_valid_literals(input_str, kind, literal, tokenizer):
    tokens = list(tokenizer(input_str))

    assert len(tokens) == 1
    assert tokens[0] == t.Token(kind, literal, 0, len(literal) - 1)


@pytest.mark.parametrize(
    "input_str, literal",
    [
        ('"unterminated', '"unterminated'),
        ('"bad\\', '"bad\\'),
    ]
)
def test_invalid_string(input_str, literal, tokenizer):
    tokens = list(tokenizer(input_str))

    assert len(tokens) == 1
    assert tokens[0] == t.Token(
        t.MohitoTokenKind.INVALID_STRING, literal, 0, len(literal) - 1
    )


def test_mixed_sequence(tokenizer):
    s = "[ foo 123 4.56 bar!? 'baz']"
    expected = [
        t.Token(
            t.MohitoTokenKind.LEFT_SQUARE_BRACKET, "[", 0, 0
        ),
        t.Token(
            t.MohitoTokenKind.WORD, "foo", 2, 4
        ),
        t.Token(
            t.MohitoTokenKind.INTEGER_NUMBER, "123", 6, 8
        ),
        t.Token(
            t.MohitoTokenKind.FLOAT_NUMBER, "4.56", 10, 13
        ),
        t.Token(
            t.MohitoTokenKind.WORD, "bar!?", 15, 19
        ),
        t.Token(
            t.MohitoTokenKind.WORD, "'baz'", 21, 25
        ),
        t.Token(
            t.MohitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 26, 26
        ),
    ]

    assert list(tokenizer(s)) == expected


def test_comment(tokenizer):
    s = "print // this is a comment, not a word sequence"
    expected = [
        t.Token(t.MohitoTokenKind.WORD, "print", 0, 4),
    ]

    assert list(tokenizer(s)) == expected


def test_multiline_text():
    lines = iter([": sum", "0 [+] reduce", ";"])
    def source():
        return next(lines, "")
    
    expected = [
        # line 1: ": sum"
        t.Token(t.MohitoTokenKind.WORD, ":",0, 0),
        t.Token(t.MohitoTokenKind.WORD, "sum",  2, 4),
        # line 2: "0 [+] reduce"
        t.Token(t.MohitoTokenKind.INTEGER_NUMBER, "0", 0, 0),
        t.Token(t.MohitoTokenKind.LEFT_SQUARE_BRACKET, "[", 2, 2),
        t.Token(t.MohitoTokenKind.WORD, "+", 3, 3),
        t.Token(t.MohitoTokenKind.RIGHT_SQUARE_BRACKET, "]", 4, 4),
        t.Token(t.MohitoTokenKind.WORD, "reduce", 6, 11),
        # line 3: ";"
        t.Token(t.MohitoTokenKind.WORD, ";", 0, 0),
    ]

    assert list(t.tokenize(source)) == expected
