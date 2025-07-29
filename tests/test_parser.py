import pytest

import mojito.parser as parser
import mojito.types as types


def test_parse_integer_number():
    seq = parser.parse("123")
    assert isinstance(seq, types.Program)
    assert len(seq) == 1
    elem = seq[0]
    assert isinstance(elem, types.Number)
    assert elem.value == 123.0


def test_parse_float_number():
    seq = parser.parse("-3.14 +2.5")
    # parse processes as two tokens: -3.14 and +2.5
    assert len(seq) == 2
    assert pytest.approx(seq[0].value) == -3.14
    assert pytest.approx(seq[1].value) == 2.5


def test_parse_string_literal():
    seq = parser.parse('"hello\\nworld"')
    assert len(seq) == 1
    elem = seq[0]
    assert isinstance(elem, types.String)
    # The token value includes quotes and escape sequences
    assert elem.value == "hello\\nworld"


def test_parse_word():
    seq = parser.parse("foo BAR123 _baz")
    assert len(seq) == 3
    assert all(isinstance(elem, types.Word) for elem in seq)
    assert [elem.name for elem in seq] == ["foo", "BAR123", "_baz"]


def test_parse_mixed_primitives():
    seq = parser.parse("42 foo 'ignored' [nested]")
    assert isinstance(seq, types.Program)
    assert len(seq) == 4
    assert isinstance(seq[0], types.Number)
    assert isinstance(seq[1], types.Word)
    assert isinstance(seq[2], types.Word)
    assert isinstance(seq[3], types.Quotation)
    assert isinstance(seq[3][0], types.Word)


def test_parse_simple_sequence():
    seq = parser.parse("[1 2 3]")
    # One top-level Sequence containing three Numbers
    assert len(seq) == 1
    inner = seq[0]
    assert isinstance(inner, types.Quotation)
    assert [n.value for n in inner] == [1.0, 2.0, 3.0]


def test_parse_nested_sequence():
    seq = parser.parse("[ a [ b c ] d ]")
    assert len(seq) == 1
    outer = seq[0]
    assert isinstance(outer, types.Quotation)
    assert isinstance(outer[0], types.Word) and outer[0].name == "a"
    assert isinstance(outer[1], types.Quotation)
    assert [w.name for w in outer[1]] == ["b", "c"]
    assert isinstance(outer[2], types.Word) and outer[2].name == "d"


def test_unmatched_left_bracket_raises():
    with pytest.raises(parser.MojitoSyntaxError, match=r"quotation was not closed"):
        parser.parse("[1 2 3")


def test_unmatched_right_bracket_raises():
    with pytest.raises(parser.MojitoSyntaxError, match=r"unexpected quotation end"):
        parser.parse("1 2] 3")


def test_invalid_string_literal_raises():
    with pytest.raises(parser.MojitoSyntaxError, match=r"invalid string literal"):
        parser.parse('"unterminated string')
