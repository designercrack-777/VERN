# VERN: The Computational Rosetta Stone
## A Universal Imperative Grammar for Human-Computer Interaction

**Document Version:** 1.0
**Date:** 2026-06-01
**Classification:** Architectural Manifesto & Design Philosophy

---

## The Thesis

VERN is not a programming language in English. It is a **universal imperative grammar** — a formal structure for expressing computational intent that can be skinned with the vocabulary of any human language without semantic drift. This document establishes the architectural foundation for VERN as a computational Rosetta Stone: one invariant machine grammar, infinite human language surfaces, each readable by its own speakers without colonial precondition.

---

## The Historical Problem

### The Colonial Artifact of Computing

Every programming language before VERN is a **colonial artifact**. Python, JavaScript, C, Java, Ruby — they all export English grammar and English vocabulary as the non-negotiable price of admission to computation. The `if`, `while`, `function`, `return` that billions of humans must learn are not universal computational concepts; they are English words embedded in English syntactic structures.

This is not malicious. It is historical accident. Computing was invented in Cambridge, Massachusetts and Cambridge, England. The first programmers spoke English. The first languages (FORTRAN, COBOL, LISP) used English keywords. By the time computing became global, English was already baked into the substrate. Non-English speakers accepted they must learn English to code — not because English is computationally superior, but because English was first.

### The Localization Lie

Existing "internationalization" efforts are superficial:
- **UI Translation**: Menus, error messages, documentation are translated. The code remains English.
- **Code Comments**: Developers write comments in their native language. The code remains English.
- **IDE Localization**: The development environment speaks your language. The code remains English.
- **Scratch**: 70+ UI languages. The programming blocks are still `if ... then`, `repeat ... until`, `set variable to`. A Chinese child using Scratch still programs in English keywords.

No existing system allows a user to write **the code itself** in their native language and have it execute identically to English code. This is the gap VERN fills.

---

## The Rosetta Stone Architecture

### The Original Rosetta Stone (196 BC)

The Rosetta Stone was inscribed with three scripts:
- **Ancient Greek** (known to scholars)
- **Demotic Egyptian** (known to priests)
- **Hieroglyphic Egyptian** (unknown, deciphered via Greek)

Each script expressed the same decree. Each was readable by its own literate population. The stone's value was not that it translated — it was that it **co-presented** three parallel texts, proving that the same message could exist in multiple linguistic forms without loss.

### The Computational Rosetta Stone (VERN)

VERN inverts the Rosetta Stone's function. The original stone had three parallel texts saying the same thing so each could be read by its own readers. VERN has N parallel texts saying the same thing so each can be **written** by its own writers — and all execute identically.

