from mohito import tokenizer


def main():
    s = '123'
    rules = []
    print(list(tokenizer.tokenize(s, rules)))


if __name__ == "__main__":
    main()
