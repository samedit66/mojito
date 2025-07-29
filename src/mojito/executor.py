from mojito import types
from mojito import parser


class Executor:
    def __init__(self, vocab: types.Vocab):
        self.vocab = vocab
        self.state = types.InternalState([])

    def run(self, source):
        ast = types.Quotation(parser.parse(source).items)
        closure = types.Closure(ast, self.vocab)
        return self.execute(closure)

    def execute(self, closure):
        def reader(ws):
            i = 0

            def aux():
                nonlocal i
                if i < len(ws):
                    r = ws[i]
                    i += 1
                    return r
                return None

            return aux

        read_word = reader(closure.body.items)
        while word := read_word():
            match word:
                case types.Number() | types.String():
                    self.state.push(word)
                case types.Quotation():
                    closure = types.Closure(word, closure.vocab)
                    self.state.push(closure)
                case types.Word(name=name):
                    func = closure.vocab.lookup(name)
                    if not func:
                        raise RuntimeError(f"I don't know the word: {name}")

                    if isinstance(func, types.Closure):
                        self.execute(func)
                    else:
                        func(word, self.state, closure.vocab, read_word, self.execute)