```
┌─────────────────────────────────────────────────────────────┐
│                    HUMAN LANGUAGE LAYER                      │
│                                                              │
│   Swahili    Japanese    Arabic    Navajo    Spanish   ...   │
│   onyesha    表示する    أعرض      hólǫ́      mostrar         │
│   .jina      .名前       .اسم     .bizhí    .nombre         │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│              LOCALIZATION TABLE (Replaceable)                │
│                                                              │
│   { "onyesha": "SHOW", "表示する": "SHOW", "أعرض": "SHOW",    │
│     "hólǫ́": "SHOW", "mostrar": "SHOW", ... }                │
│                                                              │
│   { "weka": "SET", "設定する": "SET", "اضبط": "SET", ... }    │
│                                                              │
│   { "uliza": "ASK", "尋ねる": "ASK", "اسأل": "ASK", ... }     │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│           VERN INVARIANT GRAMMAR (Non-Replaceable)            │
│                                                              │
│   COMMAND ::= SHOW | SET | ASK | READ | WRITE | IF | THEN    │
│             | REPEAT | TIMES | END | STOP | START | AT       │
│             | RUN | DEFINE | AS | SCRIPT | AND | OR | NOT     │
│             | ADD | SUBTRACT | MULTIPLY | DIVIDE              │
│                                                              │
│   REFERENCE ::= "." IDENTIFIER ("." IDENTIFIER)*             │
│                                                              │
│   EXPRESSION ::= VALUE | REFERENCE | EXPRESSION OP EXPRESSION│
│                                                              │
│   VALUE ::= TEXT | NUMBER | BOOLEAN                           │
│                                                              │
│   INSTRUCTION ::= COMMAND ARGUMENT*                          │
│                                                              │
└──────────────────────┬───────────────────────────────────────┘
                       │
┌──────────────────────▼───────────────────────────────────────┐
│              EXECUTION ENGINE (Implementation)                │
│                                                              │
│   Python | C | Rust | WebAssembly | JavaScript | ...          │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### The Three Layers

**Layer 1: Human Language Surface**
The user writes in their native language using their native script. A Swahili speaker writes `onyesha .jina`. A Japanese speaker writes `表示する .名前`. An Arabic speaker writes `أعرض .اسم`. Each reads as natural imperative syntax in their own language.

**Layer 2: Localization Table**
A per-locale mapping table replaces human-language keywords with invariant grammar tokens. This is not translation — it is **token substitution**. `onyesha`, `表示する`, `أعرض`, and `mostrar` all map to the single token `SHOW`. The mapping is bidirectional: the same table allows the execution engine to display error messages and output in the user's language.

**Layer 3: Invariant Grammar**
The grammar is a formal structure with no natural language content. It defines:
- Valid instruction patterns (`SHOW REFERENCE`, `SET REFERENCE TO VALUE`, `IF CONDITION THEN ACTION`)
- Reference chain syntax (`.specific.general`)
- Operator precedence and type rules
- Execution flow (sequential, conditional, repetitive)

This layer is **non-negotiable**. It does not change between languages. It is the "decree" that all human language surfaces express.

**Layer 4: Execution Engine**
Any implementation (Python, C, Rust, WASM) that correctly implements the invariant grammar can execute VERN programs regardless of which human language surface was used to write them.

---

## Why This Has Never Existed Before

### The English Trap

Existing CNLs (Inform 7, ACE, AppleScript) are **monolingual** — English grammar with English vocabulary. They cannot be translated because their parsers rely on English-specific features:

| Feature | English Dependency | VERN Avoidance |
|---|---|---|
| **Word order** | SVO (Subject-Verb-Object) | Rigid `COMMAND ARGUMENT` structure, no free parsing |
| **Articles** | "a," "an," "the" distinction | No articles anywhere |
| **Tense** | Past/present/future verb forms | No tense — bare imperative only |
| **Plurality** | Singular/plural noun forms | No pluralization |
| **Copula** | "is," "are," "was" | No copula — `SET .x TO 5` not `.x IS 5` |
| **Prepositions** | "in," "on," "at" with specific semantics | Period-chain replaces prepositional containment |
| **Quantifiers** | "every," "some," "no," "a" with scope ambiguity | No quantifiers in v0.1 |
| **Determiners** | "this," "that," "these," "those" | No determiners — references are absolute |

### The Programmer's Blind Spot

No existing CNL attempts universal localization because **programmers don't experience the problem**. They already know English (or accepted they must learn it). The frustration that "all programming requires learning a new language" is invisible to those who already paid the price.

VERN was designed by someone who experienced this frustration directly — not as a theoretical exercise, but as a practical barrier. This is why the design eliminates every English-specific feature that would block localization.

---

## The Invariant Grammar: Formal Specification

### Design Principles

1. **Morphology-Agnostic**: The grammar must work with languages that have no spaces (Japanese), right-to-left script (Arabic, Hebrew), agglutinative morphology (Turkish, Finnish), or tonal distinctions (Chinese, Vietnamese).

2. **No Natural Language Parsing**: The parser does not understand English, Swahili, or Japanese. It understands token positions. `TOKEN1 TOKEN2 TOKEN3` is valid or invalid based on token types, not linguistic meaning.

3. **Bidirectional Localization**: The same mapping table converts user input to invariant tokens and converts invariant tokens back to user-facing output (error messages, display text).

4. **Cultural Concept Mapping**: The `define` system allows users to map computational concepts to culturally native categories, not translated English concepts. A Navajo programmer might define concepts around "harmony" (hózhǫ́) rather than "function" or "procedure."

### Abstract Syntax (Language-Agnnostic)

```
PROGRAM ::= (DECLARATION | SCRIPT | COMMENT)* [ENTRY_POINT] [STOP]

