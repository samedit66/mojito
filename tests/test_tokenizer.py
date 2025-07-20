import pytest

from mohito import tokenizer


def test_numbers_and_words_tokenizer():
    s = '123 abcd    413'
    rules = [
        tokenizer.TokenRule(r'\s+', 'space'),
        tokenizer.TokenRule(r'\d+', 'integer'),
        tokenizer.TokenRule(r'\w+', 'ident'),
    ]

    expected = [
        tokenizer.Token(
            kind='integer',
            value='123',
            start=0,
            end=2,
        ),
        tokenizer.Token(
            kind='space',
            value=' ',
            start=3,
            end=3,
        ),
        tokenizer.Token(
            kind='ident',
            value='abcd',
            start=4,
            end=7,
        ),
        tokenizer.Token(
            kind='space',
            value='    ',
            start=8,
            end=11,
        ),
        tokenizer.Token(
            kind='integer',
            value='413',
            start=12,
            end=14,
        ),
    ]

    assert expected == list(tokenizer.tokenize(s, rules))


@pytest.mark.parametrize(
    'rules',
    [
        [],
        [tokenizer.TokenRule(r'\s+', 'space')],
    ]
)
def test_no_matching_rule(rules):
    s = '123'

    with pytest.raises(tokenizer.NoMatchingRuleFoundError):
        list(tokenizer.tokenize(s, rules))
