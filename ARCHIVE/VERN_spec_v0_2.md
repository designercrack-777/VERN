# VERN Language Specification v0.2

## Overview

VERN is a controlled natural language programming language designed to make programming accessible to anyone who can read and write in their own language. It uses a simplified, command-style pidgin grammar with a strict but readable rule set, eliminating the translation layer between human intent and executable code. VERN is designed to be readable at a glance, writable without prior programming knowledge, and extensible through a user-defined vocabulary system. The grammar is invariant — it does not change between languages. The vocabulary is replaceable — every keyword maps to an equivalent word or phrase in the target language. Code written in any vocabulary binding executes identically.

This document is the full specification for v0.2, covering syntax, grammar rules, reference system, data handling, collections, imports, extended math, conditionals, repetition, scripts, error recovery, date and time, string operations, and core operations.

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

## Importing Files

The `import` instruction loads an external `.vern` file and makes its contents — file-level values, lists, scripts, and containers — available to the importing file. Imported contents are resolved according to the reference resolution priority established in the reference system.

```
import .utilities.vern
```

One `import` per line. To import multiple files, use multiple lines:

```
import .utilities.vern
import .languages.vern
import .data.vern
```

`import` instructions are recommended at the top of the file, before any list declarations, file-level values, scripts, or containers. This keeps dependencies visible and explicit. `import` is not required to be first — a script that only needs a cross-file reference to a specific list or value can use the direct reference syntax without importing.

Loading a file via `import` makes all of its contents addressable by the importing file. Without `import`, cross-file references must use the full file chain — `.valuename.filename.vern`. After `import`, the minimum context rule applies: if the reference is unambiguous, the chain can be shortened.

### Import Order and Resolution Priority

When multiple files are imported, imported contents resolve after current script scope and current file scope, in the order the files were imported. If two imported files contain a value, list, or script with the same name, the first imported file wins on a short reference. To reach the second, extend the chain to include the filename explicitly.

Imported lists follow the same priority. To reach a list in the second imported file, append the filename after the list name.

### Circular Imports

Circular imports are fatal. If file A imports file B and file B imports file A, VERN detects the cycle at load time before execution begins and halts with a fatal error. A file may not import itself. Attempting to do so is a fatal error.

### Import Error Behaviors

**File not found** — if the specified file does not exist, this is a fatal error. The error log records the filename and the line number.

**Circular import** — detected at load time, fatal. The error log records the files involved.

**Self-import** — fatal.

---

## The Reference System

A period before any word denotes that what follows belongs to or is contained within something. Chains read from most specific on the left to least specific on the right. The minimum necessary chain must always be provided to locate a reference unambiguously.

### Containment Hierarchy

```
file → script → value → data
file → container → value → data
```

- A **file** can contain scripts, containers, and lists
- A **script** can contain values and run instructions
- A **container** can contain values only — containers do not run
- A **value** contains only raw data — nothing named lives inside it

### Descriptor Rules

A period must be placed before every classifier in the chain. The period signals that something smaller belongs to what follows it. Every named element — value, script, file — receives a period prefix because each either contains something smaller or belongs to something larger.

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

A file-level value is accessible from any script within that file. Under the minimum context rule, `.valuename` resolves to the local script scope first. If no local value of that name exists, it falls through to the file level automatically.

If a script declares a local value with the same name as a file-level value and you need to reference the file-level one explicitly, qualify it with the filename:

```
set .score to 100                // file-level .score

script .quiz
    set .score to 0              // local .score — shadows file-level

    show .score                  // resolves to local: 0
    show .score.filename         // resolves to file-level: 100
end script
```

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

---

## Containers

A container is a named context modifier at the file level. Containers hold modified states of values — they store data, they do not run. Scripts run and process information. Containers modify what that information is depending on context.

Containers are denoted by `#`. The `#` symbol is self-identifying and does not use the period chain — the period hierarchy is exclusive to file, script, and value references.

