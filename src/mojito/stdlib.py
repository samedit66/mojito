from mojito import executor


vocab = executor.Vocab(
    parent_vocab=None,
    builtins={},
    user_defined={},
)


@vocab.builtin("dup")
def dup(word, state, vocab, read_word, execute):
    try:
        state.dup()
    except IndexError:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.value}' expected a single element on top of the stack"
        )


@vocab.builtin("drop")
def drop(word, state, vocab, read_word, execute):
    try:
        state.pop()
    except IndexError:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.value}' expected a single element on top of the stack"
        )


@vocab.builtin("dip")
def dip(word, state, vocab, read_word, execute):
    try:
        quotation = state.pop()
        top = state.pop()
        execute(quotation)
        state.push(top)
    except IndexError:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.value}' expected a closure on top of the stack"
        )


@vocab.builtin("swap")
def swap(word, state, vocab, read_word, execute):
    try:
        a, b = state.pop(), state.pop()
        state.push(a)
        state.push(b)
    except IndexError:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.value}' expected 2 elements on top of the stack"
        )
