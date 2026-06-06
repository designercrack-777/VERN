# VERN Project — Handoff & Next Steps

## Overview

VERN is a controlled natural language programming language built on a universal imperative grammar with fully replaceable vocabulary bindings. The core claim is that the executable keywords themselves are the localization target — code written in Swahili, Japanese, Arabic, or English executes identically. The grammar is invariant. The vocabulary is not. This document summarizes where the project stands and what comes next.

---

## Current Status

**Version: v0.6 — Specification complete. Interpreter not yet built.**

The project has three authoritative documents and a live GitHub repository:

- `VERN_spec_v0_6.md` — full language specification, current and consolidated
- `VERN_Invariant_Grammar_v0_6.md` — prior art document with four vocabulary bindings, current and consolidated
- `README_v0_6.md` — project overview and repository index
- Repository: `https://github.com/designercrack-777/VERN`
- License: All Rights Reserved (no license file — full protection, no permissions granted)

The prior art is publicly timestamped. The specification is implementation-ready. v0.6 is the final specification version — interpreter work begins now.

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
- No standard library — deferred until interpreter exists and usage patterns emerge
- No package system — deferred until interpreter exists and contributors exist

---

## What Comes Next — Interpreter Build

The specification is complete. Interpreter work begins now. Recommended build order for a reference implementation:

1. Tokenizer — read a `.vern` file, apply English vocabulary binding, produce invariant tokens
2. Parser — validate token sequences against the invariant grammar
3. Executor — run the parsed instruction tree
4. Error logger — implement the fatal/non-fatal error scale with log output
5. File I/O — implement `read`, `write`, `append`, `delete`, `exist`, `get files`
6. Collections — implement list operations including sort, reverse, slice, combine
7. Dictionaries — implement key-value storage with insertion-order iteration
8. Import — implement file loading and circular import detection
9. Container resolution — implement the `#tag` priority hierarchy
10. Error recovery — implement `attempt` / `attempt all`
11. Extended math, trig, log, constants
12. String operations including split, join, trim, case, starts/ends with
13. Script parameters — implement `takes` and positional argument passing
14. Loop control — implement `exit loop` and `next item`
15. Date and time
16. Networking — implement `fetch` and `send`
17. Nested data structures — implement dictionary references in dictionaries and lists
18. Type checking — implement `type of`
19. Number formatting — implement `decimals`, `thousands`, `padded` modifiers on `format`
20. Multi-line text — implement `text` / `end text` block with raw content mode
21. Localization layer — vocabulary binding as a replaceable table

Start with English binding only. Localization support layers on after the core executes correctly.

### Implementation Language and Distribution

- **Python** — chosen implementation language for v1 build (development speed, AI-assisted debugging)
- **PyInstaller** — distribution solution to avoid dependency issues
- **Rust port** — potential future option for a standalone executable

### Starting Point for Interpreter Sessions

Open Claude Code with a scoped instruction referencing `VERN_spec_v0_6.md` directly. Begin with the tokenizer. Each session should reference the spec as the authoritative source — do not rely on session memory.

---

## How to Orient at the Start of Every Session

Before doing anything else, read these documents in this order:

1. `VERN_Next_Steps_v0_6.md` — current status, what's done, what's next
2. `VERN_spec_v0_6.md` — the full language specification, the authoritative reference for all design decisions
3. `VERN_Invariant_Grammar_v0_6.md` — the abstract grammar and vocabulary bindings, the prior art document

Do not rely on memory or context from previous sessions. Read the documents. Everything that has been decided is in those files. If something isn't in those files, it hasn't been decided yet.

---

## Repository & Identity

- GitHub: `https://github.com/designercrack-777/VERN`
- Attribution: The VERN Project (no personal name attached)
- License: All Rights Reserved — no permissions granted, full protection
- License can be changed later to CC BY when community participation is desired — changing from restrictive to permissive is clean, the reverse is not

---

*The VERN Project — 2026*