### Defining a Container

```
#containername
    set .valuename to data
```

### Tagging a Script

A script may be tagged with a container at definition. All value references inside that script resolve against the specified container first.

```
script .output #english
    show .greeting
end script
```

### Tagging a Run Call

A `run` instruction may carry a container tag. The tag applies to all value references inside the called script for that execution, overriding any tag set at the script's definition.

```
run .greet.script #english
run .greet.script #spanish
```

### Tagging an Individual Reference

A single value reference may be tagged inline. The inline tag takes priority over any script-level tag.

```
script .output #english
    show .greeting              // resolves from #english
    show .greeting #spanish     // resolves from #spanish — inline overrides script-level
end script
```

### Baseline vs Modified Values

A value may exist with an untagged baseline, with container-modified states, or both. Referencing a value without a tag when no untagged baseline exists follows the error scale.

### Container Resolution Priority

When a value is referenced, resolution follows this order:

1. Inline `#tag` on the specific reference
2. `run`-level `#tag` on the call that invoked the current script
3. Script-level `#tag` on the script definition
4. Untagged value in current script scope
5. Untagged value at file level
6. Imported files in order
7. Error scale applies if nothing resolves

If a `#tag` is present but the value has no state in that container, the parser falls back to the untagged baseline. If no untagged baseline exists, the error scale applies.

### External Container Files

A `.vern` file may contain nothing but containers, functioning as a pure data pool. Other files import and reference these containers via the reference system. This is the recommended pattern for localization.

---

## Collections

A list is a named, ordered sequence of values of a single type. Lists live at the file level only — they cannot be declared inside a script. Like file-level values, lists are accessible to all scripts within the file.

Lists are homogeneous. All items in a list must be the same type. The type of a list is determined by the first item added to it — either at declaration or via the first `put` instruction.

### Declaring a List

```
list listname
    "item one"
    "item two"
    "item three"
end list
```

Items are written one per line inside the block. The block is closed with `end list`. Indentation is cosmetic. A list may be declared empty — its type is determined on first insertion.

### Adding to a List

```
put .value in list names
```

Items are always appended to the end. `put` always adds to the last position. The word `in` is resolved by context — `put .value in list` is unambiguous.

### Removing from a List

```
remove .value from list names
```

Removes the first matching item. If not found, non-fatal log entry, execution continues. Removal shifts all subsequent items down by one position. The word `from` is resolved by context — `list` following `from` identifies a list operation, not a file read.

### Retrieving an Item by Position

```
get list names 3 as .currentname
```

Retrieves the item at the specified position and assigns it to a value. Positions begin at 1. If the position does not exist, fatal error. The word `as` is resolved by context — a number following a list name identifies a list retrieval, not a vocabulary definition.

### Iterating Through a List

```
repeat through list names
    show current item
end repeat
```

`current item` is an implicit read-only two-word keyword available only inside a `repeat through list` block. It holds the value of the current item for that iteration. It carries no period prefix and cannot be assigned to. The loop iterates from position 1 to last in order. An empty list produces zero iterations — no error.

If you need to work with `current item` beyond the loop or combine it with text, assign it to a value first:

```
repeat through list names
    set .working to current item
    show "name: " + .working
end repeat
```

### Membership Check

```
if .answer is in list validanswers then show "found"
if .answer not in list validanswers then show "not found"
```

`is in` and `not in` are compound tokens. The check is type-sensitive — a number `3` and a text `"3"` are not equal.

### Counting a List

```
count list names as .total
```

Returns the number of items as a number type. An empty list returns 0. `count` is a general-purpose keyword — `list` following it identifies this as a list count operation.

### Cross-File Lists

A list in another file is referenced by appending the file reference after the list name:

```
list names .filename.vern
```

Cross-file lists support all operations using the same syntax with the file reference appended:

```
put .item in list names .filename.vern
remove .item from list names .filename.vern
get list names .filename.vern 3 as .currentname
count list names .filename.vern as .total
if .value is in list names .filename.vern then show "found"

repeat through list names .filename.vern
    show current item
end repeat
```

Imported lists follow the same resolution priority as imported values. If two imported files contain lists with the same name, the first imported file wins on a short reference.

### Collection Error Behaviors

**Type mismatch on put** — fatal. Error log records the value, its type, and the list's type.

**Position out of range** — fatal. Error log records the position requested and the list length.

**Remove item not found** — non-fatal. Log entry generated, execution continues.

**current item outside loop** — fatal.

**Assigning to current item** — fatal. It is read-only.

---

## Values

A value is a named container for data. Values are data type agnostic until assigned — the data itself determines what type the value is and what operations are valid on it.

### File-level values

Values may be declared at the top of a `.vern` file, outside of any script. These values are accessible to all scripts within that file.

### Assignment

```
set .valuename to data
```

### Data Types

| Type | Example | Valid Operations |
|---|---|---|
| Text | `"Gabriel"` | display, combine, compare, string operations |
| Number | `34` | math, compare |
| True/False | `true` / `false` | logic, compare |
| Date | `2026-06-02` | compare, difference, format |
| Time | `14:30:00` | compare, difference, format |

The type is determined by what is assigned. The language enforces valid operations based on the type.

### Type Conversion

There is no implicit type coercion. To convert a value from one type to another, use the `convert` keyword. `convert` always creates a new named value — the original is never modified.

```
convert .valuename to number as .newvaluename
convert .valuename to text as .newvaluename
```

`convert` also accepts bare reserved keywords that hold implicit values. `loop` and `current item` are the implicit keywords in v0.2:

```
convert loop to text as .looptext
convert current item to text as .itemtext
```

Converting a date or time to text produces the raw internal storage string — `YYYY-MM-DD` for dates, `HH:MI:SS` for times. Use `format` for locale-appropriate display.

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

All other math operators (`-`, `*`, `/`) are strictly numeric. There is no implicit type coercion anywhere in the language.

### Comparison Operators

| Word Form | Symbol | Meaning |
|---|---|---|
| `is equal to` | `=` | equal |
| `is not` | `!=` | not equal |
| `is greater than` | `>` | greater than |
| `is less than` | `<` | less than |
| `is greater than or equal to` | `>=` | greater or equal |
| `is less than or equal to` | `<=` | less or equal |

Comparison operators work on date and time values — earlier dates and times are less than later ones.

### Compound Operators

The following multi-word sequences are treated as single atomic tokens by the parser:

- `is equal to`
- `is not`
- `is greater than`
- `is less than`
- `is greater than or equal to`
- `is less than or equal to`
- `is in`
- `not in`

These compound operators are indivisible. The individual words within them are not valid standalone tokens in expression contexts.

### Boolean Logic

| Keyword | Meaning |
|---|---|
| `and` | both conditions must be true |
| `or` | at least one condition must be true |
| `not` | inverts a true/false state |
| `is not` | compares two values for inequality |

`not` inverts an existing true/false value. `is not` compares two values directly. These are distinct operations.

### Boolean Evaluation

All conditions in a compound expression are evaluated fully before the boolean result is computed. There is no short-circuiting. Short-circuit evaluation may be introduced in a future version.

### Extended Math Operations

The four basic operators handle arithmetic inline within expressions. Extended math operations are non-destructive — they always produce a result assigned to a new named value via `as`. The original value is never modified. All extended math operations are strictly numeric.

#### Rounding

```
round .number as .result
round .number to 2 as .result
```

`round` without a decimal specification rounds to the nearest whole number. With `to n` rounds to `n` decimal places.

#### Floor and Ceiling

```
floor .number as .result
floor .number to 2 as .result

ceiling .number as .result
ceiling .number to 2 as .result
```

`floor` always rounds down. `ceiling` always rounds up. Without a decimal specification both produce whole numbers. With `to n` they round down or up to `n` decimal places.

