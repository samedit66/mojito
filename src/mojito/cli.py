import argparse
import pathlib

from mojito import (
    executor,
    stdlib,
)


MOJITO_VERSION = "mojito 0.1.0"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", nargs="?")
    parser.add_argument("--version", action="store_true")
    args = parser.parse_args()
    return args


def repl():
    ex = executor.Executor(stdlib.vocab)
    print("mojito REPL. Type 'exit' or Ctrl-D to quit.")
    while True:
        try:
            line = input(">>> ")
            if line.strip() in {"exit", "quit"}:
                print("Bye!")
                break
            if not line.strip():
                continue
            try:
                ex.run(line)
                print(ex.state)
            except Exception as e:
                print(f"Error: {e}")
        except EOFError:
            print("\nBye!")
            break


def run_file(file_path):
    ex = executor.Executor(stdlib.vocab)
    text = pathlib.Path(file_path).read_text()
    ex.run(text)


def main():
    args = parse_args()

    if args.version:
        print(MOJITO_VERSION)
    elif args.input_file:
        run_file(args.input_file)
    else:
        repl()


if __name__ == "__main__":
    main()
