from mohito import executor
from mohito import types


vocab = executor.Vocab(None, {}, {})


# Example builtins
@vocab.builtin("*")
def mul(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(a * b)


@vocab.builtin("dup")
def dup(state, vocab, read_word, execute):
    state.dup()


@vocab.builtin("print")
def print_(state, vocab, read_word, execute):
    val = state.data_stack.pop()
    print(val)


@vocab.builtin(":")
def define(state, vocab, read_word, execute):
    func_name = read_word()

    # Read body until ';'
    body = []
    while True:
        w = read_word()
        if isinstance(w, types.Word) and w.name == ";":
            break
        body.append(w)

    closure = executor.Closure(types.Quotation(body), vocab.child())
    vocab.define_word(func_name.name, closure)


@vocab.builtin("+")
def add(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(a + b)


@vocab.builtin("-")
def sub(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(a - b)


@vocab.builtin("/")
def div(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(a / b)


@vocab.builtin("mod")
def mod(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(a % b)


@vocab.builtin("swap")
def swap(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(b)
    state.data_stack.append(a)


@vocab.builtin("drop")
def drop(state, vocab, read_word, execute):
    state.drop()


@vocab.builtin("over")
def over(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(a)
    state.data_stack.append(b)
    state.data_stack.append(a)


@vocab.builtin("=")
def eq(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(float(a == b))


@vocab.builtin("<")
def lt(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(float(a < b))


@vocab.builtin(">")
def gt(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(float(a > b))


@vocab.builtin("not")
def not_(state, vocab, read_word, execute):
    a = state.data_stack.pop()
    state.data_stack.append(float(not a))


@vocab.builtin("and")
def and_(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(float(bool(a) and bool(b)))


@vocab.builtin("or")
def or_(state, vocab, read_word, execute):
    b = state.data_stack.pop()
    a = state.data_stack.pop()
    state.data_stack.append(float(bool(a) or bool(b)))


@vocab.builtin("apply")
def apply(state, vocab, read_word, execute):
    closure = state.data_stack.pop()
    if not isinstance(closure, executor.Closure):
        raise RuntimeError("apply expects a quotation/closure on the stack")
    # Execute the closure body in its own vocab
    execute(closure.body.items, vocab)


if __name__ == "__main__":
    # Setup builtins
    ex = executor.Executor(vocab)
    # Simple program: define square, use it, print result
    code = ": square dup * ; 3 square print\n[ 2 3 + ] apply print"  # Should print 9 and then 5
    ex.run(code)
