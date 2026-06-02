# VERN Language Specification v0.1.1

## Overview

VERN is a controlled natural language programming language designed to make programming accessible to anyone who can read and write plain English. It uses a simplified, command-style pidgin English grammar with a strict but readable rule set, eliminating the translation layer between human intent and executable code. VERN is designed to be readable at a glance, writable without prior programming knowledge, and extensible through a user-defined vocabulary system. This document is the foundational specification for the language covering syntax, grammar rules, reference system, data handling, and core operations.

---

## File Format

- VERN programs are written in plain text files with the extension `.vern`
- One instruction per line
- The parser reads top to bottom, one line at a time
- Whitespace and indentation are cosmetic only and carry no syntactic meaning
- The parser is case insensitive — `Set`, `SET`, and `set` are treated as identical
- Case is preserved only in displayed or written text output

---

## Comments

Any line or portion of a line preceded by `//` is ignored by the parser entirely.

```
// this is a comment, the parser ignores this line
set .name to "Gabriel" // this part is also ignored
```

---

## Entry Point

By default VERN begins execution at the first line of the file and runs top to bottom. File-level values are initialized as they are encountered.

A user may define a custom entry point using:

```
start at .scriptname.script
```

When a custom entry point is defined:

1. All file-level values in the current file are initialized first, regardless of their physical position in the file
2. Execution then jumps to the specified script
3. Execution proceeds from that script forward

File-level values are always initialized before any script executes, even if `start at` appears before them in the file. This ensures scripts can reliably reference file-level values regardless of declaration order.

---

## Ending a Program

The keyword `stop` ends program execution. VERN auto-generates `stop` at the end of every `.vern` file to prevent unintended looping. A `stop` command may also be placed anywhere in the program to end execution early.

```
show "done"
stop
```

---

## The Reference System

A period before any word denotes that what follows belongs to or is contained within something. Chains read from most specific on the left to least specific on the right. The minimum necessary chain must always be provided to locate a reference unambiguously.

### Containment Hierarchy

```
file → script → value → data
file → container → value → data
```

- A **file** can contain scripts and containers
- A **script** can contain values and run instructions
- A **container** can contain values only — containers do not run
- A **value** contains only raw data — nothing named lives inside it

### Descriptor Rules

A period must be placed before every classifier in the chain. The period signals that something smaller belongs to what follows it. Every named element — value, script, file — receives a period prefix because each either contains something smaller or belongs to something larger.

A value requires no type descriptor because nothing named lives inside it. It is always the most specific thing in the chain. Every container above it requires a type descriptor following its name.

| Thing | Descriptor | Example |
|---|---|---|
| File (external) | `.vern` | `.utilities.vern` |
| File (current) | name only | `.utilities` |
| Script | `.script` | `.scriptname.script` |
| Container | `#` prefix | `#english` |
| Value | none | `.valuename` |

### Reference Chain Examples

```
.valuename
— a value in the current script

.valuename.scriptname.script
— a value within a script in the current file

.valuename.scriptname.script.filename.vern
— a value within a script in a different file

.valuename.filename
— a file-level value in the current file, explicitly qualified
  (used when a local script value shares the same name)

.valuename.filename.vern
— a file-level value in an external file

.scriptname.script
— the current script referencing itself

.scriptname.script.filename
— a script within the current file

.scriptname.script.filename.vern
— a script within a different file

.filename.vern
— a different file entirely

.valuename #containername
— a value from a named container in the current file

.valuename #containername.filename.vern
— a value from a named container in an external file
```

### File-Level Value Disambiguation

A file-level value is accessible from any script within that file. Under the minimum context rule, `.valuename` resolves to the local script scope first. If no local value of that name exists, it falls through to the file level automatically — no extra chain needed.

If a script declares a local value with the same name as a file-level value and you need to reference the file-level one explicitly, qualify it with the filename:

```
set .score to 100                // file-level .score

script .quiz
    set .score to 0              // local .score — shadows file-level

    show .score                  // resolves to local: 0
    show .score.filename         // resolves to file-level: 100
end script
```

The file-level value is not lost — it is simply shadowed by the local one within that script's scope. Extending the chain to include the filename bypasses the local scope and reaches the file-level value directly. The same applies to external files using `.filename.vern`.

### The Minimum Context Rule

