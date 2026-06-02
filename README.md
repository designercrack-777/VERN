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
| `VERN_Invariant_Grammar_v0.1.1.md` | The core prior art document. Abstract grammar specification plus four vocabulary bindings: English, Swahili, Japanese, and Arabic. |
| `VERN_spec_v0.1.1.md` | The full language specification. Syntax, grammar rules, reference system, data handling, core operations, and examples. |

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

**Strict pidgin grammar** — limited vocabulary, rigid structure, one instruction per line. No synonyms, no optional words, no free-form parsing. What you see is what runs.

**Period-chain referencing** — values, scripts, and files are referenced by containment chain reading specific to general: `.valuename.scriptname.script.filename.vern`. The minimum necessary chain is always used.

**Container system** — named data pools tagged with `#` allow context-switching without separate scripts. The same value resolves differently depending on which container is active. Built for localization.

**Explicit type conversion** — no implicit coercion. `convert .value to number as .newvalue` is the only way to change types. The original is never modified.

**Extensible vocabulary** — users define new words mapped to script calls: `define "greet" as run .greet.script`. Domain experts build their own vocabulary on top of the grammar.

**Universal localizability** — every keyword is a replaceable slot in the invariant grammar. To create a new language binding, map each token to the target language's imperative equivalent. Programs in any binding execute identically.

---

## Status

**Current version: v0.1.1 — Specification complete, interpreter not yet implemented.**

The specification is implementation-ready. An interpreter has not yet been built. Contributions toward a reference implementation are noted as a future priority.

---

## Prior Art Notice

This repository constitutes a public prior art disclosure for the VERN language architecture, specifically the invariant grammar with replaceable vocabulary bindings as described in `VERN_Invariant_Grammar_v0.1.1.md`.

All rights reserved. No license is granted for use, modification, or distribution without explicit permission from The VERN Project.

---

*The VERN Project — 2026*
