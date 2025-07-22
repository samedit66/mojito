import pytest

from mohito import tokenizer as t


def test_numbers_and_words_tokenizer():
    s = '123 abcd    413'
    rules = [
        t.TokenRule(r'\s+', 'space'),
        t.TokenRule(r'\d+', 'integer'),
        t.TokenRule(r'\w+', 'ident'),
    ]

    expected = [
        t.Token(
            kind='integer',
            value='123',
            start=0,
            end=2,
        ),
        t.Token(
            kind='space',
            value=' ',
            start=3,
            end=3,
        ),
        t.Token(
            kind='ident',
            value='abcd',
            start=4,
            end=7,
        ),
        t.Token(
            kind='space',
            value='    ',
            start=8,
            end=11,
        ),
        t.Token(
            kind='integer',
            value='413',
            start=12,
            end=14,
        ),
    ]

    assert expected == list(t.simple_tokenize(s, rules))


@pytest.mark.parametrize(
    'rules',
    [
        [],
        [t.TokenRule(r'\s+', 'space')],
    ]
)
def test_no_matching_rule(rules):
    s = '123'

    with pytest.raises(t.NoMatchingRuleFoundError):
        list(t.simple_tokenize(s, rules))