Provide exactly as much chain as the system needs to locate the reference without ambiguity — no more. If a value is in the current script, `.valuename` is sufficient. Adding unnecessary chain is valid but redundant.

### Reference Resolution Priority

When a reference chain is ambiguous, the parser resolves in the following order:

1. Current script scope
2. Current file scope (outside any script)
3. Imported files, in the order they were imported
4. If ambiguity persists after (1)–(3), execution halts with a fatal error

The minimum context rule applies only within a single scope level. Cross-scope references require explicit chain disambiguation. Silent fallbacks are never used — ambiguity that cannot be resolved by the priority hierarchy is always fatal.

### Scoping Rules

A value's scope is determined by its container. The duplicate-name rule — first declaration wins — applies only within the same scope. The same name used in different scopes is not a duplicate; it is a distinct value that happens to share a name.

```
// Three values all named .score — no conflict
set .score to 0                  // file-level scope

script .quiz
    set .score to 0              // .score.quiz.script — distinct from file-level
end script

script .leaderboard
    set .score to 0              // .score.leaderboard.script — distinct from both above
end script
```

Inside any script, `.score` resolves to the local value first (current script scope). To reference the file-level `.score` from inside a script, extend the chain explicitly. The reference system makes every value unambiguous regardless of how many share the same name across different scopes.

---

## Containers

A container is a named context modifier at the file level. Containers hold modified states of values — they store data, they do not run. Scripts run and process information. Containers modify what that information is depending on context.

Containers are denoted by `#`. The `#` symbol is self-identifying and does not use the period chain — the period hierarchy is exclusive to file, script, and value references.

### Defining a Container

```
#containername
    set .valuename to data
```

Example:

```
#english
    set .greeting to "hello"
    set .farewell to "goodbye"

#spanish
    set .greeting to "hola"
    set .farewell to "adios"
```

### Tagging a Script

A script may be tagged with a container at definition. All value references inside that script resolve against the specified container first.

```
script .output #english
    show .greeting
    // resolves to "hello"
end script
```

### Tagging a Run Call

A `run` instruction may also carry a container tag. The tag applies to all value references inside the called script for that execution, overriding any tag set at the script's definition.

```
run .greet.script #english
run .greet.script #spanish
```

This allows a single script to behave differently depending on which container context it is called with, without needing to define separate scripts for each container.

### Tagging an Individual Reference

A single value reference may be tagged inline. The inline tag takes priority over any script-level tag.

```
script .output #english
    show .greeting
    // resolves to "hello" from #english (script-level tag)
    show .greeting #spanish
    // resolves to "hola" from #spanish (inline tag overrides script-level)
end script
```

### Baseline vs Modified Values

A value may exist with an untagged baseline, with container-modified states, or both.

**Untagged baseline only** — the value exists at its default state. No container modification.
```
set .greeting to "hey"
```

**Container states only** — the value exists only in its container-modified states. No baseline.
```
#english
    set .greeting to "hello"

#spanish
    set .greeting to "hola"
```
Referencing `.greeting` without a tag when no untagged baseline exists follows the error scale.

**Both baseline and container states** — the untagged baseline is the default. Container tags are modifications applied on top.
```
#formal
    set .greeting to "good evening"

set .greeting to "hey"
```
Referencing `.greeting` without a tag returns "hey". Referencing `.greeting #formal` returns "good evening".

### Container Resolution Priority

When a value is referenced, resolution follows this order:

1. Inline `#tag` on the specific reference
2. `run`-level `#tag` on the call that invoked the current script
3. Script-level `#tag` on the script definition
4. Untagged value in current script scope
5. Untagged value at file level
6. Imported files in order
7. Error scale applies if nothing resolves

If a `#tag` is present but the value has no state in that container, the parser falls back to the untagged baseline. If no untagged baseline exists, the error scale applies — non-fatal log if execution can continue, fatal if it cannot.

### External Container Files

A `.vern` file may contain nothing but containers, functioning as a pure data pool. Other files import and reference these containers via the reference system. This is the recommended pattern for localization — a dedicated file of language containers that any program file can draw from.

```
// languages.vern
#english
    set .greeting to "hello"
    set .farewell to "goodbye"

#spanish
    set .greeting to "hola"
    set .farewell to "adios"

#swahili
    set .greeting to "habari"
    set .farewell to "kwaheri"
```