#### Exponents and Roots

```
set .result to .number power 2
set .result to .number root 2
```

`power` raises a number to the specified exponent. `root` takes the nth root. Both follow the inline expression pattern.

#### Remainder

```
set .result to .number remainder .divisor
```

Returns the remainder after dividing the first number by the second. Follows the inline expression pattern.

#### Random

```
random .min to .max as .result
```

Generates a random whole number between `min` and `max` inclusive. Both bounds are included. Bounds accept literal numbers or value references that hold numbers.

#### Absolute Value

```
absolute .number as .result
```

Returns the non-negative value of a number.

#### Minimum and Maximum

```
minimum .value1 .value2 as .result
maximum .value1 .value2 as .result

minimum list numbers as .result
maximum list numbers as .result
```

Between two values, returns the smaller or larger. Across a list, returns the smallest or largest value. The list must be numeric.

#### Percentage

```
percent .value of .total as .result
```

Calculates what percentage `.value` is of `.total`. Both must be numeric. The result is a number.

### Extended Math Error Behaviors

**Non-numeric operand** — fatal. Error log records the operation, the value, and its type.

**Root of a negative number** — taking an even root of a negative number is fatal.

**Remainder by zero** — fatal.

**Random bounds invalid** — if minimum bound is greater than maximum bound, fatal.

**Minimum or maximum on empty list** — fatal.

**Minimum or maximum on non-numeric list** — fatal.

**Percentage with zero total** — fatal.

---

## Input and Output

### Input

| Command | Meaning |
|---|---|
| `ask .valuename` | prompt user for text input, store in valuename |
| `read .valuename from .filename.vern` | read a single value from a file |
| `read .value1, .value2 from .filename.vern` | read multiple values from a file in order |

`ask` always stores user input as text regardless of what the user types. Use `convert` to change the type before performing math or other numeric operations.

### Output

| Command | Meaning |
|---|---|
| `show .value` | display a single value to screen |
| `show .value1, .value2, .value3` | display multiple values in order |
| `write .value to .filename.vern` | overwrite file with value |
| `write .value1, .value2 to .filename.vern` | overwrite file with multiple values |
| `append .value to .filename.vern` | add value to end of existing file |
| `append .value1, .value2 to .filename.vern` | add multiple values to end of file |

`write` replaces all existing file content. `append` adds to it. Both create the file if it does not exist.

---

## Conditionals

### Inline Form

```
if condition then action
```

Handles a single action per condition. Use for single-instruction conditionals.

```
if .name is equal to "Gabriel" then show "welcome back"
if .age is greater than 18 then show "access granted"
if not .active then show "account inactive"
if .score >= 4 then show "great job"
```

Conditions can be chained using `and` and `or`:

```
if condition and condition then action
if condition or condition then action
```

### Block Form

```
if condition
    instructions
end if
```

Use for multiple instructions per condition. All instructions between `if condition` and `end if` execute only if the condition is true.

```
if .score is greater than 90
    show "excellent"
    set .grade to "A"
    run .award.script
end if
```

All condition syntax applies identically to both forms — `and`, `or`, `not`, compound comparison operators, membership checks.

### Nesting

`if` blocks may be nested inside other `if` blocks, inside `repeat` blocks, and inside `attempt` blocks.

```
if .score is greater than 50
    show "passing"
    if .score is greater than 90
        show "excellent"
    end if
end if
```

---

## Repetition

### Count-Based Loop

```
repeat n times
    instructions
end repeat
```

The keyword `loop` is available inside every `repeat` block. It holds the current iteration number, starting at 1. `loop` is read-only, carries no period prefix. Attempting to assign to `loop` is a fatal error. Referencing `loop` outside a `repeat` block is a fatal error.

Values created inside a `repeat` block belong to the enclosing script's scope. Values persist after the loop ends, retaining the value from the final iteration.

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
```

### List Iteration Loop

```
repeat through list names
    show current item