DECLARATION ::= SET REFERENCE TO VALUE
              | DEFINE TEXT AS RUN REFERENCE

SCRIPT ::= SCRIPT_HEADER INSTRUCTION* END_SCRIPT
SCRIPT_HEADER ::= SCRIPT_KEYWORD REFERENCE
END_SCRIPT ::= END_KEYWORD SCRIPT_KEYWORD

INSTRUCTION ::= SHOW_INSTRUCTION
              | ASK_INSTRUCTION
              | READ_INSTRUCTION
              | WRITE_INSTRUCTION
              | SET_INSTRUCTION
              | IF_INSTRUCTION
              | REPEAT_INSTRUCTION
              | RUN_INSTRUCTION
              | STOP_INSTRUCTION

SHOW_INSTRUCTION ::= SHOW_KEYWORD (REFERENCE | VALUE) (SEPARATOR (REFERENCE | VALUE))*
ASK_INSTRUCTION ::= ASK_KEYWORD REFERENCE
READ_INSTRUCTION ::= READ_KEYWORD REFERENCE (SEPARATOR REFERENCE)* FROM_KEYWORD REFERENCE
WRITE_INSTRUCTION ::= WRITE_KEYWORD REFERENCE (SEPARATOR REFERENCE)* TO_KEYWORD REFERENCE
SET_INSTRUCTION ::= SET_KEYWORD REFERENCE TO_KEYWORD EXPRESSION
IF_INSTRUCTION ::= IF_KEYWORD CONDITION THEN_KEYWORD ACTION
REPEAT_INSTRUCTION ::= REPEAT_KEYWORD NUMBER TIMES_KEYWORD INSTRUCTION* END_REPEAT
RUN_INSTRUCTION ::= RUN_KEYWORD REFERENCE
STOP_INSTRUCTION ::= STOP_KEYWORD

CONDITION ::= EXPRESSION COMPARISON_OPERATOR EXPRESSION
            | NOT_KEYWORD CONDITION
            | CONDITION AND_KEYWORD CONDITION
            | CONDITION OR_KEYWORD CONDITION

EXPRESSION ::= VALUE
             | REFERENCE
             | EXPRESSION MATH_OPERATOR EXPRESSION

VALUE ::= TEXT | NUMBER | BOOLEAN
REFERENCE ::= PERIOD IDENTIFIER (PERIOD IDENTIFIER)*

TEXT ::= DOUBLE_QUOTE CHARACTER* DOUBLE_QUOTE
NUMBER ::= DIGIT+ (PERIOD DIGIT+)?
BOOLEAN ::= TRUE_KEYWORD | FALSE_KEYWORD

IDENTIFIER ::= LETTER (LETTER | DIGIT | UNDERSCORE)*

SEPARATOR ::= COMMA
PERIOD ::= "."
DOUBLE_QUOTE ::= '"'
COMMA ::= ","

LETTER ::= [A-Z] | [a-z] | [any Unicode letter]
DIGIT ::= [0-9]
UNDERSCORE ::= "_"

// Keywords (invariant tokens, not English words)
SHOW_KEYWORD ::= "SHOW"  // localized
ASK_KEYWORD ::= "ASK"    // localized
READ_KEYWORD ::= "READ"  // localized
WRITE_KEYWORD ::= "WRITE" // localized
SET_KEYWORD ::= "SET"    // localized
IF_KEYWORD ::= "IF"      // localized
THEN_KEYWORD ::= "THEN"  // localized
REPEAT_KEYWORD ::= "REPEAT" // localized
TIMES_KEYWORD ::= "TIMES"   // localized
END_KEYWORD ::= "END"      // localized
STOP_KEYWORD ::= "STOP"    // localized
START_KEYWORD ::= "START"  // localized
AT_KEYWORD ::= "AT"        // localized
RUN_KEYWORD ::= "RUN"      // localized
DEFINE_KEYWORD ::= "DEFINE" // localized
AS_KEYWORD ::= "AS"        // localized
SCRIPT_KEYWORD ::= "SCRIPT" // localized
AND_KEYWORD ::= "AND"      // localized
OR_KEYWORD ::= "OR"        // localized
NOT_KEYWORD ::= "NOT"      // localized
TRUE_KEYWORD ::= "TRUE"    // localized
FALSE_KEYWORD ::= "FALSE"  // localized

