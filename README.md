# VERN

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20646051.svg)](https://doi.org/10.5281/zenodo.20646051)

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
| --- | --- |
| `VERN_Invariant_Grammar_v0_7_7.md` | The core prior art document. Abstract grammar specification plus four vocabulary bindings: English, Swahili, Japanese, and Arabic. |
| `VERN_spec_v0_7_7.md` | The full language specification. Syntax, grammar rules, reference system, data handling, collections, dictionaries, nested data structures, imports, extended math, trigonometry, logarithms, mathematical constants, angle conversion, conditionals, repetition, loop control, scripts, script parameters, return values, multiple return values, first-class functions, error recovery, typed exception handling, date and time, string operations, file operations, non-VERN file extensions, dynamic file references, core operations, type checking, number formatting, multi-line text, networking, parse and inspect, none type, execution modes, inter-program stop, concurrent program launching, and timed pauses. |

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

**Execution modes** — four program lifecycle behaviors beyond run-once: `wait reset`, `wait keep`, `cycle reset`, `cycle keep`. Programs can loop immediately, pause for input between cycles, and carry or reset state across cycles. Stop conditions at the bottom of the file provide clean, auditable exit logic.

**Concurrent program launching** — `launch .programname.vern` starts another VERN program as a concurrent process within the same runtime. The launching script continues immediately. Launched programs are addressable by name and can be halted with `stop .programname.vern`.

**Inter-program stop signal** — `stop .programname.vern` inside a script halts another named running program immediately, regardless of its execution mode. Both programs share a runtime registry so they can find each other.

**Timed pauses** — `wait 2 seconds` or `wait 500 milliseconds` pauses execution for a fixed duration before continuing. Useful for pacing concurrent programs, polling loops, and any behavior that depends on timing.

**Nested data structures** — dictionaries of dictionaries and lists of dictionaries, up to four levels deep. Built from flat file-level declarations linked by reference. Consistent with the language's flat, explicit design philosophy.

**None type** — `none` is a first-class value representing the explicit absence of data. Assignable, returnable, and checkable. Distinct from zero, false, or empty string.

**First-class functions** — `invoke script .scriptname` passes a script reference as a value and executes it from a receiving script. Enables reusable, parameterized behavior patterns without hardcoding script names.

**Multiple return values** — scripts may return more than one value using comma-separated `return` syntax. Callers assign results inline using `as`.

**Dynamic file references** — `path .valuename` constructs a file reference from a runtime value rather than a hardcoded literal. Allows file names to be determined while the program runs.

**Typed exception handling** — `attempt` blocks may specify failure types using `fail type`. `if fail type` branches handle specific error categories distinctly from the general `if fail` catch.

**Expanded networking** — `fetch` and `send` support custom headers, status code retrieval, and HTTP PUT and DELETE in addition to GET and POST.

**Parse and inspect** — `parse .value as json` (or csv, xml, ini) converts structured text into a navigable VERN data structure. `inspect .value` reports structural information about a value at runtime.

**Type checking** — `type of .value as .result` returns the data type of any value as a text string. Works on value references and implicit loop keywords.

**Number formatting** — `format .number as .result decimals 2 thousands` prepares numbers for display with controlled decimal places, thousands separators, and padding.

**Multi-line text** — `text .valuename` / `end text` blocks declare file-level values holding structured text across multiple lines. Content is treated as raw text — reserved words are not parsed inside blocks.

**Dictionaries** — key-value data structures with full iteration, membership checks, and cross-file access. Keys are always text. `current key` and `current value` follow the same pattern as `current item` in list iteration.

**Loop control** — `exit loop` exits the current loop immediately. `next item` skips to the next iteration. Both are resolved as two-word compounds, consistent with existing compound token patterns.

**Script parameters** — scripts may declare named input parameters using `takes`. Values are passed positionally using `with` on the `run` call. Parameters are local to the script and not typed at declaration.

**Extended string operations** — `split`, `join`, `trim`, `uppercase`, `lowercase`, `starts with`, `ends with`. All non-destructive.

**Extended list operations** — `sort`, `reverse`, `slice`, `combine`. All non-destructive. Results always assigned to a new named list.

**Extended math** — trigonometric operations (`sine`, `cosine`, `tangent` and inverses, hyperbolic forms), logarithms (natural, base 10, arbitrary base), mathematical constants (`pi`, `e`, `tau`, `infinity`), angle conversion, and additional numeric operations (`sum`, `factorial`, `combinations`, `permutations`, `sign`). All non-destructive, all strictly numeric.

**Negative number literals** — negative numbers are written directly: `-15`, `-0.5`. No workaround needed.

**Expression grouping** — parentheses group math expressions exactly as in written mathematics: `(3 + 4) * 2`. Left-to-right evaluation is the default without parentheses.

**Strict pidgin grammar** — limited vocabulary, rigid structure, one instruction per line. No synonyms, no optional words, no free-form parsing. What you see is what runs.

**Period-chain referencing** — values, scripts, files, and folders are referenced by containment chain reading specific to general: `.valuename.scriptname.script.filename.vern`. Directory navigation uses `.folder` and `.parent` descriptors. The minimum necessary chain is always used.

**Container system** — named data pools tagged with `#` allow context-switching without separate scripts. The same value resolves differently depending on which container is active. Built for localization.

**Explicit type conversion** — no implicit coercion. `convert .value to number as .newvalue` is the only way to change types. The original is never modified.

**While loops and branching** — `while` loops run as long as a condition holds. `otherwise` provides a clean true/false branch inside `if` blocks. Both are fully nestable.

**File operations** — read, write, append, delete, and check existence of files. List directory contents. All file references use the standard period chain extended with `.folder` and `.parent` descriptors.

**Extensible vocabulary** — users define new words mapped to script calls: `define "greet" as run .greet.script`. Domain experts build their own vocabulary on top of the grammar.

**Universal localizability** — every keyword is a replaceable slot in the invariant grammar. To create a new language binding, map each token to the target language's imperative equivalent. Programs in any binding execute identically.

---

## Status

**Current version: v0.7.7 — Specification complete. Interpreter complete. Windows installer available.**

The interpreter implements every v0.7.7 feature and is distributed as a standalone Windows executable with a proper installer. No Python or dependencies required.

---

## Prior Art Notice

This repository constitutes a public prior art disclosure for the VERN language architecture, specifically the invariant grammar with replaceable vocabulary bindings as described in `VERN_Invariant_Grammar_v0_7_7.md`.

Permanent public record: https://doi.org/10.5281/zenodo.20646051

All rights reserved. No license is granted for use, modification, or distribution without explicit permission from The VERN Project.

---

*The VERN Project — 2026*
