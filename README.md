# VERN

**A universal imperative programming grammar with replaceable vocabulary bindings.**

VERN is a controlled natural language programming language designed to make programming accessible to anyone who can read and write in their own language. It uses a strict, command-style pidgin grammar that eliminates the translation layer between human intent and executable code.

VERN is not a programming language in English. It is a universal imperative grammar — a formal structure for expressing computational intent that can be bound to the vocabulary of any human language without altering execution semantics. Code written in Swahili, Japanese, Arabic, or English executes identically. The grammar is the same. Only the words change.

---

## The Core Claim

Existing programming languages require users to learn English keywords as a prerequisite to computation. Internationalization efforts translate user interfaces and documentation — but the code itself remains English. VERN makes the executable vocabulary the localization target. A programmer writes code in their own language. The machine runs it.

This is distinct from:
- **i18n** — translating UI strings while code stays English
- **l10n** — adapting regional formats while code stays English
- **DSLs** — specialized English vocabulary for specific domains
- **Transliteration** — phonetic script mapping, not semantic equivalence

VERN's claim: a general-purpose imperative grammar in which the executable keywords are fully replaceable, such that programs written in any vocabulary binding execute identically.

---

## Repository Contents

| Document | Description |
|---|---|
| `VERN_Invariant_Grammar_v0_6.md` | The core prior art document. Abstract grammar specification plus four vocabulary bindings: English, Swahili, Japanese, and Arabic. |
| `VERN_spec_v0_6.md` | The full language specification. Syntax, grammar rules, reference system, data handling, collections, dictionaries, nested data structures, imports, extended math, trigonometry, logarithms, mathematical constants, angle conversion, conditionals, repetition, loop control, scripts, script parameters, error recovery, date and time, string operations, file operations, core operations, type checking, number formatting, multi-line text, and networking. |
| `VERN_Next_Steps_v0_6.md` | Current project status and orientation document. |
| `VERN_Next_Steps_Post_v0_6.md` | Forward paths for the post-interpreter phase — documentation, distribution, licensing, standard library, and ecosystem. |
| `VERN_interpreter/` | Complete Python interpreter implementing every feature in the v0.6 spec. |

---

## Language Overview

VERN programs are plain text files with the `.vern` extension. One instruction per line. No symbolic syntax beyond the period (`.`) for containment hierarchy and the hash (`#`) for container tags.

```
// Calculator — English binding

script .calculation
    ask .number1input
    convert .number1input to number as .number1
    ask .operator
    ask .number2input
    convert .number2input to number as .number2
    if .operator = "+" then set .number3 to .number1 + .number2
    if .operator = "-" then set .number3 to .number1 - .number2
    if .operator = "*" then set .number3 to .number1 * .number2
    if .operator = "/" then set .number3 to .number1 / .number2
    show .number1, .operator, .number2, "=", .number3
end script

start at .calculation.script
stop
```

The same program in Swahili:

```
// Kikokotoo — Swahili binding

hati .hesabu
    uliza .ingizo1
    badilisha .ingizo1 kwa nambari kama .namba1
    uliza .opereta
    uliza .ingizo2
    badilisha .ingizo2 kwa nambari kama .namba2
    ikiwa .opereta = "+" basi weka .namba3 kwa .namba1 + .namba2
    ikiwa .opereta = "-" basi weka .namba3 kwa .namba1 - .namba2
    ikiwa .opereta = "*" basi weka .namba3 kwa .namba1 * .namba2
    ikiwa .opereta = "/" basi weka .namba3 kwa .namba1 / .namba2
    onyesha .namba1, .opereta, .namba2, "=", .namba3
mwisho hati

anza katika .hesabu.hati
simama
```

Both programs execute identically. The grammar is invariant. The vocabulary is not.

---

## Key Features

**Nested data structures** — dictionaries of dictionaries and lists of dictionaries. Built from flat file-level declarations linked by reference. Access is two steps: retrieve the inner structure, then operate on it.

**Type checking** — `type of .value as .result` returns the data type of any value as a text string. Works on value references and implicit loop keywords.

**Number formatting** — `format .number as .result decimals 2 thousands` prepares numbers for display with controlled decimal places, thousands separators, and padding.

**Multi-line text** — `text .valuename` / `end text` blocks declare file-level values holding structured text across multiple lines. Content is treated as raw text — reserved words are not parsed inside blocks.

**Networking** — `fetch .url as .result` sends HTTP GET requests. `send .data to .url` sends HTTP POST requests. Both return raw text and are fully recoverable inside `attempt` blocks.

**Dictionaries** — key-value data structures with full iteration, membership checks, and cross-file access. Keys are always text. Values are homogeneous by type. `current key` and `current value` follow the same pattern as `current item` in list iteration.

**Loop control** — `exit loop` exits the current loop immediately. `next item` skips to the next iteration.

**Script parameters** — scripts may declare named input parameters using `takes`. Values are passed positionally using `with` on the `run` call.

**Extended string operations** — `split`, `join`, `trim`, `uppercase`, `lowercase`, `starts with`, `ends with`. All non-destructive.

**Extended list operations** — `sort`, `reverse`, `slice`, `combine`. All non-destructive. Results always assigned to a new named list.

**Extended math** — trigonometric operations, logarithms, mathematical constants (`pi`, `e`, `tau`, `infinity`), angle conversion, and additional numeric operations. All non-destructive.

**Strict pidgin grammar** — limited vocabulary, rigid structure, one instruction per line. No synonyms, no optional words, no free-form parsing.

**Period-chain referencing** — values, scripts, files, and folders referenced by containment chain reading specific to general.

**Container system** — named data pools tagged with `#` allow context-switching without separate scripts. Built for localization.

**Explicit type conversion** — no implicit coercion. `convert .value to number as .newvalue` is the only way to change types.

**File operations** — read, write, append, delete, and check existence of files. List directory contents.

**Extensible vocabulary** — users define new words mapped to script calls: `define "greet" as run .greet.script`.

**Universal localizability** — every keyword is a replaceable slot in the invariant grammar. To create a new language binding, map each token to the target language's imperative equivalent. Programs in any binding execute identically.

---

## Status

**Current version: v0.6 — Specification complete. Interpreter complete. Packaged and installed.**

VERN is a working programming language. The v0.6 interpreter implements every feature in the specification. A standalone Windows executable (`vern.exe`) is built and installed. Six example programs run correctly. All 267 automated tests pass.

The next phase covers documentation, distribution, licensing, standard library, and ecosystem development. See `VERN_Next_Steps_Post_v0_6.md` for the full forward paths document.

---

## Prior Art Notice

This repository constitutes a public prior art disclosure for the VERN language architecture, specifically the invariant grammar with replaceable vocabulary bindings as described in `VERN_Invariant_Grammar_v0_6.md`.

All rights reserved. No license is granted for use, modification, or distribution without explicit permission from The VERN Project.

---

*The VERN Project — 2026*