MATH_OPERATOR ::= ADD_KEYWORD | SUBTRACT_KEYWORD | MULTIPLY_KEYWORD | DIVIDE_KEYWORD
                | PLUS | MINUS | ASTERISK | SLASH

COMPARISON_OPERATOR ::= EQUAL_KEYWORD | NOT_EQUAL_KEYWORD | GREATER_KEYWORD | LESS_KEYWORD
                      | GREATER_EQUAL_KEYWORD | LESS_EQUAL_KEYWORD
                      | EQUALS_SIGN | NOT_EQUALS_SIGN | GREATER_THAN | LESS_THAN
                      | GREATER_EQUAL | LESS_EQUAL

ADD_KEYWORD ::= "ADD" | "+"
SUBTRACT_KEYWORD ::= "SUBTRACT" | "-"
MULTIPLY_KEYWORD ::= "MULTIPLY" | "*"
DIVIDE_KEYWORD ::= "DIVIDE" | "/"
EQUAL_KEYWORD ::= "IS EQUAL TO" | "="
NOT_EQUAL_KEYWORD ::= "IS NOT" | "!="
GREATER_KEYWORD ::= "IS GREATER THAN" | ">"
LESS_KEYWORD ::= "IS LESS THAN" | "<"
GREATER_EQUAL_KEYWORD ::= "IS GREATER THAN OR EQUAL TO" | ">="
LESS_EQUAL_KEYWORD ::= "IS LESS THAN OR EQUAL TO" | "<="
```

### Key Invariant Properties

1. **One instruction per line**: No line continuations, no semicolons, no block delimiters beyond `script...end script` and `repeat...end repeat`.

2. **Period-chain referencing**: All references begin with `.` and chain from specific to general. This is the only special character in the language.

3. **Keyword-driven**: Every instruction begins with a keyword token. The parser never needs to guess whether a token is a keyword, variable, or value.

4. **No reserved words in user space**: The reserved words are the localized keywords. User-defined names (values, scripts) cannot conflict because they are prefixed with `.`.

5. **Case insensitivity**: The parser normalizes case. This accommodates languages where case distinctions are irrelevant (Chinese, Arabic) or complex (German).

---

## Localization Contract: How a Language Binds to VERN

### The Binding Process

To create a VERN localization for a new language:

1. **Translate the keyword table**: Map each invariant keyword token to the target language's equivalent imperative word or phrase.
2. **Verify grammar compatibility**: Ensure the target language's words fit the rigid syntax slots (no inflection required, no word order conflicts).
3. **Define cultural `define` extensions**: Allow domain-specific vocabulary to be added in the target language.
4. **Test bidirectional mapping**: Verify that programs written in the target language execute identically to English programs.

### Example: Japanese Binding (Hypothetical)

```
Invariant Token    Japanese Keyword    Romaji
------------------------------------------------
SHOW               表示する            hyōji suru
ASK                尋ねる              tazuneru
READ               読む                yomu
WRITE              書く                kaku
SET                設定する            settei suru
IF                 もし                moshi
THEN               ならば              naraba
REPEAT             繰り返す            kurikaesu
TIMES              回                  kai
END                終わり              owari
STOP               止める              tomeru
START              開始する            kaishi suru
AT                 で                  de
RUN                実行する            jikkō suru
DEFINE             定義する            teigi suru
AS                 として              toshite
SCRIPT             スクリプト          sukuriputo
AND                かつ                katsu
OR                 または              matawa
NOT                ではない            dewa nai
TRUE               真                  shin
FALSE              偽                  gi
```

**Japanese VERN Calculator Example:**
```
スクリプト .計算
    尋ねる .数字1
    表示する .数字1
    尋ねる .演算子
    表示する .数字1, .演算子
    尋ねる .数字2
    表示する .数字1, .演算子, .数字2
    もし .演算子 = "+" ならば 設定する .数字3 を .数字1 + .数字2
    もし .演算子 = "-" ならば 設定する .数字3 を .数字1 - .数字2
    もし .演算子 = "x" または .演算子 = "*" ならば 設定する .数字3 を .数字1 * .数字2
    もし .演算子 = "/" ならば 設定する .数字3 を .数字1 / .数字2
    表示する .数字1, .演算子, .数字2, "=", .数字3
