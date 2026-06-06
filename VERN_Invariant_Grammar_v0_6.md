# VERN Project — Handoff & Next Steps

## Overview

VERN is a controlled natural language programming language built on a universal imperative grammar with fully replaceable vocabulary bindings. The core claim is that the executable keywords themselves are the localization target — code written in Swahili, Japanese, Arabic, or English executes identically. The grammar is invariant. The vocabulary is not. This document summarizes where the project stands and what comes next.

---

## Current Status

**Version: v0.6 — Specification complete. Interpreter complete. Packaged and installed.**

VERN is no longer a design document. It is a working programming language with a standalone executable.

The project has the following authoritative documents and a live GitHub repository:

- `VERN_spec_v0_6.md` — full language specification, authoritative reference for all design decisions
- `VERN_Invariant_Grammar_v0_6.md` — prior art document with four vocabulary bindings (English, Swahili, Japanese, Arabic)
- `README_v0_6.md` — project overview and repository index
- `VERN_Next_Steps_Post_v0_6.md` — forward paths document covering documentation, distribution, licensing, standard library, and ecosystem
- Repository: `https://github.com/designercrack-777/VERN`
- License: All Rights Reserved (no license file — full protection, no permissions granted)

The prior art is publicly timestamped. The specification is complete. The interpreter is complete. The next phase of the project is distribution, documentation, and ecosystem.

---

## What the Interpreter Contains

The Python interpreter implements every feature in the v0.6 spec. All 21 build steps are complete and verified.

### Interpreter files

- `tokenizer.py` — reads `.vern` files, applies English vocabulary binding, produces invariant tokens. 109 tests, all passing.
- `parser.py` — validates token sequences against the invariant grammar, produces an instruction tree. 158 tests, all passing.
- `executor.py` — walks the instruction tree and runs programs. All features implemented and verified.
- `error_logger.py` — three error states: WARNING (non-fatal, continues), FATAL recovered (caught by attempt, continues), FATAL halting (execution stopped). Log written to `<program>.vern.log`.
- `ast_nodes.py` — instruction tree node definitions, imported by parser and executor.
- `vern_main.py` — entry point script.
- `vern.spec` — PyInstaller build specification.

### Distribution

- `vern.exe` — standalone Windows executable, 8.1 MB, no Python or dependencies required.
- Installed via PATH on Windows. Run from anywhere: `vern myprogram.vern`
- Mac and Linux builds require running PyInstaller on those platforms — the source is cross-platform.

### What the interpreter supports

Every feature in the v0.6 spec is implemented and tested: values, types, explicit type conversion, basic and extended math, trigonometry, logarithms, mathematical constants, angle conversion, string operations, list operations, dictionary operations, nested data structures, scripts, script parameters, return values, conditionals, while loops, repeat loops, loop control, file read/write/append/delete/exist/directory listing, date and time operations, error recovery, container and localization system, import, type checking, number formatting for display, multi-line text, networking (HTTP GET and POST), and user input and output.

### Example programs

Six example programs ship with the interpreter in the `examples/` folder: calculator, quiz, days until, name registry, safe input, and localization. All run correctly.

---

## What v0.6 Contains

### Carried from v0.5
All features from v0.5 are unchanged. v0.5 added: loop control (`exit loop`, `next item`), extended string operations (`split`, `join`, `trim`, `uppercase`, `lowercase`, `starts with`, `ends with`), extended list operations (`sort`, `reverse`, `slice`, `combine`), dictionaries, and script parameters (`takes`, `with`).

### New in v0.6

**Type Checking** — `type of .value as .result` returns the data type of any value as a text string. Valid returns: `"text"`, `"number"`, `"true/false"`, `"date"`, `"time"`. Works on `.value` references and implicit loop keywords (`current item`, `current key`, `current value`). `type` is a new reserved word.

**Number Formatting for Display** — `format` is extended to handle numbers in addition to dates and times. Three modifiers: `decimals n` (round and display to n decimal places), `thousands` (comma separator), `padded n` (left-pad to n characters). Modifiers combinable in any order. Parser distinguishes number formatting from date/time formatting by `using` vs modifier keywords. Three new reserved words: `decimals`, `thousands`, `padded`.

**Multi-Line Text** — `text .valuename` / `end text` block declares a file-level value holding text spanning multiple lines. Content is treated as raw text — reserved words inside are not parsed. Newlines between lines are preserved. Leading whitespace on each line is stripped. `text` gains a second valid position as a block opener when first token on a line. `end text` added as a valid `end` compound.

**Networking** — `fetch .url as .result` sends an HTTP GET request and assigns the response body as text. `send .data to .url` sends an HTTP POST request. Both accept text values only. Both are recoverable inside `attempt` blocks. Two new reserved words: `fetch`, `send`.