```
// main.vern
script .output #english
    show .greeting.languages.vern
    // resolves "hello" from #english in languages.vern
end script
```

---

## Values

A value is a named container for data. Values are data type agnostic until assigned — the data itself determines what type the value is and what operations are valid on it.

### File-level values

Values may be declared at the top of a `.vern` file, outside of any script. These values are accessible to all scripts within that file. This is the recommended pattern for storing data that scripts will reference — keeping data separate from logic.

```
set .question1 to "What is the capital of France?"
set .correct1 to "Paris"

script .quiz
    show .question1
    ask .answer1
    if .answer1 = .correct1 then show "correct"
end script
```

### Assignment

```
set .valuename to data
```

Examples:

```
set .name to "Gabriel"
set .age to 34
set .active to true
```

### Data Types

| Type | Example | Valid Operations |
|---|---|---|
| Text | `"Gabriel"` | display, combine, compare |
| Number | `34` | math, compare |
| True/False | `true` / `false` | logic, compare |

The type is determined by what is assigned. The language enforces valid operations based on the type — you cannot perform math on text.

### Type Conversion

There is no implicit type coercion. To convert a value from one type to another, use the `convert` keyword. `convert` always creates a new named value — the original is never modified.

```
convert .valuename to number as .newvaluename
convert .valuename to text as .newvaluename
```

`convert` also accepts bare reserved keywords that hold implicit values. `loop` is the only such keyword in v0.1.1:

```
convert loop to text as .looptext
```

Examples:

```
// User input is always text. Convert it to a number for math.
ask .input
convert .input to number as .workingvalue
set .doubled to .workingvalue * 2

// A number needs to appear inside a sentence.
set .score to 9
convert .score to text as .scoretext
show "your score is " + .scoretext
```

If the value cannot be converted — for example, converting the text `"hello"` to a number — this is a fatal error. The error log records the value, its current type, and the attempted conversion.

---

## Operators

### Math Operators

Both word and symbol forms are valid and treated as identical by the parser.

| Word | Symbol | Operation |
|---|---|---|
| `add` | `+` | addition |
| `subtract` | `-` | subtraction |
| `multiply` | `*` | multiplication |
| `divide` | `/` | division |

### Operator Type Matrix

The `+` operator is polymorphic. Its behavior depends on the types of both operands:

| Left | Right | Result | Behavior |
|---|---|---|---|
| Number | Number | Number | Arithmetic addition |
| Text | Text | Text | String concatenation |
| Text | Number | Fatal | No implicit coercion |
| Number | Text | Fatal | No implicit coercion |
| Other | Any | Fatal | Unsupported operation |

All other math operators (`-`, `*`, `/`) are strictly numeric. Applying them to text or true/false values is a fatal error. There is no implicit type coercion anywhere in the language.

### Comparison Operators

| Word Form | Symbol | Meaning |
|---|---|---|
| `is equal to` | `=` | equal |
| `is not` | `!=` | not equal |
| `is greater than` | `>` | greater than |
| `is less than` | `<` | less than |
| `is greater than or equal to` | `>=` | greater or equal |
| `is less than or equal to` | `<=` | less or equal |

### Compound Operators

The following multi-word sequences are treated as single atomic tokens by the parser:

- `is equal to`
- `is not`
- `is greater than`
- `is less than`
- `is greater than or equal to`
- `is less than or equal to`

These compound operators are indivisible. The individual words within them (`is`, `not`, `equal`, `to`, `greater`, `less`, `than`, `or`) are not valid standalone tokens in expression contexts. `is not` is a single inequality operator — it is not equivalent to `is` followed by `not`.

### Boolean Logic

| Keyword | Meaning |
|---|---|
| `and` | both conditions must be true |
| `or` | at least one condition must be true |
| `not` | inverts a true/false state |
| `is not` | compares two values for inequality |

Note: `not` inverts an existing true/false value. `is not` compares two values directly. These are distinct operations.

### Boolean Evaluation

In v0.1, all conditions in a compound expression are evaluated fully before the boolean result is computed. There is no short-circuiting.

`if .a and .b then action` evaluates both `.a` and `.b` regardless of `.a`'s value. This means any side effects in conditions (such as `ask` or `run` calls) will always execute. Short-circuit evaluation may be introduced in a future version.