end repeat
```

`current item` is an implicit read-only two-word keyword. It holds the value of the current item for that iteration. It is only valid inside a `repeat through list` block. An empty list produces zero iterations — no error.

---

## Scripts

A script is a named, reusable block of instructions. Scripts must be defined at the file level — nesting scripts inside other scripts is a fatal error.

### Defining a Script

```
script .scriptname
    instructions
end script
```

### Running a Script

```
run .scriptname.script
run .cleanup.script.utilities.vern
```

A script may be run from anywhere in the file, including from within another script.

### Script Return Values

A script may pass a value back to its caller using `return` with `pass to`. The destination must be a file-level value declared before the script runs.

```
return .valuename pass to .destination
```

If a script does not include a `return` instruction, no value is passed. The destination value retains whatever it was initialized to at the file level.

### Calling a Script from Within a Script

```
script .main
    run .setup.script
    run .process.script
    run .output.script
end script
```

### Recommended Entry Point Convention

It is recommended to define a `.main` script as the single entry point that orchestrates all other scripts.

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

## Error Recovery

In v0.1.1, all fatal errors halt execution unconditionally. The `attempt` construct allows a program to handle failures gracefully and continue running. Wrapping instructions in an `attempt` block makes those instructions recoverable.

### Basic Syntax

```
attempt
    instructions
if fail
    instructions
end fail
end attempt
```

All four keywords are required. Execution always continues after `end attempt` regardless of whether the fail handler ran.

### Two Modes

#### Stop at First Failure

```
attempt
    convert .input to number as .value
    set .doubled to .value * 2
if fail
    show fail reason
end fail
end attempt
```

The default mode. At the first failure, execution immediately jumps to `if fail`. Instructions after the failure point are skipped. The fail handler runs once.

#### Try All

```
attempt all
    convert .input to number as .value
    set .doubled to .value * 2
if fail
    show fail reason
end fail
end attempt
```

`attempt all` runs every instruction regardless of failures. After all instructions have been attempted, the fail handler executes once for each failure in order. `fail reason` updates with each failure's description before the fail handler runs for that failure.

### fail reason

`fail reason` is an implicit read-only two-word keyword available only inside an `if fail` block. It holds a text description of the current failure. It carries no period prefix and cannot be assigned to.

`fail reason` describes two categories of failure:

**Direct failure** — the instruction itself could not execute:
```
"could not convert "hello" to number — value is text type"
```

**Dependent failure** — the instruction could not execute because a value it required failed to initialize earlier in the block:
```
"could not execute — depends on .value which failed to initialize"
```

Referencing `fail reason` outside an `if fail` block is a fatal error. Attempting to assign to `fail reason` is a fatal error.

### What Becomes Recoverable

Inside an `attempt` block, all previously fatal errors become recoverable:

- Type conflicts
- Invalid type conversions
- Undefined value references
- Position out of range (list and string operations)
- File not found on read
- Invalid math operations
- Return to undeclared destination

Errors that occur at load time — circular imports, self-imports, missing imported files — are not recoverable via `attempt` because they occur before execution begins.

### Nested Attempts

`attempt` blocks may be nested. If an inner attempt handles a failure through its own fail handler, the outer attempt does not see that failure — it was contained. Only unhandled failures propagate outward.

Nested attempts add complexity. Users new to programming should use single attempts.

### Execution Flow After attempt

Execution always continues after `end attempt`. If you need to branch based on whether an attempt succeeded, use a file-level value as a flag:

```
set .succeeded to false

attempt
    convert .input to number as .value
    set .succeeded to true
if fail
    show fail reason
end fail
end attempt

if .succeeded = true
    run .process.script