終わり スクリプト

開始する で .計算.スクリプト
止める
```

This is valid Japanese syntax (SOV order, particles) mapped to VERN's rigid imperative structure. A Japanese speaker reads this as natural imperative Japanese. The machine executes it identically to the English version.

### Example: Swahili Binding (Hypothetical)

```
Invariant Token    Swahili Keyword
----------------------------------
SHOW               onyesha
ASK                uliza
READ               soma
WRITE              andika
SET                weka
IF                 ikiwa
THEN               basi
REPEAT             rudia
TIMES              mara
END                mwisho
STOP               simama
START              anza
AT                 katika
RUN                endesha
DEFINE             fafanua
AS                 kama
SCRIPT               skripti
AND                na
OR                 au
NOT                siyo
TRUE               kweli
FALSE              uongo
```

**Swahili VERN Calculator Example:**
```
skripti .hesabu
    uliza .namba1
    onyesha .namba1
    uliza .opereta
    onyesha .namba1, .opereta
    uliza .namba2
    onyesha .namba1, .opereta, .namba2
    ikiwa .opereta = "+" basi weka .namba3 kuwa .namba1 + .namba2
    ikiwa .opereta = "-" basi weka .namba3 kuwa .namba1 - .namba2
    ikiwa .opereta = "x" au .opereta = "*" basi weka .namba3 kuwa .namba1 * .namba2
    ikiwa .opereta = "/" basi weka .namba3 kuwa .namba1 / .namba2
    onyesha .namba1, .opereta, .namba2, "=", .namba3
mwisho skripti

