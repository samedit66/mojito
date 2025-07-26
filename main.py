from mojito import executor
from mojito import stdlib


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
            except Exception as e:
                print(f"Error: {e}")
        except EOFError:
            print("\nBye!")
            break


if __name__ == "__main__":
    repl()