end if
```

### Error Recovery Error Behaviors

**fail reason outside if fail block** — fatal.

**Assigning to fail reason** — fatal. It is read-only.

**Empty attempt block** — not an error. The fail handler never runs.

**Fail handler with no failures** — not an error. The fail handler does not run.

---

## Date and Time

VERN introduces two new primitive types in v0.2: `date` and `time`. These join text, number, and true/false as the five primitive types of the language.

### Date Type

A date value holds a calendar date in the format `YYYY-MM-DD`. The parser recognizes this format and infers the date type automatically.

```
set .birthday to 1990-03-15
set .deadline to 2026-12-31
```

`YYYY-MM-DD` is the only valid literal date format.

### Time Type

A time value holds a time of day in the format `HH:MM:SS` using 24-hour notation. The parser recognizes this format and infers the time type automatically.

```
set .alarm to 07:30:00
set .meetingtime to 14:30:00
```

`HH:MM:SS` is the only valid literal time format.

### Getting the Current Date and Time

```
get date as .today
get time as .now
```

`get date` retrieves the current date from the system. `get time` retrieves the current time. Both assign to a named value via `as`.

### Difference Between Dates and Times

```
difference between .date1 and .date2 in days as .result
difference between .time1 and .time2 in hours as .result
difference between .time1 and .time2 in minutes as .result
```

Returns the absolute difference between two date or time values in the specified unit, assigned to a number type value. The result is always positive regardless of which value is earlier.

Available units for date differences: `days`
Available units for time differences: `hours`, `minutes`

The word `and` in this context is a separator between the two values, not a boolean operator. The parser resolves `and` by context — preceded by `difference between .reference` it is a separator, not a boolean conjunction.

### Formatting for Display

Date and time values have an internal representation that is not directly displayable as human-readable text. The `format` instruction converts a date or time value to a text value using a specified format pattern.

```
format .today as .displaydate using .dateformat
format .now as .displaytime using .timeformat
```

Date and time format codes are fully distinct — no code is shared between the two types.

**Date format codes:**
| Code | Meaning | Example |
|---|---|---|
| `YYYY` | Four-digit year | 2026 |
| `MO` | Two-digit month | 06 |
| `DD` | Two-digit day | 02 |

**Time format codes:**
| Code | Meaning | Example |
|---|---|---|
| `HH` | Two-digit hour (24-hour) | 14 |
| `MI` | Two-digit minute | 30 |
| `SS` | Two-digit second | 00 |

Format patterns are text values and can include any separator characters:

```
set .dateformat to "DD/MO/YYYY"
format .today as .displaydate using .dateformat
show .displaydate
// displays: 02/06/2026
```

### Localization of Date Formats

The container system handles locale-specific date and time formatting naturally:

```
#us
    set .dateformat to "MO/DD/YYYY"

#european
    set .dateformat to "DD/MO/YYYY"

#japanese
    set .dateformat to "YYYY/MO/DD"