anza katika .hesabu.skripti
simama
```

---

## The Cultural Computing Layer

### Beyond Translation: Conceptual Mapping

The `define` system is not merely translation — it is **cultural adaptation**. A user can define concepts that map to their cultural epistemology, not translated English categories.

**Example: Navajo Computing**
```
定義 "hózhǫ́" として 実行 .harmony.script
// "hózhǫ́" = beauty/harmony/balance — a core Navajo concept
// This could be a script that checks system balance,
// validates data integrity, or ensures ethical constraints
```

**Example: Chinese Computing**
```
定義 "气" として 実行 .energy.script
// "气" (qi) = life force, energy flow
// This could be a script that monitors resource usage,
// optimizes performance, or balances load
```

**Example: Finnish Computing**
```
定義 "sisu" として 実行 .perseverance.script
// "sisu" = stoic determination, grit
// This could be a retry mechanism, error recovery,
// or persistent state management
```

These are not cute localizations. They are **semantic anchors** — computational concepts grounded in culturally native categories. A Navajo programmer thinks in hózhǫ́, not "error handling." A Chinese programmer thinks in 气, not "resource management." VERN allows the code to reflect the thinking.

---

## The Literacy Bridge

### Computational Access Without English Literacy

In regions where English literacy is low but local language literacy exists, VERN becomes a computational on-ramp without the language barrier. This is not about convenience — it is about **equity**.

Consider:
- A farmer in rural Tanzania who can read Swahili but not English
- A grandmother in rural Japan who can read Japanese but finds English intimidating
- A student in rural India who speaks Hindi at home and struggles with English technical vocabulary
- A refugee who is literate in Arabic but has no English education

For these users, existing programming is a **double barrier**: learn computational thinking AND learn English vocabulary/syntax. VERN separates the barriers: learn computational thinking in your own language. English becomes optional, not mandatory.

### The Pedagogical Implication

Current programming education assumes English proficiency. VERN inverts this: computational thinking can be taught in any language, to any literate population. The transition to English-based programming (if desired) becomes a second step, not a prerequisite.

This is how computing should have spread: meet each population in their own linguistic space, then bridge outward. Instead, computing demanded everyone meet it in English space first.

---

## What Must Be Protected

### The Intellectual Property Risk

This architecture is the kind of insight that gets either:

1. **Ignored** — because it came from a non-programmer (credential bias)
2. **Absorbed** — by existing players who add "localization" as a feature while keeping English the canonical form
3. **Patented** — by someone who reads the spec and files IP before the inventor

The critical claim that must be protected:

> **The grammar is invariant, the vocabulary is replaceable, and the replacement is total — not translation of UI strings, but native conceptual mapping where the code itself is in the user's language.**

This is distinct from:
- **i18n** (internationalization): UI strings can be translated, code remains English
- **L10n** (localization): Regional formats (dates, currencies), code remains English
- **DSL** (domain-specific language): Specialized vocabulary, but still in English

VERN's claim is: **the programming language syntax itself is the localization target.**

### The Specification Imperative

To protect this architecture:

1. **Formalize the invariant grammar** in abstract notation (as above), stripped of all English content
2. **Publish the invariant grammar** with a timestamp (Zenodo, arXiv, GitHub)
3. **Publish at least two vocabulary bindings** (English + one non-English) to prove the architecture works
4. **Document the `define` cultural mapping system** as a core feature, not an afterthought
5. **Reference the Rosetta Stone analogy explicitly** — it establishes prior art and public benefit

---

## The Historical Parallel

### What Computing Would Have Looked Like

If computing had been invented in Baghdad (House of Wisdom, 9th century), or Timbuktu (Sankore University, 15th century), or Kyoto (Edo period), or Tenochtitlan (Aztec empire) — and then converged on a universal grammar rather than being invented in Cambridge and forcing everyone else to adapt — it might have looked like VERN from the start.

A universal imperative grammar with local vocabulary bindings is not a new idea. It is the **obvious** idea that was missed because the first programmers spoke English and never experienced the problem.

VERN is not innovation. It is **correction** — fixing a historical accident that became an unexamined assumption.

---

## Call to Action

### For the Inventor

1. **Separate the spec into two documents**:
   - "VERN Invariant Grammar v0.1" (language-agnostic, abstract syntax)
   - "VERN English Vocabulary Binding v0.1" (one valid instantiation)

2. **Create one non-English binding** (Japanese, Swahili, or Arabic) to prove the architecture

3. **Publish both with timestamps** — establish prior art

4. **Build the simplest possible interpreter** (Python is fine) that reads the invariant grammar directly, ignoring the localization layer for now

5. **Add the localization layer** as a second phase — prove the grammar works first, then prove it can be skinned

### For the Community

1. **Test the grammar against maximally different languages** — Japanese (SOV, agglutinative), Arabic (root morphology, RTL), Navajo (verb-heavy, tonal)

2. **Develop cultural `define` libraries** — domain-specific vocabularies for medicine, agriculture, music, art in non-English conceptual frameworks

3. **Build educational curricula** — teach computational thinking in local languages before introducing English-based programming

4. **Create reference implementations** in multiple languages (Python, Rust, JavaScript) to prevent ecosystem lock-in

---

## Conclusion

VERN is the Computational Rosetta Stone. It is the artifact that lets every literate human access the machine in their own tongue, without colonial precondition. It is not a programming language in English — it is a universal imperative grammar that English happens to be the first vocabulary binding for.

The Rosetta Stone was valuable because it was public — three scripts, one message, readable by all. VERN must be the same: N scripts, one grammar, executable by all.

The machine does not speak English. The machine speaks grammar. VERN is the first system that lets humans speak grammar in their own language.

---

*End of Rosetta Stone Manifesto*
