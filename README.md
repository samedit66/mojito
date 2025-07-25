<div align="center">
  <a href="https://github.com/samedit66/mojito">
    <img src="https://github.com/user-attachments/assets/81ea07e5-82be-4782-9b7b-9e1f35b67458" alt="mojito logo" width="180" height="180" />
  </a>
  <h1>mojito</h1>
  <p><em>A minimalist concatenative language in pure Python</em></p>
</div>

---

## Overview

**mojito** is a toy-grade, stack-based concatenative language implemented in under 1,000 lines of pure Python. Born as a weekend experiment, it’s designed for:
- Hands-on exploration of [Forth](https://en.wikipedia.org/wiki/Forth_(programming_language))-style evaluation.
- Learning how parsers, runtimes, and vocabularies interplay.
- Rapid prototyping of new language ideas.

It deliberately forgoes heavy tooling: no module system, no IDE plugins, just a minimal REPL, core primitives, and (probably) clear error messages.

**mojito** is a like a younger brother of [Factor](https://factorcode.org/) and a cousin of [xi](https://github.com/thesephist/xi).

---

## Examples

A classic resursive factorial:

```js
: fact 1 > [dup 1 - fact *] [drop 1] ;
4 fact . // Should print 24.0
```