**Nested Data Structures** — dictionaries of dictionaries and lists of dictionaries. Built from flat file-level declarations linked by reference. Access is two steps: retrieve the inner dictionary into a named value, then operate on it. `put dictionary name in list` and `put dictionary name in dictionary` are the runtime insertion forms. Two levels of nesting only — deeper nesting deferred.

### Key Design Decisions Made in v0.6 (Non-Negotiable)

- `type of` works on scalar value references and implicit loop keywords only — not on list or dictionary names
- `type of` returns `"true/false"` as the string for boolean type — matches the language's own terminology
- Number format modifiers are processed in fixed order regardless of written order: `decimals` first, `thousands` second, `padded` last
- Number separator characters are fixed: `.` decimal, `,` thousands — locale-aware separators deferred to future container system
- Multi-line text blocks are file-level only — same as lists and dictionaries
- Leading whitespace in text blocks is stripped — if preservation required, use concatenation
- Newlines in multi-line text values are honored by `show` — each line displays on its own line
- Networking returns response body as raw text only — headers, status codes, authentication deferred to libraries
- `fetch` empty response returns empty string — not an error
- Nested structures are reference-based not copy-based — modifying through a reference modifies the original
- Nested structures are two levels maximum in v0.6
- `put dictionary name in list/dictionary` requires explicit `dictionary` keyword for unambiguous parsing

---

## Permanent Design Constraints

These are non-negotiable and must never be violated in any future version:

- **Strict pidgin only** — no synonyms, no optional words, no free-form parsing. Every instruction has one form.
- **No string interpolation** — use `convert` and `+` concatenation.
- **No implicit type coercion** — all type conversion is explicit via `convert`.
- **Two reserved symbols only** — `.` for containment hierarchy, `#` for container tags. No other special characters. The `:` separator in dictionary declarations is the only additional symbol — it is a structural delimiter, not a reserved operator.
- **The period chain is exclusive** — `.` belongs only to the file/script/value/folder hierarchy.
- **One instruction per line** — always.
- **Non-destructive operations where possible** — originals never modified, results go to new named values.
- **`beginning` and `finishing`** are the position markers for `extract` — `start` and `end` are block keywords only.
- **`current item` is two words** — not `currentitem` — for translatability. `current key` and `current value` follow the same pattern.
- **`MO` for month, `MI` for minute** in format codes — no `MM` in either context.
- **All contextual resolutions must be explicit and positional** — no vague "surrounding tokens" rules. Every ambiguous keyword must have a documented mechanical rule the parser can follow without interpretation.

---

## v0.6 Limitations

- Nested structures limited to two levels — deeper nesting deferred
- Number separator characters fixed — locale-aware separators deferred to container system
- Networking returns response body only — headers, status codes, authentication deferred to libraries
- No standard library — usage patterns are now emerging; standard library design can begin
- No package system — deferred until contributors exist
- English binding only — Swahili, Japanese, and Arabic bindings are specified but not implemented in the interpreter
- Windows only — Mac and Linux builds require running PyInstaller on those platforms

---

## What Comes Next

The interpreter is complete. The next phase covers eight possible forward paths, documented in full in `VERN_Next_Steps_Post_v0_6.md`. The recommended starting point is documentation — writing a getting started guide and plain-language reference for the audience the language was built for.

The eight paths are:

1. **Documentation** — getting started guide, plain-language reference, tutorials
2. **Go public** — make the GitHub repository publicly discoverable
3. **Proper distribution** — Windows installer, Mac and Linux builds, download page
4. **Standard library** — reusable `.vern` utility files that ship with the interpreter
5. **Licensing** — decide between All Rights Reserved, CC BY, MIT, or dual license
6. **Write real programs** — use VERN to build actual tools and feed that experience back into design
7. **Additional vocabulary bindings** — implement Swahili, Japanese, or Arabic in the interpreter
8. **Monetization** — tooling, hosting, education, consulting

---

## How to Orient at the Start of Every Session

Before doing anything else, read these documents in this order:

1. `VERN_Next_Steps_v0_6.md` — current status, what's done, what's next (this document)
2. `VERN_spec_v0_6.md` — the full language specification, the authoritative reference for all design decisions
3. `VERN_Invariant_Grammar_v0_6.md` — the abstract grammar and vocabulary bindings, the prior art document
4. `VERN_Next_Steps_Post_v0_6.md` — forward paths for the post-interpreter phase

Do not rely on memory or context from previous sessions. Read the documents. Everything that has been decided is in those files. If something isn't in those files, it hasn't been decided yet.

---

## Repository & Identity

- GitHub: `https://github.com/designercrack-777/VERN`
- Attribution: The VERN Project (no personal name attached)
- License: All Rights Reserved — subject to revision
- License can be changed later to CC BY when community participation is desired — changing from restrictive to permissive is clean, the reverse is not

---

*The VERN Project — 2026*