---

## Input and Output

### Input

| Command | Meaning |
|---|---|
| `ask .valuename` | prompt user for text input, store in valuename |
| `read .valuename from .filename.vern` | read a single value from a file |
| `read .value1, .value2 from .filename.vern` | read multiple values from a file in order, left to right |

`ask` always stores user input as text regardless of what the user types. A user entering `42` produces the text `"42"`, not the number `42`. Use `convert` to change the type before performing math or other numeric operations.

### Output

| Command | Meaning |
|---|---|
| `show .value` | display a single value to screen |
| `show .value1, .value2, .value3` | display multiple values in order, left to right |
| `write .value to .filename.vern` | overwrite file with value (creates file if it does not exist) |
| `write .value1, .value2 to .filename.vern` | overwrite file with multiple values in order, left to right |
| `append .value to .filename.vern` | add value to end of existing file (creates file if it does not exist) |
| `append .value1, .value2 to .filename.vern` | add multiple values to end of existing file in order, left to right |

`write` replaces all existing file content. `append` adds to it. If the target file does not exist, both `write` and `append` create it automatically.

---

## Conditionals

```
if condition then action
```

Conditions can be chained using `and` and `or`:

```
if condition and condition then action
if condition or condition then action
```

Examples:

```
if .name is equal to "Gabriel" then show "welcome back"
if .age is greater than 18 then show "access granted"
if not .active then show "account inactive"
if .operator = "x" or .operator = "*" then set .number3 to .number1 * .number2
if .age is greater than 18 and .active = true then show "access granted"
```

---

## Repetition

```
repeat n times
    instructions
end repeat
```

The keyword `loop` is available inside every `repeat` block. It holds the current iteration number, starting at 1 and incrementing by 1 each pass. `loop` is a reserved keyword — it is read-only, carries no period prefix, and is distinct from any user-defined value. Attempting to assign to `loop` is a fatal error. Referencing `loop` outside a `repeat` block is a fatal error.

### Loop Scope

Values created inside a `repeat` block belong to the enclosing script's scope. On the first iteration a new value is created. On subsequent iterations, assigning to the same name updates the existing value — this is not a duplicate declaration and does not trigger the duplicate-name error. Values created inside a `repeat` block persist after the loop ends, retaining the value from the final iteration.

```
repeat 5 times
    convert loop to text as .looptext
    show "item " + .looptext
end repeat
// .looptext persists after the loop, holding "5" — the final iteration value
```

The same scoping rules apply here as everywhere else — `.looptext` inside one script does not conflict with `.looptext` inside another script. Each belongs to its own container.

Example:

```
repeat 3 times
    show loop
end repeat
// displays 1, then 2, then 3
```

If you need to combine `loop` with text, convert it first:

```
repeat 5 times
    convert loop to text as .looptext
    show "item " + .looptext
end repeat
// displays: item 1, item 2, item 3, item 4, item 5
```

---

## Scripts

A script is a named, reusable block of instructions. Scripts are the single container type in VERN v0.1. Additional container types may be introduced in future versions.

### Defining a Script

```
script .scriptname
    instructions
end script
```

Example:

```
script .greet
    ask .username
    show "hello " + .username
end script
```

### Running a Script

A script may be run from anywhere in the file, including from within another script. This allows scripts to call and chain other scripts.

```
run .scriptname.script
run .cleanup.script.utilities.vern
```

### Script Return Values

A script may pass a value back to its caller using `return` with `pass to`. The destination must be a file-level value declared before the script runs. Attempting to pass to an undeclared value is a fatal error.

```
return .valuename pass to .destination
```

Example:

```
// file-level destination declared upfront
set .answer to 0
set .input to 0

script .double
    set .output to .input * 2
    return .output pass to .answer
end script

script .main
    set .input to 6
    run .double.script
    show .answer
    // displays 12
end script
```

Because the destination is a named file-level value, multiple scripts can pass to different destinations without any collision risk. Declare a separate destination for each script that returns a value.

```
// declare all destinations at file level
set .firstanswer to 0
set .secondanswer to 0
set .input to 0

script .double
    set .output to .input * 2
    return .output pass to .firstanswer
end script

script .triple
    set .output to .input * 3
    return .output pass to .secondanswer
end script

script .main
    set .input to 4
    run .double.script
    run .triple.script
    show .firstanswer
    // displays 8
    show .secondanswer
    // displays 12
end script
```

