# VERN Project — Handoff & Next Steps

## Overview

VERN is a controlled natural language programming language built on a universal imperative grammar with fully replaceable vocabulary bindings. The core claim is that the executable keywords themselves are the localization target — code written in Swahili, Japanese, Arabic, or English executes identically. The grammar is invariant. The vocabulary is not. This document summarizes where the project stands and what comes next.

---

## Current Status

**Version: v0.1.1 — Specification complete. Interpreter not yet built.**

The project has two complete documents and a live GitHub repository:

- `VERN_spec_v0.1.1.md` — full language specification
- `VERN_Invariant_Grammar_v0.1.1.md` — prior art document with four vocabulary bindings (English, Swahili, Japanese, Arabic)
- Repository: `https://github.com/designercrack-777/VERN`
- License: All Rights Reserved (no license file — full protection, no permissions granted)

The prior art is publicly timestamped. The specification is implementation-ready.

---

## What v0.1.1 Contains

### Core Language Features
- Strict pidgin grammar — one instruction per line, no synonyms, no free-form parsing
- Period-chain reference system — `.valuename.scriptname.script.filename.vern` reading specific to general
- Three primitive data types — Text, Number, True/False
- Explicit type conversion via `convert` keyword — no implicit coercion anywhere
- File I/O — `write` (overwrite) and `append` (additive)
- Scripts — named reusable blocks, called with `run`
- Script return values — `return .value pass to .destination` with pre-declared file-level destinations
- Conditionals — `if / then` with `and`, `or`, `not`
- Loops — `repeat n times` with implicit read-only `loop` counter keyword
- Container system — `#tag` named data pools for context switching and localization
- Extensible vocabulary — `define` keyword maps user words to script calls
- Reference resolution priority — script scope → file scope → imported files → fatal error
- Scoping rules — same name in different scripts is not a conflict, distinct values

### Resolved Issues (from original technical audit)
All six critical issues and all four medium issues from the v0.1 audit are resolved. See `VERN_v0.1.1_Review_Assessment.md` for the full audit resolution table.

### Known v0.1.1 Limitations
- No nested scripts — all scripts must be defined at file level
- No collection types — no lists, arrays, or key-value structures
- No import mechanism — cross-file references exist but loading syntax is unspecified
- No error recovery — fatal errors halt execution, no try/catch equivalent
- No math beyond four basic operators — no rounding, random, exponents, etc.
- No string operations beyond concatenation — no length, search, split, replace

---

## Permanent Design Constraints

These are non-negotiable and must never be violated in future versions:

- **Strict pidgin only** — no synonyms, no optional words, no free-form parsing. Every instruction has one form.
- **No string interpolation** — `"your score is {.score}"` style syntax is explicitly rejected. Use `convert` and `+` concatenation.
- **No implicit type coercion** — all type conversion is explicit via `convert`.
- **Two reserved symbols only** — `.` for containment hierarchy, `#` for container tags. No other special characters.
- **The period chain is exclusive** — `.` belongs only to the file/script/value hierarchy. Containers use `#` and are not part of the period chain.
- **One instruction per line** — always.

---

## v0.2 Priorities

These are the next features in order of importance:

### 1. Collection Types (CRITICAL)
Without lists, real programs hit a ceiling immediately. Every non-trivial program needs the ability to store multiple values in one place and iterate over them.

Proposed syntax (to be fully specced):
```
// creating and populating a list
add .item to .listname
remove .item from .listname
count .listname
show .listname at 3
```

Loop integration will need to handle iterating over a list, not just a fixed count.

### 2. Import Mechanism (CRITICAL)
The spec mentions library files and cross-file references but never defines how a file is loaded. The reference system handles resolution but loading is unspecified. Proposed syntax:
```
import .utilities.vern
```

### 3. Math Completeness (HIGH)
Built-in keywords for common math operations currently missing:
- Rounding
- Square roots and exponents
- Modulo (remainder)
- Random number generation
- Absolute value
- Min and max between two values

### 4. String Operations (HIGH)
Text is nearly read-only beyond concatenation. Needed:
- Length of a text value
- Search within text
- Extract a portion of text
- Replace within text

### 5. Error Recovery (MEDIUM)
Currently one fatal error kills the entire program. For non-programmers this is harsh. A simple try/catch equivalent would significantly improve robustness. Not yet agreed on syntax — needs design work.

### 6. Date and Time (MEDIUM)
Ubiquitous in real programs. Current date, current time, difference between dates. Needs design work.

---

## v0.3 and Beyond

- Nested scripts (significant complexity, low priority)
- Short-circuit boolean evaluation (performance, low priority)
- File operations beyond read/write (check if file exists, delete, list directory)
- Standard library — pre-built container files and define libraries shipping with VERN
- Package system for community-contributed bindings and libraries

---

## Building an Interpreter

The spec is implementation-ready. A minimal Python interpreter is the recommended first build. Priority order for implementation:

1. Tokenizer — read a `.vern` file, apply vocabulary binding, produce invariant tokens
2. Parser — validate token sequences against the invariant grammar
3. Executor — run the parsed instruction tree
4. Error logger — implement the fatal/non-fatal error scale with log output
5. File I/O — implement `read`, `write`, `append`
6. Container resolution — implement the `#tag` priority hierarchy

Start with the English binding only. Localization support can be layered on after the core executes correctly.

---

## Key Design Decisions Already Made

These came up during v0.1.1 development and should not be re-litigated without strong reason:

- `loop` is a bare keyword with no period prefix — not `.loop` — to distinguish it from user-defined values
- `return` uses `pass to` as a compound token for the destination — `return .value pass to .destination`
- `pass to` can only assign to a pre-declared file-level value — it cannot create values
- Container `#tags` sit after value references and before file chain — `.greeting #english.languages.vern`
- `run` can carry a container tag — `run .greet.script #english` — overriding any definition-level tag
- File-level values are disambiguated by filename — `.score.filename` not a new keyword
- String interpolation is permanently off the table
- `convert` is non-destructive — always creates a new named value, original is unchanged
- `ask` always returns text — caller is responsible for converting to number if needed

---

## Repository & Identity

- GitHub: `https://github.com/designercrack-777/VERN`
- Attribution: The VERN Project (no personal name attached)
- License: All Rights Reserved — no permissions granted, full protection
- License can be changed later to CC BY when community participation is desired — changing from restrictive to permissive is clean, the reverse is not

---

*The VERN Project — 2026*
