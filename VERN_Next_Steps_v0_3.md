# VERN Project — Handoff & Next Steps

## Overview

VERN is a controlled natural language programming language built on a universal imperative grammar with fully replaceable vocabulary bindings. The core claim is that the executable keywords themselves are the localization target — code written in Swahili, Japanese, Arabic, or English executes identically. The grammar is invariant. The vocabulary is not. This document summarizes where the project stands and what comes next.

---

## Current Status

**Version: v0.2 — Specification complete. Interpreter not yet built.**

The project has two authoritative documents and a live GitHub repository:

- `VERN_spec_v0_2.md` — full language specification
- `VERN_Invariant_Grammar_v0_2.md` — prior art document with four vocabulary bindings (English, Swahili, Japanese, Arabic), all verified collision-free
- Repository: `https://github.com/designercrack-777/VERN`
- License: All Rights Reserved (no license file — full protection, no permissions granted)

The prior art is publicly timestamped. The specification is implementation-ready.

---

## What v0.2 Contains

### Core Language Features (carried from v0.1.1)
- Strict pidgin grammar — one instruction per line, no synonyms, no free-form parsing
- Period-chain reference system — `.valuename.scriptname.script.filename.vern` reading specific to general
- File I/O — `write` (overwrite) and `append` (additive)
- Scripts — named reusable blocks, called with `run`
- Script return values — `return .value pass to .destination`
- Inline conditionals — `if / then` with `and`, `or`, `not`
- Count-based loops — `repeat n times` with implicit read-only `loop` counter
- Container system — `#tag` named data pools for context switching and localization
- Extensible vocabulary — `define` keyword maps user words to script calls
- Reference resolution priority — script scope → file scope → imported files → fatal error

### New in v0.2

**Five primitive types** — Text, Number, True/False, Date (`YYYY-MM-DD`), Time (`HH:MM:SS`)

**Collections** — file-level homogeneous lists. `put`, `remove`, `get`, `count`, `repeat through`, `is in`, `not in`. Cross-file list support via `list listname .filename.vern`.

**Import Mechanism** — `import .filename.vern`. Circular import detection at load time. Resolution priority fully documented.

**Extended Math** — `round`, `floor`, `ceiling` (all with optional decimal places), `power`, `root`, `remainder`, `random`, `absolute`, `minimum`, `maximum`, `percent`. All non-destructive.

**Conditional Block Form** — `if condition` / `end if` for multiple instructions per condition. Inline `if / then` unchanged and not deprecated.

**Error Recovery** — `attempt` / `if fail` / `end fail` / `end attempt`. Two modes: stop at first failure (default) and `attempt all`. `fail reason` implicit read-only keyword. Nested attempts supported.

**Date and Time** — `get date`, `get time`, `difference between`, `format` with `MO`/`MI` codes. Container system handles locale-specific formatting.

**String Operations** — `length of`, `find`, `extract` (using `beginning`/`finishing`), `replace`. All non-destructive. Position arguments accept value references for dynamic calculation.

### Key Design Decisions Made in v0.2 (Non-Negotiable)
- Lists are file-level only — no script-local lists
- Lists are homogeneous — one type per list, enforced
- `beginning` and `finishing` used in `extract` — `start` and `end` are block keywords only
- `current item` is two words — for translatability
- `MO` for month, `MI` for minute in format codes — no shared codes between date and time
- `not in` and `is in` are two-word compound tokens
- `attempt all` runs all instructions then reports all failures; fail handler runs once per failure
- Nested attempts: inner handled failures are invisible to outer attempt
- All extended math operations are non-destructive

---

## Permanent Design Constraints

These are non-negotiable and must never be violated in any future version:

- **Strict pidgin only** — no synonyms, no optional words, no free-form parsing. Every instruction has one form.
- **No string interpolation** — use `convert` and `+` concatenation.
- **No implicit type coercion** — all type conversion is explicit via `convert`.
- **Two reserved symbols only** — `.` for containment hierarchy, `#` for container tags. No other special characters.
- **The period chain is exclusive** — `.` belongs only to the file/script/value hierarchy.
- **One instruction per line** — always.
- **Non-destructive operations where possible** — originals never modified, results go to new named values.

---

## v0.2 Limitations

- No nested scripts — all scripts must be defined at file level
- No while loop — open-ended repetition requires count-based `repeat` or recursion
- No text-to-date/time conversion — parsing user-entered dates deferred to v0.3
- No short-circuit boolean evaluation
- No otherwise/else — two separate `if` blocks required for true/false branching

---

## v0.3 Priorities

These are the next features in order of importance:

### 1. While Loop (CRITICAL)
The absence of a while-style loop caused workarounds in multiple v0.2 examples. Open-ended repetition — repeat until a condition is met rather than a fixed count — is essential for real programs. Needs full design work. Proposed pattern:

```
while condition
    instructions
end while
```

Must not allow infinite loops to go undetected — needs documentation of recursive loop warning equivalent.

### 2. Otherwise / Else (HIGH)
Currently two separate `if` blocks handle true/false branching. An `otherwise` block eliminates the redundancy and is more readable:

```
if condition
    instructions
otherwise
    instructions
end if
```

### 3. Text-to-Date/Time Conversion (HIGH)
Users collecting dates via `ask` have no way to convert the text to a date type in v0.2. Parsing user-entered date strings needs a defined syntax and defined valid input formats.

### 4. File Operations Beyond Read/Write (MEDIUM)
- Check if a file exists before reading
- Delete a file
- List files in a directory

### 5. Nested Scripts (MEDIUM)
Currently a fatal error. Allowing scripts to be defined inside other scripts adds flexibility but significant parsing complexity. Low priority relative to the items above.

### 6. Short-Circuit Boolean Evaluation (LOW)
Currently all conditions in a compound expression are always evaluated fully. Short-circuit evaluation (stop as soon as the result is known) is a performance improvement. Low user impact.

### 7. Standard Library (LOW)
Pre-built container files and `define` libraries — common operations, locale-specific date/time helpers, math utilities — shipping with VERN as optional imports.

### 8. Package System (LOW)
Community-contributed bindings and libraries. Needs design work on distribution, versioning, and trust.

### 9. Logarithms and Trigonometry (LOW)
Specialized math operations. Deferred until the language has a user base that can confirm the need.

---

## Building an Interpreter

The spec is implementation-ready. Recommended build order for a Python reference implementation:

1. Tokenizer — read a `.vern` file, apply English vocabulary binding, produce invariant tokens
2. Parser — validate token sequences against the invariant grammar
3. Executor — run the parsed instruction tree
4. Error logger — implement the fatal/non-fatal error scale with log output
5. File I/O — implement `read`, `write`, `append`
6. Collections — implement list operations
7. Import — implement file loading and circular import detection
8. Container resolution — implement the `#tag` priority hierarchy
9. Error recovery — implement `attempt` / `attempt all`
10. Extended math and string operations
11. Date and time
12. Localization layer — vocabulary binding as a replaceable table

Start with English binding only. Localization support layers on after the core executes correctly.

---

## Repository & Identity

- GitHub: `https://github.com/designercrack-777/VERN`
- Attribution: The VERN Project (no personal name attached)
- License: All Rights Reserved — no permissions granted, full protection
- License can be changed later to CC BY when community participation is desired — changing from restrictive to permissive is clean, the reverse is not

---

*The VERN Project — 2026*