```

### Date and Time Type Rules

- Math operators cannot be applied to date or time values — use `difference between` for date/time arithmetic
- Comparison operators work on date and time values — earlier dates/times are less than later ones
- `convert` can convert a date or time to text — produces the raw internal storage string (`YYYY-MM-DD` or `HH:MI:SS`). Use `format` for locale-appropriate display.
- Converting text to date or time is not supported in v0.2

### Date and Time Error Behaviors

**Invalid date literal** — fatal. Error log records the invalid literal and line number.

**Invalid time literal** — fatal. Error log records the invalid literal and line number.

**Math on date or time** — fatal. Use `difference between`.

**Difference between mismatched types** — fatal. Error log records the types involved.

**Invalid format code** — non-fatal. The code is passed through as literal text. Log entry generated.

**format applied to non-date/time value** — fatal.

---

## String Operations

Text values support display, concatenation, and comparison. The following operations extend text handling. All string operations are non-destructive — the original value is never modified. Results are always assigned to a new named value via `as`. All string operations are strictly for text type values. Character positions begin at 1.

### Length

```
length of .text as .result
```

Returns the number of characters as a number. Spaces and punctuation count. An empty string returns 0.

### Search

#### Existence Check

```
if "hello" is in .message then show "found"
if "hello" not in .message then show "not found"
```

`is in` and `not in` work for both list membership and text search. The parser resolves which context applies by whether a `list` keyword or a value reference follows. The check is case-sensitive.

#### Position Check

```
find "hello" in .message as .position
```

Returns the character position of the first occurrence as a number. Positions begin at 1. Returns 0 if not found. Searching within an empty string returns 0 — not an error.

### Extract

```
extract from .text beginning 1 finishing 5 as .result
```

Pulls a portion of text by character position. The beginning and finishing positions are both inclusive. Position arguments accept literal numbers or value references that hold numbers — this allows positions to be calculated dynamically.

If the beginning position is less than 1, greater than the length of the text, or greater than the finishing position, this is a fatal error. If the finishing position is greater than the length of the text, this is a fatal error.

### Replace

```
replace "old" with "new" in .text as .result
```

Searches for the first occurrence and replaces it. The original is unchanged. A log entry is always generated noting the search text, whether it was found, and the result. If the search text is not found, the original text is assigned to the result unchanged — not a fatal error.

### String Operation Error Behaviors

**Non-text operand** — fatal. Error log records the operation, the value, and its type.

**Extract position out of range** — fatal. Error log records the positions and the actual length.

**Replace search text not found** — non-fatal. Original assigned to result. Log entry generated.

---

## Error Handling

VERN has two error states:

- **Non-fatal** — execution continues, error is written to the error log
- **Fatal** — execution stops, error is written to the error log

An error log is generated any time an error occurs. The log records what went wrong, on which line, and whether execution was halted. Use the `attempt` construct to make fatal errors recoverable at runtime.

### Specific Error Behaviors

**Undefined value reference** — fatal. Error log records which value was missing and on which line.

**Type conflict** — fatal. Error log records the operation, the value, and its actual type.

**Invalid type conversion** — fatal. Error log records the value, its current type, and the attempted target type.

**Return to undeclared destination** — fatal. All return destinations must be declared as file-level values before any script runs.

**Writing to a file that does not exist** — VERN creates the file automatically. Not an error. If the directory does not exist, fatal.

**Writing to a file that exists** — the file is overwritten entirely. Use `append` to add without overwriting.

**Reading from a file** — values are read in order, left to right, mapping to lines 1, 2, 3. If fewer lines exist than values requested, fatal. Excess lines are ignored.

**Container tag with no matching value** — falls back to untagged baseline. If no baseline exists, follows error scale.

**Duplicate name declarations** — within the same scope, first declaration wins. Subsequent duplicates are ignored with a non-fatal log entry. Same name in different scopes is not a duplicate.

**Recursive loops** — VERN does not prevent recursive script calls. A script that calls itself will loop indefinitely. Recursive loops are the user's responsibility.

**Partial display with undefined values** — `show` displays defined values and generates a non-fatal log entry for each undefined value. Execution continues.

**Empty input** — if a user presses enter without typing anything, the value is assigned an empty string. Not an error.

---

## v0.2 Limitations

The following behaviors are intentionally deferred to future versions.

**Script Nesting** — scripts cannot be nested inside other scripts. Attempting to define a script inside another script is a fatal error.

**Empty vs. Uninitialized Values** — an empty string (`""`) is a valid text value. An uninitialized value is distinct from an empty string — referencing a value that has never been assigned is always a fatal error.

**Text to Date/Time Conversion** — converting user-entered text to date or time type is not supported. Parsing user-entered dates is a v0.3 consideration.

**While Loop** — VERN has no while-style loop in v0.2. Open-ended repetition requires a count-based `repeat` block. A while construct may be introduced in a future version.

**Short-Circuit Boolean Evaluation** — all conditions in a compound expression are always evaluated fully. Short-circuit evaluation may be introduced in a future version.

---

## Reserved Words

The following words are reserved by the language and cannot be used as value names, script names, or list names:

`set`, `to`, `show`, `ask`, `read`, `write`, `append`, `from`, `if`, `then`, `repeat`, `times`, `end`, `stop`, `start`, `at`, `run`, `define`, `as`, `script`, `and`, `or`, `not`, `is`, `true`, `false`, `add`, `subtract`, `multiply`, `divide`, `convert`, `number`, `text`, `return`, `pass`, `loop`, `import`, `list`, `put`, `in`, `not in`, `remove`, `through`, `get`, `current`, `item`, `count`, `round`, `floor`, `ceiling`, `power`, `root`, `remainder`, `random`, `absolute`, `minimum`, `maximum`, `percent`, `of`, `length`, `find`, `extract`, `replace`, `with`, `beginning`, `finishing`, `attempt`, `fail`, `reason`, `date`, `time`, `difference`, `between`, `days`, `hours`, `minutes`, `format`, `using`

**Contextual resolution notes:**

- `is`, `not`, `equal`, `to`, `greater`, `less`, `than`, `or` are reserved as standalone tokens but also appear as components of compound comparison operators. When adjacent in a recognized compound sequence, they are parsed as a single token.
- `from`, `as`, `in`, `and` are reserved but appear in multiple contexts. The parser resolves which context applies by surrounding tokens — the presence of `list`, `difference between`, `replace`, or other identifying keywords makes each use unambiguous.
- `days`, `hours`, and `minutes` are reserved as unit keywords. User-defined values named `.days`, `.hours`, or `.minutes` are not affected — the period prefix makes user references unambiguous from bare reserved keywords.
- `fail` appears in `if fail`, `end fail`, and `fail reason`. All uses are resolved by context.
- `current` appears in `current item`. User-defined values use the period prefix and cannot conflict.

### Reserved Symbols

| Symbol | Use |
|---|---|
| `.` | Period — denotes containment in the file, script, value hierarchy. Exclusive to this hierarchy. |
| `#` | Hash — denotes a container tag. Not part of the period chain. |

