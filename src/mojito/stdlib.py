from mojito import types
from mojito.types import runtime


vocab = types.Vocab(
    parent_vocab=None,
    builtins={},
    user_defined={},
)


@vocab.define("dup")
def dup(word, state, vocab, read_word, execute):
    try:
        state.dup()
    except IndexError:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.name}' expected a single element on top of the stack"
        )


@vocab.define("drop")
def drop(word, state, vocab, read_word, execute):
    try:
        state.pop()
    except IndexError:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.name}' expected a single element on top of the stack"
        )


@vocab.define("dip")
def dip(word, state, vocab, read_word, execute):
    try:
        quotation = state.pop()
        top = state.pop()
        execute(quotation)
        state.push(top)
    except IndexError:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.name}' expected a closure on top of the stack"
        )


@vocab.define("swap")
def swap(word, state, vocab, read_word, execute):
    try:
        a, b = state.pop(), state.pop()
        state.push(a)
        state.push(b)
    except IndexError:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.name}' expected 2 elements on top of the stack"
        )


# Everything below was written by LLM just to quick check the prototype...


def _pop2_numbers(word, state):
    try:
        b = state.pop()
        a = state.pop()
    except Exception:
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.name}' expected 2 elements on the stack")
    if not (isinstance(a, types.Number) and isinstance(b, types.Number)):
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.name}' expected two numbers, got {type(a).__name__} and {type(b).__name__}"
        )
    return a, b


@vocab.define("<")
def lt(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, float(a.value < b.value)))


@vocab.define(">")
def gt(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, float(a.value > b.value)))


@vocab.define("+")
def add(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, a.value + b.value))


@vocab.define("-")
def sub(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, a.value - b.value))


@vocab.define("*")
def mul(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    state.push(types.Number(word.location, a.value * b.value))


@vocab.define("/")
def div(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    if b.value == 0:
        loc = word.location
        raise RuntimeError(f"{loc}: Division by zero in '{word.name}'")
    state.push(types.Number(word.location, a.value / b.value))


@vocab.define("mod")
def mod(word, state, vocab, read_word, execute):
    a, b = _pop2_numbers(word, state)
    if b.value == 0:
        loc = word.location
        raise RuntimeError(f"{loc}: Modulo by zero in '{word.name}'")
    state.push(types.Number(word.location, a.value % b.value))


@vocab.define("if")
def if_combinator(word, state, vocab, read_word, execute):
    try:
        false_branch = state.pop()
        true_branch = state.pop()
        cond = state.pop()
    except Exception:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.name}' expected 3 elements on the stack (cond true-branch false-branch)"
        )
    if not isinstance(false_branch, types.Closure) or not isinstance(
        true_branch, types.Closure
    ):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.name}' expected quotations for branches")
    if not isinstance(cond, types.Number):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.name}' expected a number as condition")
    if cond.value:
        execute(true_branch)
    else:
        execute(false_branch)


@vocab.define("bi")
def bi(word, state, vocab, read_word, execute):
    try:
        q2 = state.pop()
        q1 = state.pop()
        x = state.pop()
    except Exception:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.name}' expected 3 elements on the stack (x q1 q2)"
        )
    if not isinstance(q1, types.Closure) or not isinstance(q2, types.Closure):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.name}' expected quotations for bi")
    state.push(x)
    execute(q1)
    state.push(x)
    execute(q2)


@vocab.define("when")
def when(word, state, vocab, read_word, execute):
    try:
        q = state.pop()
        cond = state.pop()
    except Exception:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.name}' expected 2 elements on the stack (cond quotation)"
        )
    if not isinstance(q, types.Closure):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.name}' expected a quotation for when")
    if not isinstance(cond, types.Number):
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.name}' expected a number as condition")
    if cond.value:
        execute(q)


@vocab.define("apply")
def apply(word, state, vocab, read_word, execute):
    try:
        q = state.pop()
    except Exception:
        loc = word.location
        raise RuntimeError(
            f"{loc}: '{word.name}' expected 1 element on the stack (quotation)"
        )

    execute(q)


@vocab.define(":")
def define(word, state, vocab, read_word, execute):
    # Read the function name (should be a Word)
    func_name = read_word()
    if func_name is None or not isinstance(func_name, types.Word):
        loc = word.location
        raise RuntimeError(f"{loc}: ':' expected a word for function name")
    # Read body until ';'
    body = []
    level = 0
    while True:
        w = read_word()
        if w is None:
            loc = word.location
            raise RuntimeError(f"{loc}: ':' expected ';' to end definition")

        # The following allows us to define local functions -- no Forth supported that
        if isinstance(w, types.Word):
            if w.name == ":":
                level += 1
            elif w.name == ";":
                if level == 0:
                    break
                level -= 1

        body.append(w)
    closure = types.Closure(types.Quotation(body), vocab.offspring())
    vocab.define(func_name.name, closure)


@vocab.define("put")
@vocab.define(".")
def println(word, state, vocab, read_word, execute):
    try:
        print(runtime.as_string(state.pop()))

    except IndexError:
        loc = word.location
        raise RuntimeError(f"{loc}: '{word.name}' expected a value on top of the stack")
