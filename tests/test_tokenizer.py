import pytest

import mojito.tokenizer as t
from mojito import types


def test_numbers_and_words_tokenizer():
    s = "123 abcd    413"
    rules = [
        types.TokenRule(r"\s+", "space"),
        types.TokenRule(r"\d+", "integer"),
        types.TokenRule(r"\w+", "ident"),
    ]

    expected = [
        types.Token(
            kind="integer",
            value="123",
            start=0,
            end=2,
        ),
        types.Token(
            kind="space",
            value=" ",
            start=3,
            end=3,
        ),
        types.Token(
            kind="ident",
            value="abcd",
            start=4,
            end=7,
        ),
        types.Token(
            kind="space",
            value="    ",
            start=8,
            end=11,
        ),
        types.Token(
            kind="integer",
            value="413",
            start=12,
            end=14,
        ),
    ]

    assert expected == list(t.simple_tokenize(s, rules))


@pytest.mark.parametrize(
    "rules",
    [
        [],
        [types.TokenRule(r"\s+", "space")],
    ],
)
def test_no_matching_rule(rules):
    s = "123"

    with pytest.raises(t.NoMatchingRuleFoundError):
        list(t.simple_tokenize(s, rules))