No other special characters are used by the language.

### Script Self-Reference

`.scriptname.script` used from within `.scriptname` resolves to the script's own identity, not its contents. Self-reference has no practical use in v0.2 and is reserved for future introspection features.

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
    append .name, .phonenumber to .contacts.vern
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

### Safe Input with Error Recovery

```
// Safe number input with recovery — retries up to 3 times

set .value to 0
set .succeeded to false

script .main
    repeat 3 times
        if .succeeded = false
            attempt
                ask .input
                convert .input to number as .value
                set .succeeded to true
            if fail
                show "invalid input: " + fail reason
                show "please enter a number"
            end fail
            end attempt
        end if
    end repeat
    if .succeeded = true
        run .calculate.script
    end if
    if .succeeded = false
        show "no valid input received after 3 attempts"
    end if
end script

script .calculate
    set .doubled to .value * 2
    convert .doubled to text as .doubledtext
    show "result: " + .doubledtext
end script

start at .main.script
stop
```

### Days Until with Date Formatting

```
// Calculate days until a future date

set .target to 2026-12-31
set .remaining to 0

script .main
    get date as .today
    difference between .today and .target in days as .remaining
    convert .remaining to text as .remainingtext
    format .target as .displaytarget using "DD/MO/YYYY"
    show "days until " + .displaytarget + ": " + .remainingtext
end script

start at .main.script
stop
```

### Name Registry with Collections

```
// Name registry using collections

list names
end list

script .main
    run .collect.script
    run .display.script
end script

script .collect
    ask .howmany
    convert .howmany to number as .count
    repeat .count times
        ask .input
        put .input in list names
    end repeat
end script

script .display
    count list names as .total
    convert .total to text as .totaltext
    show "total entries: " + .totaltext
    repeat through list names
        show current item
    end repeat
end script

start at .main.script
stop
```
