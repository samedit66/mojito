from mohito import tokenizer


def main():
    s = 'def inc { + 1 }'
    mt = tokenizer.mohito_tokenizer()
    print(list(mt(s)))


if __name__ == "__main__":
    main()
