from mojito import executor
from mojito import types


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


# Everything below was written by LLM just to quick check the prototype...


def _pop2_numbers(word, state):
    try:
        b = state.pop()
        a = state.pop()
    except Exception:
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.value}' expected 2 elements on the stack")
    if not (isinstance(a, types.Number) and isinstance(b, types.Number)):
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.value}' expected two numbers, got {type(a).__name__} and {type(b).__name__}"
        )
    return a, b


@vocab.builtin("<")
def lt(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, float(a.value < b.value)))


@vocab.builtin(">")
def gt(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, float(a.value > b.value)))


@vocab.builtin("+")
def add(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, a.value + b.value))


@vocab.builtin("-")
def sub(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, a.value - b.value))


@vocab.builtin("*")
def mul(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, a.value * b.value))


@vocab.builtin("/")
def div(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    if b.value == 0:
        loc = word.location
        raise RuntimeError(f"{loc}: Division by zero in '{word.value}'")
    state.push(types.Number(word.location, a.value / b.value))


@vocab.builtin("mod")
def mod(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    if b.value == 0:
        loc = word.location
        raise RuntimeError(f"{loc}: Modulo by zero in '{word.value}'")
    state.push(types.Number(word.location, a.value % b.value))


@vocab.builtin("if")
def if_combinator(word, state, vocab, read_word, execute):
    try:
        false_branch = state.pop()
        true_branch = state.pop()
        cond = state.pop()
    except Exception:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.value}' expected 3 elements on the stack (cond true-branch false-branch)"
        )
    if not isinstance(false_branch, executor.Closure) or not isinstance(
        true_branch, executor.Closure
    ):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.value}' expected quotations for branches")
    if not isinstance(cond, types.Number):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.value}' expected a number as condition")
    if cond.value:
        execute(true_branch)
    else:
        execute(false_branch)


@vocab.builtin("bi")
def bi(word, state, vocab, read_word, execute):
    try:
        q2 = state.pop()
        q1 = state.pop()
        x = state.pop()
    except Exception:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.value}' expected 3 elements on the stack (x q1 q2)"
        )
    if not isinstance(q1, executor.Closure) or not isinstance(q2, executor.Closure):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.value}' expected quotations for bi")
    state.push(x)
    execute(q1)
    state.push(x)
    execute(q2)


@vocab.builtin("when")
def when(word, state, vocab, read_word, execute):
    try:
        q = state.pop()
        cond = state.pop()
    except Exception:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.value}' expected 2 elements on the stack (cond quotation)"
        )
    if not isinstance(q, executor.Closure):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.value}' expected a quotation for when")
    if not isinstance(cond, types.Number):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.value}' expected a number as condition")
    if cond.value:
        execute(q)


@vocab.builtin(":")
def define(word, state, vocab, read_word, execute):
    # Read the function name (should be a Word)
    func_name = read_word()
    if func_name is None or not hasattr(func_name, "name"):
        loc = word.location
        raise RuntimeError(f"{loc}: ':' expected a word for function name")
    # Read body until ';'
    body = []
    while True:
        w = read_word()
        if w is None:
            loc = word.location
            raise RuntimeError(f"{loc}: ':' expected ';' to end definition")
        if hasattr(w, "name") and w.name == ";":
            break
        body.append(w)
    closure = executor.Closure(types.Quotation(body), vocab.child())
    vocab.define_word(func_name.name, closure)


@vocab.builtin("say")
def say(word, state, vocab, read_word, execute):
    try:
        w = state.pop()
        match w:
            case types.Number() | types.String():
                print(w.value)
            case types.Closure():
                print("<closure>")

    except IndexError:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.value}' expected a value on top of the stack"
        )