If a script does not include a `return` instruction, no value is passed. The destination value retains whatever it was initialized to at the file level.

### Calling a script from within a script

```
script .main
    run .collection.script
    run .retrieval.script
end script
```

### Recommended entry point convention

It is recommended to define a `.main` script as the single entry point that orchestrates all other scripts. This keeps execution order explicit and readable.

```
script .main
    run .setup.script
    run .process.script
    run .output.script
end script

start at .main.script
stop
```

---

## Extensible Vocabulary

New words may be defined and added to the language by the user. A defined word becomes a valid instruction in VERN.

```
define "greet" as run .greet.script
define "calculate" as run .math.script.utilities.vern
```

Defined words may be collected into library files and imported into any `.vern` file using the reference system.

---

## Error Handling

VERN has two error states:

- **Non-fatal** — execution continues, error is written to the error log
- **Fatal** — execution stops, error is written to the error log

An error log is generated any time an error occurs regardless of whether execution continues. The log records what went wrong, on which line, and whether execution was halted.

### Specific error behaviors

**Undefined value reference**
If a script references a value that has never been defined, execution cannot continue. This is a fatal error. The error log records which value was missing and on which line.

**Type conflict**
If an operation is performed on a value whose data type does not support it — for example, performing math on a text value — this is a fatal error. The error log records the operation attempted, the value involved, and its actual type.

**Invalid type conversion**
If a `convert` instruction cannot convert a value to the target type — for example, converting the text `"hello"` to a number — this is a fatal error. The error log records the value, its current type, and the attempted target type.

**Return to undeclared destination**
If a `return` instruction attempts to pass to a value that has not been declared, this is a fatal error. All return destinations must be declared as file-level values before any script runs.

**Writing to a file that does not exist**
If a `write` instruction targets a file that does not exist, VERN creates the file automatically in the same directory as the currently running `.vern` file. This is not an error. If the directory itself does not exist, this is a fatal error.

**Writing to a file that exists**
If a `write` instruction targets a file that already exists, the file is overwritten entirely. To add content without overwriting, use `append` instead of `write`.

**Appending to a file**
`append` adds values to the end of an existing file without affecting existing content. If the target file does not exist, `append` creates it, identical to `write` behavior on a new file.

**File format**
VERN files use a line-delimited format for value storage: one value per line, stored in the order specified in the `write` instruction. Text values are stored as-is with no quoting. Number and true/false values are stored in their literal form.

**Reading from a file**
Values are read in order, left to right, mapping to lines 1, 2, 3, and so on. If fewer lines exist in the file than values requested, this is a fatal error. If more lines exist than values requested, the excess lines are ignored.

**Container tag with no matching value**
If a `#tag` is present on a reference but the value has no state in that container, the parser falls back to the untagged baseline. If no untagged baseline exists, this follows the error scale — non-fatal log if execution can continue, fatal if it cannot.

**Duplicate name declarations**
If a value or script is declared more than once with the same name within the same scope, the first declaration is used and all subsequent duplicates are ignored. A non-fatal log entry is generated noting that a duplicate was found and ignored. This rule applies within a single scope only — the same name used in different scripts is not a duplicate, it is a distinct value. Reassigning a value inside a `repeat` block on subsequent iterations is not a duplicate declaration and does not trigger this rule.

**Recursive loops**
VERN does not prevent recursive script calls. A script that calls itself or two scripts that call each other will loop indefinitely until the program is manually terminated. Recursive loops are the user's responsibility. A future version may introduce a maximum execution depth limit.

**Partial display with undefined values**
If a `show` instruction references multiple values and some are defined while others are not, VERN displays the defined values and generates a non-fatal log entry for each undefined value. Execution continues.

**Empty input**
If a user presses enter without typing anything in response to an `ask` instruction, the value is assigned an empty string. An empty string is a valid text value. This is not an error.

---

## v0.1.1 Limitations

The following behaviors are intentionally deferred to future versions. Each is documented here to prevent implementation ambiguity.

### Script Nesting
Scripts cannot be nested inside other scripts. Attempting to define a script inside another script is a fatal error. All scripts must be defined at the file level.

