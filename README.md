<div align="center">
  <a href="https://github.com/samedit66/mojito">
    <img src="https://github.com/user-attachments/assets/81ea07e5-82be-4782-9b7b-9e1f35b67458" alt="mojito logo" width="180" height="180" />
  </a>
  <h1>mojito🍋‍🟩</h1>
  <p><em>A minimalist concatenative language in pure Python</em></p>
</div>

---

## Overview

**mojito** is a toy-grade, stack-based concatenative language implemented in under 1,000 lines of pure Python. Born as a weekend experiment, it’s designed for:
- Hands-on exploration of [Forth](https://en.wikipedia.org/wiki/Forth_(programming_language))-style evaluation.
- Learning how parsers, runtimes, and vocabularies interplay.
- Rapid prototyping of new language ideas.

It deliberately forgoes heavy tooling: no module system, no IDE plugins, just a minimal REPL, core primitives, and (probably) clear error messages.

**mojito** is like a younger brother of [Factor](https://factorcode.org/) and a cousin of [xi](https://github.com/thesephist/xi).

---

## Features

- **Stack-based approach**

  Embrace a data‑flow mindset: every operation consumes and produces values on a shared stack, encouraging you to think in terms of pipelines and transformations rather than variables and assignments.

- **Quotation‑driven, functional style**

  Quotations (`[ … ]`) serve as lightweight, anonymous functions. Compose, nest, and pass them around to build clear, declarative logic—no boilerplate lambdas or callbacks required.

- **Unrestricted extensibility**
 
  Design new words and DSLs that fit your domain perfectly. Every primitive sits alongside your custom definitions, so you can grow the language organically to express ideas as clearly and succinctly as possible.
  
---

## Examples

Let’s write a simple, classic program which computes the factorial of a given number in three different languages—Python, Clojure, and mojito—illustrating three ways of thinking with different syntax but the same underlying idea.

### Python (Imperative / Functional)
```python
def fact(n):
    """Classic recursive factorial."""
    if n <= 1:
        return 1
    return n * fact(n - 1)

print(fact(4))  # ⇒ 24
```

### Clojure (Lisp‑style Functional)
```clojure
(defn fact [n]
  (if (> n 1)
    (* n (fact (dec n)))
    1))

(println (fact 4))  ; ⇒ 24
```

### mojito (Concatenative Functional)

```js
: fact
  dup 1 > 
  [dup 1 - fact *]  // if greater than 1, recurse
  [drop 1]          // else, clean up and return 1
  if
;
  
4 fact .  // ⇒ 24.0
```

mojito may look at first glance like inscrutable ciphertext—rows of stack manipulations and bracketed quotations that could double as an ancient codebook—but beneath its “encrypted” surface lies a remarkably powerful and expressive core. Let's break it down.

Firstly, the `:` word (we call functions “words”) tells the mojito interpreter to start “compiling” a new definition—yes, that’s the extent of mojito’s syntax! Next comes the word name, fact in our case.

1. `dup`

    Duplicates the top of the stack.

    - If the stack is `… 2 3`, then dup yields `… 2 3 3`.

    - Here, it makes a copy of `n` so we can both test it and later multiply by it.

2. `1 >`

    Compares the top of the stack (our duplicated `n`) to `1`.

    - If n > 1, it pushes a truthy flag (e.g. `1`); otherwise, a falsy flag (e.g. `0`). __I promise I add booleans some day__.

3. `[dup 1 - fact *]`

    A quotation: an anonymous code block that

    - `dup`: copies `n` again

    - `1 -`: decrements it (`n - 1`)

    - `fact`: recursively calls our function on `n - 1`

    - `*`: multiplies the result by the original `n`

    This block embodies the "recursive case."

4. `[drop 1]`

    The “base case” quotation.

    - `drop`: removes the duplicated `n` (when `n <= 1`)

    - `1`: pushes the result for `0!` or `1!`.

5. `if`

    Consumes the boolean flag and the two quotations:

    - If the flag is truthy, executes the first quotation.

    - Otherwise, executes the second.

    After this, the stack holds exactly one number: `n!`.

6. `;`
    
    Ends the word definition (it's also a function! Kinda...).

So, when you run:

```forth
4 fact .
```

- `4` pushes `4` onto the stack.

- `fact` executes the steps above, leaving there `24.0`.

- `.` pops and prints that value.

mojito forces you to think of programs as pipelines of data transformation: values flow through a shared stack, operators sculpt them, and quotations wrap behavior into first‑class chunks that can be passed around, combined, or executed on demand.

## Installation

You'll need to have [uv](https://github.com/astral-sh/uv) installed, then:

```bash
git clone https://github.com/samedit66/mojito
cd mojito
uv run main.py
```

This will launch the mojito REPL. Try out a few simple stack experiments:

```bash
mojito REPL. Type 'exit' or Ctrl-D to quit.
>>> 2 3 + .
5.0
>>> 10 dup * .          // compute 10²
100.0
>>> [ 1 2 + ] apply .   // run the quotation on the top-of-stack
3.0
>>> : square dup * ;    // define a square function
>>> 7 square .
49.0
>>> exit
Bye!
```

- `2 3 + .` pushes `2` and `3`, adds them, then prints `5.0`.

- `dup *` duplicates the top value and multiplies, yielding a square.

- `[ ... ] apply` takes the quotation off the stack and executes it.

- `: square dup * ;` defines a new word, square, which you can reuse freely.

That’s all it takes to get started—welcome to your minimalist playground for exploring concatenative, stack‑based, point‑free programming!