### Empty vs. Uninitialized Values
An empty string (`""`) is a valid text value. Testing an empty string with `is equal to ""` returns true. An uninitialized value is distinct from an empty string — referencing a value that has never been assigned is always a fatal error.

---

## Reserved Words

The following words are reserved by the language and cannot be used as value names or script names:

`set`, `to`, `show`, `ask`, `read`, `write`, `append`, `from`, `if`, `then`, `repeat`, `times`, `end`, `stop`, `start`, `at`, `run`, `define`, `as`, `script`, `and`, `or`, `not`, `is`, `true`, `false`, `add`, `subtract`, `multiply`, `divide`, `convert`, `number`, `text`, `return`, `pass`, `loop`

Note: `is`, `not`, `equal`, `to`, `greater`, `less`, `than`, and `or` are reserved as standalone tokens but also appear as components of compound comparison operators (see Compound Operators). When adjacent in a recognized compound operator sequence, they are parsed as a single token, not as individual reserved words.

### Reserved Symbols

| Symbol | Use |
|---|---|
| `.` | Period — denotes containment in the file, script, value hierarchy. Exclusive to this hierarchy. |
| `#` | Hash — denotes a container tag. Used to define containers and to tag scripts or individual value references. Not part of the period chain. |

No other special characters are used by the language.

### Script Self-Reference
`.scriptname.script` used from within `.scriptname` resolves to the script's own identity, not its contents. In v0.1, self-reference has no practical use and is reserved for future introspection features.

---

## Example Programs

### Calculator

```
// Calculator program written in VERN

script .calculation
    ask .number1input
    convert .number1input to number as .number1
    show .number1
    ask .operator
    show .number1, .operator
    ask .number2input
    convert .number2input to number as .number2
    show .number1, .operator, .number2
    if .operator = "+" then set .number3 to .number1 + .number2
    if .operator = "-" then set .number3 to .number1 - .number2
    if .operator = "x" or .operator = "*" then set .number3 to .number1 * .number2
    if .operator = "/" then set .number3 to .number1 / .number2
    show .number1, .operator, .number2, "=", .number3
end script

start at .calculation.script
stop
```

### Quiz

```
// Quiz program written in VERN

set .question1 to "example question 1"
set .question2 to "example question 2"
set .question3 to "example question 3"
set .question4 to "example question 4"
set .question5 to "example question 5"
set .correct1 to "example answer 1"
set .correct2 to "example answer 2"
set .correct3 to "example answer 3"
set .correct4 to "example answer 4"
set .correct5 to "example answer 5"

script .quiz
    set .score to 0
    show .question1
    ask .answer1
    if .answer1 = .correct1 then set .score to .score + 1
    show .question2
    ask .answer2
    if .answer2 = .correct2 then set .score to .score + 1
    show .question3
    ask .answer3
    if .answer3 = .correct3 then set .score to .score + 1
    show .question4
    ask .answer4
    if .answer4 = .correct4 then set .score to .score + 1
    show .question5
    ask .answer5
    if .answer5 = .correct5 then set .score to .score + 1
    if .score >= 4 then show "great job", .score
    if .score < 4 then show "better luck next time", .score
end script

stop
```

### Contact Saver

```
// Contact collector and retrieval program written in VERN

script .main
    run .collection.script
    run .retrieval.script
end script

script .collection
    ask .name
    ask .phonenumber
    write .name, .phonenumber to .contacts.vern
    // write overwrites the file each run — use append to build a growing list
end script

script .retrieval
    read .name, .phonenumber from .contacts.vern
    show .name, .phonenumber
end script

start at .main.script
stop
```

### Localization with Containers

```
// Multilingual greeter using containers

#english
    set .greeting to "hello"
    set .farewell to "goodbye"
    set .prompt to "what is your name?"

#spanish
    set .greeting to "hola"
    set .farewell to "adios"
    set .prompt to "como te llamas?"

#swahili
    set .greeting to "habari"
    set .farewell to "kwaheri"
    set .prompt to "jina lako ni nani?"

script .greet
    show .greeting
    show .prompt
    ask .username
    show .greeting, .username
    show .farewell
end script

script .main
    ask .language
    if .language = "english" then run .greet.script #english
    if .language = "spanish" then run .greet.script #spanish
    if .language = "swahili" then run .greet.script #swahili
end script

start at .main.script
stop
```
