# VERN Language Specification v0.7

## Overview

VERN is a controlled natural language programming language designed to make programming accessible to anyone who can read and write in their own language. It uses a simplified, command-style pidgin grammar with a strict but readable rule set, eliminating the translation layer between human intent and executable code. VERN is designed to be readable at a glance, writable without prior programming knowledge, and extensible through a user-defined vocabulary system. The grammar is invariant — it does not change between languages. The vocabulary is replaceable — every keyword maps to an equivalent word or phrase in the target language. Code written in any vocabulary binding executes identically.

This document is the full specification for v0.7, covering syntax, grammar rules, reference system, data handling, collections, dictionaries, nested data structures, imports, extended math, trigonometry, logarithms, mathematical constants, angle conversion, conditionals, repetition, loop control, scripts, script parameters, error recovery, date and time, string operations, file operations, core operations, type checking, number formatting, multi-line text, networking, dynamic file references, typed exception handling, parse and inspect, none type, multiple return values, list and dictionary parameters, and first-class functions.

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
| Folder | `.folder` | `.subfolder.folder` |
| System root | `.parent` | `.parent` |

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

.filename.vern.subfolder.folder
— a file inside a subfolder relative to the program

.filename.vern.subfolder.folder.projectfolder.folder.documents.folder.parent
— a file at an absolute path from system root
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

Containers are denoted by `#`. The `#` symbol is self-identifying and does not use the period chain — the period hierarchy is exclusive to file, script, folder, and value references.

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

### Sort

```
sort list names as list sortednames
sort list names descending as list sortednames
```

Sorts a list and assigns the result to a new named list. Default sort order is ascending. The `descending` modifier reverses the order. The original list is unchanged. The target list must be declared before `sort` is called.

Sorting rules by type: text lists sort alphabetically by Unicode code point order, number lists sort numerically.

```
list scores
    85
    92
    74
    88
end list

list rankedscores
end list

sort list scores descending as list rankedscores
// rankedscores contains: 92, 88, 85, 74
```

### Reverse

```
reverse list names as list reversednames
```

Reverses the order of items in a list and assigns the result to a new named list. The original list is unchanged. The target list must be declared before `reverse` is called.

### Slice

```
slice list names 2 to 4 as list subset
```

Extracts a portion of a list by position range and assigns the result to a new named list. Both positions are inclusive. Positions begin at 1. The original list is unchanged. The target list must be declared before `slice` is called. Position arguments accept literal numbers or value references that hold numbers.

```
list names
    "alice"
    "bob"
    "charlie"
    "diana"
    "eve"
end list

list subset
end list

slice list names 2 to 4 as list subset
// subset contains: "bob", "charlie", "diana"
```

### Combine

```
combine list first with list second as list merged
```

Appends all items from the second list onto the end of the first list and assigns the result to a new named list. Both lists must be the same type. The original lists are unchanged. The target list must be declared before `combine` is called.

```
list first
    "alice"
    "bob"
end list

list second
    "charlie"
    "diana"
end list

list merged
end list

combine list first with list second as list merged
// merged contains: "alice", "bob", "charlie", "diana"
```

### Extended List Error Behaviors

**Sort on empty list** — returns empty list, not an error.

**Reverse on empty list** — returns empty list, not an error.

**Slice position out of range** — fatal. Error log records the positions and the actual list length.

**Slice start position greater than end position** — fatal.

**Combine lists of different types** — fatal. Error log records both list types.

**`descending` outside a sort instruction** — fatal.

---

## Dictionaries

A dictionary is a collection of key-value pairs. Keys are text values. Values may be any single type — text, number, true/false, date, or time. All values in a dictionary must be the same type. A dictionary is homogeneous by value type, the same as a list is homogeneous by item type.

Dictionaries live at the file level only — they cannot be declared inside a script. Like lists and file-level values, dictionaries are accessible to all scripts within the file.

### Declaring a Dictionary

```
dictionary scores
    "alice" : 95
    "bob" : 87
    "charlie" : 72
end dictionary
```

Keys and values are separated by `:`. One key-value pair per line. The block is closed with `end dictionary`. A dictionary may be declared empty — its value type is determined on first insertion.

```
dictionary scores
end dictionary
```

### Adding and Updating a Key

```
put .value in dictionary scores key "alice"
put .value in dictionary scores key .keyname
```

If the key already exists, its value is replaced. If the key does not exist, it is added. The key accepts a text literal or a value reference that holds text.

### Retrieving a Value by Key

```
get dictionary scores key "alice" as .result
get dictionary scores key .keyname as .result
```

Retrieves the value associated with the specified key and assigns it to a named value. If the key does not exist, fatal error.

### Removing a Key

```
remove key "alice" from dictionary scores
remove key .keyname from dictionary scores
```

Removes the key-value pair from the dictionary. If the key does not exist, non-fatal log entry, execution continues.

### Checking if a Key Exists

```
if "alice" is in dictionary scores then show "found"
if "alice" not in dictionary scores then show "not found"
```

`is in` and `not in` are extended to work with dictionaries. The parser resolves which context applies — list, text, or dictionary — by the keyword following: `list`, a value reference, or `dictionary`.

### Counting a Dictionary

```
count dictionary scores as .total
```

Returns the number of key-value pairs as a number type. An empty dictionary returns 0.

### Iterating Through a Dictionary

```
repeat through dictionary scores
    show current key
    show current value
end repeat
```

`current key` and `current value` are implicit read-only two-word keywords available only inside a `repeat through dictionary` block. They hold the key and value of the current pair for that iteration. Both carry no period prefix and cannot be assigned to. Iteration order is insertion order — pairs are visited in the order they were added.

If you need to work with `current key` or `current value` beyond the loop, assign them to values first:

```
repeat through dictionary scores
    set .k to current key
    set .v to current value
    show .k + ": " + .v
end repeat
```

### Cross-File Dictionaries

A dictionary in another file is referenced by appending the file reference after the dictionary name, following the same pattern as cross-file lists:

```
get dictionary scores .filename.vern key "alice" as .result
put .value in dictionary scores .filename.vern key "alice"
count dictionary scores .filename.vern as .total
```

### Dictionary Error Behaviors

**Key not found on get** — fatal. Error log records the dictionary name and the key.

**Type mismatch on put** — fatal. Error log records the value, its type, and the dictionary's value type.

**Remove key not found** — non-fatal. Log entry generated, execution continues.

**`current key` outside a repeat through dictionary block** — fatal.

**`current value` outside a repeat through dictionary block** — fatal.

**Assigning to `current key` or `current value`** — fatal. Both are read-only.

**Duplicate key at declaration** — fatal. Error log records the key and line number.

**Empty dictionary on repeat through** — zero iterations, not an error.

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
convert .valuename to date as .newvaluename
convert .valuename to time as .newvaluename
```

`convert` also accepts bare reserved keywords that hold implicit values. `loop`, `current item`, `current key`, and `current value` are the implicit keywords available inside loop blocks:

```
convert loop to text as .looptext
convert current item to text as .itemtext
convert current key to text as .keytext
convert current value to text as .valuetext
```

Converting a date or time to text produces the raw internal storage string — `YYYY-MM-DD` for dates, `HH:MI:SS` for times. Use `format` for locale-appropriate display.

If the value cannot be converted — for example, converting the text `"hello"` to a number — this is a fatal error. The error log records the value, its current type, and the attempted conversion.

### Full Conversion Type Matrix

| From | To | Valid |
|---|---|---|
| Text | Number | Yes — fatal if text is not a valid number |
| Text | Date | Yes — fatal if text is not exactly `YYYY-MM-DD` |
| Text | Time | Yes — fatal if text is not exactly `HH:MI:SS` |
| Number | Text | Yes |
| Date | Text | Yes — produces raw `YYYY-MM-DD` string |
| Time | Text | Yes — produces raw `HH:MI:SS` string |
| Number | Date | No — fatal |
| Number | Time | No — fatal |
| Date | Number | No — fatal |
| Time | Number | No — fatal |
| Date | Time | No — fatal |
| Time | Date | No — fatal |

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

Conditions in a compound expression are evaluated left to right with short-circuit evaluation. `and` stops at the first false condition. `or` stops at the first true condition.

```
// second condition never evaluated if .count is not greater than 0
if .count is greater than 0 and .total / .count is greater than 10 then show "above average"

// second condition never evaluated if .name = "Gabriel" is already true
if .name = "Gabriel" or .name = "guest" then show "welcome"
```

Because evaluation stops early, condition order affects both safety and behavior. Always put the simpler, safer check first.

Chains longer than two conditions are evaluated left to right with short-circuiting applied at each step. When `and` and `or` appear in the same expression, evaluation is strictly left to right — there is no operator precedence grouping. For clarity when mixing `and` and `or`, consider using nested `if` blocks to make the intended logic explicit.

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

## Trigonometric Operations

All trigonometric operations are non-destructive — they always produce a result assigned to a new named value via `as`. The original value is never modified. All trig operations are strictly numeric.

### Degrees and Radians

By default all trig operations accept angles in degrees. The optional `radians` modifier switches the operation to accept radians instead. The modifier appears between the value reference and `as`.

```
sine .angle as .result
sine .angle radians as .result
```

Default is degrees. `radians` is the explicit opt-in. This applies identically to every trig operation listed below.

### Sine, Cosine, Tangent

```
sine .angle as .result
sine .angle radians as .result

cosine .angle as .result
cosine .angle radians as .result

tangent .angle as .result
tangent .angle radians as .result
```

### Inverse Trig — Arcsine, Arccosine, Arctangent

Inverse trig operations return an angle. By default the result is in degrees. The `radians` modifier returns the result in radians instead.

```
arcsine .value as .result
arcsine .value radians as .result

arccosine .value as .result
arccosine .value radians as .result

arctangent .value as .result
arctangent .value radians as .result
```

### Two-Argument Arctangent

The two-argument form of `arctangent` takes a y-coordinate and an x-coordinate and returns the angle in the correct quadrant. This resolves the quadrant ambiguity of the single-argument form. The parser distinguishes the two forms by the number of value references — one reference is single-argument, two references is two-argument. By default the result is in degrees.

```
arctangent .y .x as .result
arctangent .y .x radians as .result
```

### Hyperbolic Trig

Hyperbolic trig operations do not use angle units — they operate on plain numbers. The `radians` modifier does not apply to hyperbolic operations.

```
hyperbolic sine .value as .result
hyperbolic cosine .value as .result
hyperbolic tangent .value as .result

arc hyperbolic sine .value as .result
arc hyperbolic cosine .value as .result
arc hyperbolic tangent .value as .result
```

### Trig Error Behaviors

**Non-numeric operand** — fatal. Error log records the operation, the value, and its type.

**Arcsine or arccosine with value outside -1 to 1** — fatal. Error log records the operation and the value.

**Arc hyperbolic tangent with value outside -1 to 1** — fatal. Error log records the operation and the value.

**Arc hyperbolic cosine with value less than 1** — fatal. Error log records the operation and the value.

**Tangent of 90 degrees or 270 degrees** — fatal. Tangent is undefined at these angles.

---

## Logarithmic Operations

All logarithmic operations are non-destructive. Results are always assigned to a new named value via `as`. All log operations are strictly numeric. The input value must be positive — logarithms of zero or negative numbers are undefined.

### Natural Logarithm

```
ln .value as .result
```

Returns the natural logarithm (base `e`) of the value.

### Base 10 Logarithm

```
log .value as .result
```

Returns the base 10 logarithm of the value.

### Arbitrary Base Logarithm

```
log .value base .base as .result
log .value base 2 as .result
```

Returns the logarithm of the value in the specified base. The base accepts a literal number or a value reference that holds a number. The base must be positive and not equal to 1.

### Logarithm Error Behaviors

**Input value of zero** — fatal. Logarithm of zero is undefined.

**Input value less than zero** — fatal. Logarithm of a negative number is undefined.

**Non-numeric operand** — fatal. Error log records the operation, the value, and its type.

**Base of zero or one** — fatal. These bases are undefined for logarithms.

**Negative base** — fatal.

---

## Mathematical Constants

VERN provides four reserved numeric constants. Constants carry no period prefix and cannot be assigned to. They are read-only and available anywhere a number value is valid.

| Constant | Value | Meaning |
|---|---|---|
| `pi` | 3.14159265358979... | ratio of a circle's circumference to its diameter |
| `e` | 2.71828182845904... | base of the natural logarithm |
| `tau` | 6.28318530717958... | 2π — full circle in radians |
| `infinity` | ∞ | positive infinity |

```
set .result to pi * .radius power 2
set .result to e power .exponent
set .circumference to tau * .radius
```

`infinity` is primarily used for boundary comparisons:

```
if .value is less than infinity then show "finite"
```

Constants may be used anywhere a number literal or number value reference is valid — in expressions, as operands in math operations, and as bounds in `random`.

### Negative Infinity

Negative infinity is expressed as:

```
set .result to 0 - infinity
```

There is no separate negative infinity constant.

### Constant Error Behaviors

**Assigning to a constant** — fatal. Constants are read-only.

**Using a constant in a non-numeric context** — fatal. Error log records the operation and the constant used.

---

## Angle Conversion

Two explicit conversion operations are provided for converting between degrees and radians.

```
to degrees .value as .result
to radians .value as .result
```

These convert a plain number representing an angle from one unit to the other. The original value is never modified.

```
set .angle to 180
to radians .angle as .angleradians
// .angleradians now holds approximately 3.14159

set .angle to 3.14159
to degrees .angle as .angledegrees
// .angledegrees now holds approximately 180
```

### Angle Conversion Error Behaviors

**Non-numeric operand** — fatal. Error log records the operation, the value, and its type.

---

## Additional Numeric Operations

### Sum

```
sum list numbers as .result
```

Returns the total of all values in a numeric list. The list must be numeric. An empty list returns 0 — not an error. This extends the existing `minimum` and `maximum` list operations with a third aggregate operation.

### Factorial

```
factorial .value as .result
```

Returns the factorial of a non-negative whole number. `factorial 0` returns 1. The input must be a non-negative whole number.

```
set .n to 5
factorial .n as .result
// .result is 120
```

### Combinations

```
combinations .n .k as .result
```

Returns the number of ways to choose `k` items from `n` items without regard to order. Both values must be non-negative whole numbers and `k` must be less than or equal to `n`.

```
set .n to 10
set .k to 3
combinations .n .k as .result
// .result is 120
```

### Permutations

```
permutations .n .k as .result
```

Returns the number of ways to arrange `k` items chosen from `n` items where order matters. Both values must be non-negative whole numbers and `k` must be less than or equal to `n`.

```
set .n to 10
set .k to 3
permutations .n .k as .result
// .result is 720
```

### Sign

```
sign .value as .result
```

Returns `-1` if the value is negative, `0` if the value is zero, and `1` if the value is positive. The result is always a number.

```
set .temperature to 0 - 15
sign .temperature as .direction
// .direction is -1
```

### Additional Numeric Error Behaviors

**Sum on empty list** — returns 0, not an error.

**Sum on non-numeric list** — fatal. Error log records the list name and its type.

**Factorial of a negative number** — fatal.

**Factorial of a non-whole number** — fatal. Error log records the value.

**Combinations or permutations with k greater than n** — fatal.

**Combinations or permutations with negative values** — fatal.

**Combinations or permutations with non-whole numbers** — fatal.

**Non-numeric operand on any additional numeric operation** — fatal. Error log records the operation, the value, and its type.

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

### Otherwise

The `otherwise` keyword extends the `if` block form to handle both the true and false branches in a single structure.

```
if condition
    instructions
otherwise
    instructions
end if
```

Instructions between `if condition` and `otherwise` execute when the condition is true. Instructions between `otherwise` and `end if` execute when the condition is false. Exactly one branch executes per evaluation.

```
if .score is greater than 90
    show "excellent"
    set .grade to "A"
otherwise
    show "try harder"
    set .grade to "F"
end if
```

`otherwise` is only valid inside the `if` block form. It cannot be used with the inline `if / then` form. One `otherwise` per `if` block maximum.

```
// inline — no branching, no otherwise
if .active = true then run .process.script

// block — branching with otherwise
if .active = true
    run .process.script
    show "running"
otherwise
    show "inactive"
end if
```

### Nesting

`if` blocks may be nested inside other `if` blocks, inside `repeat` blocks, inside `while` blocks, and inside `attempt` blocks. `otherwise` branches follow the same nesting rules and may contain nested `if` blocks, `while` loops, `repeat` loops, and `attempt` blocks.

```
if .score is greater than 50
    show "passing"
    if .score is greater than 90
        show "excellent"
    end if
end if
```

### Conditional Error Behaviors

**`otherwise` outside an `if` block** — fatal.

**Multiple `otherwise` keywords in a single `if` block** — fatal.

**`otherwise` used with inline `if / then`** — fatal.

---

## Repetition

### Count-Based Loop

```
repeat n times
    instructions
end repeat
```

The keyword `loop` is available inside every `repeat` block. It holds the current iteration number, starting at 1. `loop` is read-only, carries no period prefix. Attempting to assign to `loop` is a fatal error. Referencing `loop` outside a loop block is a fatal error.

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

### While Loop

```
while condition
    instructions
end while
```

A `while` loop executes its instructions repeatedly for as long as the condition remains true. When the condition becomes false, execution continues after `end while`. If the condition is false on the first check, the loop body never executes — no error.

The condition uses the same syntax as `if`: all comparison operators, `and`, `or`, `not`, membership checks, and list membership checks are valid.

```
while .attempts is less than 5
    ask .input
    set .attempts to .attempts + 1
end while
```

The keyword `loop` is available inside every `while` block, holding the current iteration number starting at 1. `loop` is read-only inside `while` blocks, same as inside `repeat` blocks.

Values created or modified inside a `while` block belong to the enclosing script's scope and persist after the loop ends.

A condition that never becomes false produces an infinite loop. This is intentional behavior — game loops, server loops, and run-until-interrupted patterns require it. VERN does not prevent infinite loops. This is the user's responsibility, the same as recursive script calls.

```
while true
    run .server.script
end while
```

### While Loop Error Behaviors

**Assigning to loop inside a while block** — fatal.

**Referencing loop outside any loop block** — fatal.

**Type conflict in condition** — fatal. Error log records the operation and types involved.

---

## Loop Control

### Exit Loop

`exit loop` immediately stops the current loop and continues execution after the loop's closing `end repeat` or `end while`. It is valid inside `repeat`, `repeat through`, and `while` blocks.

```
repeat 10 times
    if loop = 5 then exit loop
    show loop
end repeat
// displays 1, 2, 3, 4 — stops before 5
```

```
while .active = true
    ask .input
    if .input = "quit" then exit loop
end while
```

`exit loop` is valid in the inline `if / then` form and inside `if` blocks. It exits the immediately enclosing loop — in nested loops, it exits the innermost loop only.

```
repeat 3 times
    repeat 3 times
        if loop = 2 then exit loop   // exits inner loop only
    end repeat
    show loop                         // outer loop continues
end repeat
```

### Next Item

`next item` skips the remainder of the current iteration and moves immediately to the next one. It is valid inside `repeat`, `repeat through`, and `while` blocks.

```
repeat 5 times
    if loop = 3 then next item
    show loop
end repeat
// displays 1, 2, 4, 5 — skips iteration 3
```

```
repeat through list names
    if current item = "skip me" then next item
    show current item
end repeat
```

Like `exit loop`, `next item` is valid in the inline `if / then` form and inside `if` blocks. In nested loops it affects the immediately enclosing loop only.

### Compound Token Resolution

`exit` and `next` are reserved as components of their respective compounds. Neither is valid as a standalone instruction. `exit` is only valid immediately preceding `loop`. `next` is only valid immediately preceding `item`.

`loop` already exists as the implicit loop counter keyword. `item` already exists as the second word of `current item`. Both retain their existing roles — `exit loop` and `next item` are resolved as compounds only when `exit` or `next` precedes them respectively.

| Compound | Resolution |
|---|---|
| `exit loop` | exit the current loop immediately |
| `next item` | skip to the next iteration |
| `loop` alone | implicit loop counter — existing behavior unchanged |
| `current item` | implicit current list item — existing behavior unchanged |
| `item` alone | not valid as a standalone token |
| `exit` alone | fatal — must be followed by `loop` |
| `next` alone | fatal — must be followed by `item` |

### Loop Control Error Behaviors

**`exit loop` outside a loop block** — fatal.

**`next item` outside a loop block** — fatal.

**`exit` not followed by `loop`** — fatal.

**`next` not followed by `item`** — fatal.

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

### Nested Scripts

Defining a script inside another script is not supported and is a fatal error. This is a deliberate design decision. VERN is entirely command-driven — nothing runs unless explicitly called with `run`. A script defined at file level with a clear name is unambiguous, accessible only when explicitly called, and fully visible in the file structure.

The `run` command calling scripts from within scripts already provides equivalent functionality:

```
script .main
    if .value = true
        run .helper.script
    end if
end script

script .helper
    show "hello"
end script
```

`.helper` is defined at file level but the relationship between `.main` and `.helper` is effectively the same as nesting. `.helper` will never run unless something explicitly calls it with `run`.

**Defining a script inside another script** — fatal. Error log records the line number where the nested definition begins.

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

## Script Parameters

Scripts may declare named input parameters. Parameters allow a script to receive values directly when called, rather than relying exclusively on file-level values.

### Declaring Parameters

Parameters are declared on the same line as the script definition, after the script name, using `takes`:

```
script .greet takes .name
    show "hello " + .name
end script
```

Multiple parameters are separated by commas:

```
script .add takes .first, .second
    set .total to .first + .second
    return .total pass to .answer
end script
```

Parameters are local to the script. They behave identically to values declared inside the script — they are in scope for the duration of the script and are not accessible outside it.

### Passing Values to a Script

Values are passed to a script when it is called using `with`:

```
run .greet.script with "Alice"
run .greet.script with .username
```

Multiple values are passed in order, separated by commas:

```
run .add.script with 10, 20
run .add.script with .value1, .value2
```

Values are matched to parameters by position — the first value passed maps to the first parameter declared, the second to the second, and so on.

### Parameters and Containers

A script with parameters may still be tagged with a container. The container tag follows the parameter list on the `run` call:

```
run .greet.script with .username #english
run .greet.script with .username #spanish
```

### Scripts Without Parameters

Scripts without parameters continue to work exactly as before. The `takes` keyword is optional — a script that needs no input simply omits it. All existing scripts are unaffected.

### Return Values

Scripts with parameters use `return` and `pass to` identically to scripts without parameters. The destination must be a file-level value declared before the script runs.

```
set .answer to 0

script .add takes .first, .second
    set .total to .first + .second
    return .total pass to .answer
end script

run .add.script with 10, 20
show .answer
// displays 30
```

### Script Parameter Error Behaviors

**Wrong number of values passed** — fatal. Error log records the script name, the number of parameters declared, and the number of values passed.

**Type mismatch between passed value and parameter usage** — fatal at the point of use inside the script, following existing type rules. Parameters are not typed at declaration — the type is determined by what is passed and enforced when the parameter is used in an operation.

**Passing values to a script that declares no parameters** — fatal.

**Referencing a parameter outside its script** — fatal.

**`takes` on a script definition with no parameter names following** — fatal.

---

### Inline Return Assignment (Form 2)

Scripts may use a second return form where the destination is declared inline on the `run` call rather than pre-declared at the file level.

**Calling side:**
```
run .scriptname.script with .value1, .value2 as .result
```

**Script side:**
```
script .scriptname takes .param1, .param2
    // ... instructions ...
    return .output
end script
```

The `as .result` on the `run` line creates the destination value inline. No pre-declaration required. The called script uses bare `return .valuename` with no `pass to` destination.

**Rules:**
- A single script definition uses either Form 1 (`pass to`) or Form 2 (bare `return`), not both
- `return` without `as` on the caller — non-fatal, returned value discarded silently
- `as` on the caller without `return` in the script — fatal
- `return` ends script execution immediately in single-return scripts
- In multiple-return scripts (see below), execution continues past each `return`
- `return` is only valid inside a script

**Error Behaviors:**
- `as` on caller but no `return` in script — fatal. Error log records script name and line of `run` call
- `return` outside a script — fatal
- `return` with no value reference — fatal
- Parameter count mismatch — fatal. Error log records script name, expected count, actual count

---

### Multiple Return Values

A script may contain multiple `return` statements in sequence. Each hands back one value. On the calling side, a comma-separated list of names after `as` receives each value in order.

```
script .minmax takes .first, .second
    set .low to minimum .first .second
    set .high to maximum .first .second
    return .low
    return .high
end script

run .minmax.script with 10, 45 as .minimum, .maximum
```

**Rules:**
- Return values matched positionally — first `return` to first `as` name, second to second
- Fewer `as` names than `return` statements — non-fatal, extras discarded
- More `as` names than `return` statements — fatal
- Multiple `return` with `pass to` — fatal
- `return` statements must be at script top level — not inside `if`, `while`, `repeat`, or `attempt` blocks

---

### List and Dictionary Parameters

Scripts may accept lists and dictionaries as parameters alongside value parameters.

**List parameters** use no period prefix in `takes`:
```
script .finditem takes list searchlist, .searchvalue
```

**Dictionary parameters** use no period prefix in `takes`:
```
script .getvalue takes dictionary sourcedict, .searchkey
```

**Passing on the calling side:**
```
run .finditem.script with list names, "bob" as .position
run .getvalue.script with dictionary scores, "alice" as .result
```

Inside the script, list parameters are used with `list parametername` (no period). Dictionary parameters are used with `dictionary parametername` (no period).

List and dictionary parameters are references to the originals — modifications affect the original.

**Positional rules:**
- `list` in `takes` — valid only immediately before a parameter name in a `takes` declaration
- `dictionary` in `takes` — valid only immediately before a parameter name in a `takes` declaration
- `list` in `with` — valid as a parameter passing marker when following `with` or a comma in a `run` call
- `dictionary` in `with` — valid as a parameter passing marker when following `with` or a comma in a `run` call

**Error Behaviors:**
- Type mismatch on parameter — fatal
- Wrong parameter count — fatal

---

### First-Class Functions

Scripts may be passed as parameters to other scripts and executed from within them.

**Declaring a script parameter:**
```
script .processlist takes list numbers, script operation
```

**Passing a script reference:**
```
run .processlist.script with list numbers, script .double.script
```

The full script reference (`.scriptname.script`) is required. Script parameter names carry no period prefix.

**Executing the passed script:**
```
invoke script operation
invoke script operation with .current as .result
```

**Rules:**
- `invoke` is valid only inside a script
- Script parameters are file-scope only — only file-level scripts may be passed
- A script parameter may be invoked more than once
- `invoke` always uses the `script` keyword

**Contextual resolution for `script`:**
- Opening keyword of a script definition — existing behavior
- Following `with` or comma in a `run` call — script parameter passing
- Following `takes` or comma in a `takes` declaration — script parameter declaration
- Following `invoke` — script parameter execution

**New reserved word:** `invoke`

**Positional rule for `invoke`:** valid only as the opening keyword of an invoke instruction inside a script. Must be followed by `script` and a declared script parameter name.

**Error Behaviors:**
- `invoke` outside a script — fatal
- `invoke` without `script` keyword — fatal
- `invoke script` followed by undeclared parameter name — fatal
- Passing a non-file-level script reference — fatal at load time
- Wrong parameter count — fatal
- `invoke` on a non-script parameter — fatal

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

The `attempt` construct allows a program to handle failures gracefully and continue running. Wrapping instructions in an `attempt` block makes those instructions recoverable.

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

### fail type

`fail type` is an implicit read-only two-word keyword available inside any `if fail` block. The interpreter populates it automatically when a failure occurs. It returns one of four category strings:

| Category | Covers |
|---|---|
| `"type"` | Type conflicts, invalid type conversions |
| `"file"` | File not found, directory missing, permission denied |
| `"network"` | Connection failures, timeouts, invalid URLs |
| `"value"` | Undefined value references, position out of range, invalid math |

```
attempt
    fetch .url as .response
if fail
    show fail type
    show fail reason
end fail
end attempt
```

`fail type` is read-only. Attempting to assign to it is fatal. Valid only inside an `if fail` block.

### Typed Fail Handlers

A typed fail handler runs automatically when a failure's category matches its declared type:

```
attempt
    fetch .url as .response
if fail "network"
    show "connection failed"
if fail "type"
    show "wrong data type"
if fail
    show "unexpected error:", fail reason
end fail
end attempt
```

**Rules:**
- Typed handlers must appear before the catch-all `if fail`
- The catch-all runs for any failure that doesn't match a typed handler
- Multiple handlers for the same category in one `attempt` block — fatal
- Category string must be one of the four valid values — any other string is fatal

**Error Behaviors:**
- `fail type` outside an `if fail` block — fatal
- Assigning to `fail type` — fatal
- Typed handler with unrecognized category string — fatal
- Typed handler appearing after the catch-all — fatal

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

VERN has two date and time primitive types: `date` and `time`. These join text, number, and true/false as the five primitive types of the language.

### Date Type

A date value holds a calendar date in the format `YYYY-MM-DD`. The parser recognizes this format and infers the date type automatically.

```
set .birthday to 1990-03-15
set .deadline to 2026-12-31
```

`YYYY-MM-DD` is the only valid literal date format.

### Time Type

A time value holds a time of day in the format `HH:MI:SS` using 24-hour notation. The parser recognizes this format and infers the time type automatically.

```
set .alarm to 07:30:00
set .meetingtime to 14:30:00
```

`HH:MI:SS` is the only valid literal time format.

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

### Text to Date and Time Conversion

Text values may be converted to date or time types using the `convert` keyword. The input text must match the VERN literal format exactly: `YYYY-MM-DD` for dates, `HH:MI:SS` for times. No other format is accepted. If the text does not match exactly, this is a fatal error.

```
set .input to "2026-12-31"
convert .input to date as .deadline

set .clockinput to "14:30:00"
convert .clockinput to time as .meetingtime
```

`ask` always returns text. If a user enters a date or time, the text must be in the correct format before conversion will succeed. The recommended pattern for accepting dates or times from users combines `while` and `attempt`:

```
set .valid to false

while .valid = false
    ask .inputdate
    attempt
        convert .inputdate to date as .cleandate
        set .valid to true
    if fail
        show "invalid format, please use YYYY-MM-DD"
    end fail
    end attempt
end while
```

The `attempt` block catches invalid input without halting the program. The `while` loop keeps asking until a valid date is entered. Once `.valid` is true the loop exits and `.cleandate` is available for use. This pattern works identically for time input — substitute `to time` and the appropriate format message.

This is the standard pattern for validated user input in VERN. It applies to any situation where user input must meet a specific format or type requirement before the program can proceed.

If your program must accept dates or times in a format other than `YYYY-MM-DD` or `HH:MI:SS`, use `extract` and `replace` to reshape the text into the required format first, then convert.

### Date and Time Type Rules

- Math operators cannot be applied to date or time values — use `difference between` for date/time arithmetic
- Comparison operators work on date and time values — earlier dates/times are less than later ones
- `convert` can convert a date or time to text — produces the raw internal storage string (`YYYY-MM-DD` or `HH:MI:SS`). Use `format` for locale-appropriate display.

### Date and Time Error Behaviors

**Invalid date literal** — fatal. Error log records the invalid literal and line number.

**Invalid time literal** — fatal. Error log records the invalid literal and line number.

**Math on date or time** — fatal. Use `difference between`.

**Difference between mismatched types** — fatal. Error log records the types involved.

**Invalid format code** — non-fatal. The code is passed through as literal text. Log entry generated.

**format applied to non-date/time value** — fatal.

**Text does not match required format on convert to date or time** — fatal. Error log records the value content and the attempted target type.

**Converting number to date or time** — fatal.

**Converting date to time or time to date** — fatal.

**Converting an uninitialized value** — fatal. Error log records the value name and line number.

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

### Split

```
split .text by "," as list parts
split .text by .delimiter as list parts
```

Splits a text value into a list of text values at every occurrence of the specified delimiter. The delimiter is consumed — it does not appear in the results. The result is always a list of text type values.

If the delimiter is not found, the result is a list containing the original text as a single item — not an error. If the input text is empty, the result is an empty list. The target list must be declared before `split` is called. If the list already contains items, `split` replaces all existing contents with the new items.

```
set .csv to "alice,bob,charlie"
split .csv by "," as list names
// list names contains: "alice", "bob", "charlie"
```

### Join

```
join list names by "," as .result
join list names by .separator as .result
```

Combines all items in a list into a single text value, placing the specified separator between each item. The list must be text type. The result is a text value. If the list is empty, the result is an empty string — not an error.

```
join list names by ", " as .result
// .result is "alice, bob, charlie"
```

### Trim

```
trim .text as .result
```

Removes whitespace characters — spaces, tabs, newlines — from the beginning and end of a text value. Characters in the middle of the text are not affected.

```
set .input to "  hello  "
trim .input as .clean
// .clean is "hello"
```

### Uppercase and Lowercase

```
uppercase .text as .result
lowercase .text as .result
```

`uppercase` converts all characters to their uppercase equivalents. `lowercase` converts all characters to their lowercase equivalents. Characters with no case equivalent — numbers, punctuation, symbols — are unchanged.

```
uppercase .name as .shout
lowercase .name as .quiet
```

### Starts With and Ends With

```
if .text starts with "hello" then show "found"
if .text ends with "world" then show "found"
```

`starts with` and `ends with` are compound condition keywords used exclusively in `if` statements — both inline and block form. They evaluate to true or false. Both checks are case-sensitive. Both accept a text literal or a value reference that holds text as the comparison value.

```
if .filename ends with ".vern"
    show "vern file"
otherwise
    show "not a vern file"
end if
```

### Extended String Error Behaviors

**Split with empty delimiter** — fatal. An empty string is not a valid delimiter.

**Join on non-text list** — fatal. Error log records the list name and its type.

**`starts with` or `ends with` outside an `if` statement** — fatal.

**`starts with` or `ends with` with non-text comparison value** — fatal.

---

## File Operations

VERN provides five file operations: `read`, `write`, `append`, `delete`, and `exist`. All file references use the standard period chain, extended with `.folder` and `.parent` descriptors for directory navigation.

### File Reference and Directory Navigation

File references follow the minimum context rule. If the file is in the same directory as the program, `.filename.vern` is sufficient. For files in other locations, extend the chain using `.folder` and `.parent` descriptors.

```
.filename.vern
— a file in the same directory as the program

.filename.vern.subfolder.folder
— a file inside a subfolder relative to the program

.filename.vern.subfolder.folder.projectfolder.folder.documents.folder.parent
— a file at an absolute path from system root
```

**Descriptor rules:**
- Every folder name must be followed by `.folder`
- Every file name must be followed by `.vern`
- `.parent` means system root — valid anywhere in the chain, once per chain only
- Two `.parent` descriptors in one chain — fatal
- Any name not followed by a valid descriptor — fatal
- Minimum context rule applies — only extend the chain as far as needed to be unambiguous

Chains without `.parent` are relative to the program's working directory. Chains with `.parent` are absolute from system root. These are the only two modes.

Platform-specific path separators (`/` on Unix, `\` on Windows) are handled by the execution engine. The user never writes a separator character.

### Checking if a File Exists

```
if .filename.vern exist then run .process.script
```

`exist` is a condition keyword used exclusively in `if` statements. It evaluates to true if the file is present and accessible, false if it is not. All standard `if` forms are valid — inline and block, with and without `otherwise`.

```
if .filename.vern exist
    read .name from .filename.vern
otherwise
    show "file not found"
end if
```

`exist` may also be used with directory references:

```
if .subfolder.folder exist then run .process.script
```

### Reading from a File

```
read .valuename from .filename.vern
read .value1, .value2 from .filename.vern
```

Values are read in order, mapping to lines 1, 2, 3 in the file. If fewer lines exist than values requested, fatal error. Excess lines are ignored.

### Writing to a File

```
write .valuename to .filename.vern
write .value1, .value2 to .filename.vern
```

`write` replaces all existing file content. If the file does not exist, VERN creates it automatically. If the directory does not exist, fatal error.

### Appending to a File

```
append .valuename to .filename.vern
append .value1, .value2 to .filename.vern
```

`append` adds to the end of an existing file without overwriting. If the file does not exist, VERN creates it automatically.

### Deleting a File

```
delete .filename.vern
```

`delete` permanently removes the file from the system. This operation is irreversible — the file is not moved to a trash or recycle location, it is deleted. The recommended pattern is to check existence before deleting:

```
if .filename.vern exist then delete .filename.vern
```

Deleting a file that does not exist is a fatal error. Always check with `exist` first if the file's presence is not guaranteed.

### Listing Files in a Directory

```
get files in .foldername.folder as list filenames
get files in .parent as list filenames
```

Returns all files in the specified directory as a list of text values. Each item in the list is a filename including its extension. The list is unordered. An empty directory returns an empty list — not an error.

`get files` returns all files regardless of extension. To work with only `.vern` files or any other specific type, filter the list using existing string operations after retrieval.

```
list filenames
end list

script .main
    get files in .projects.folder as list filenames
    repeat through list filenames
        show current item
    end repeat
end script
```

### File Operation Error Behaviors

**File not found on read** — fatal. Error log records the filename and line number.

**Fewer lines in file than values requested** — fatal. Error log records the filename, lines available, and values requested.

**Directory does not exist on write or append** — fatal.

**Deleting a file that does not exist** — fatal. Use `exist` to check first.

**Permission denied on any file operation** — fatal. Error log records the directory, filename, and operation attempted.

**`.parent` appearing more than once in a chain** — fatal.

**Directory name not followed by `.folder`** — fatal.

**File name not followed by `.vern`** — fatal.

**`get files` on an empty directory** — returns empty list, not an error.

**`exist` outside an `if` statement** — fatal.

---

## Dynamic File References

A dynamic file reference uses a text value in place of a literal file chain. The keyword `path` signals that what follows is a text value containing a file reference.

### Syntax

```
write .entry to path .filename
read .entry from path .filename
append .entry to path .filename
delete path .filename
if path .filename exist then run .process.script
```

`.filename` must be a text value holding a complete valid file reference string including `.vern`.

### Building at Runtime

```
get date as .today
format .today as .datetext using "YYYY-MM-DD"
set .filename to .datetext + ".vern.logs.folder"
write .entry to path .filename
```

### Positional Rule for `path`

`path` is valid in exactly four positions:
1. Immediately after `to` in a `write` or `append` instruction
2. Immediately after `from` in a `read` instruction
3. As the first token after `delete` (in file context — chain containing `.vern`)
4. As the first token after `if` in an `exist` check

Any other position is fatal.

### Reserved Word

`path` is added to the reserved word list.

### Error Behaviors

- Value is not text type — fatal
- Value does not end in `.vern` — fatal
- Value contains invalid path string — fatal
- Directory does not exist — fatal
- File not found on read — fatal
- `path` in any other position — fatal

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

## v0.5 Limitations

---

## Type Checking

The `type of` operation returns the data type of a value as a text string. This allows programs to inspect what kind of data a value holds before operating on it — useful when values come from user input, file reads, or script parameters whose type may not be known at write time.

### Syntax

```
type of .value as .result
```

The result is always a text type value. It is assigned to a new named value via `as`. The original value is never modified.

### Valid Return Values

| Type | Returns |
|---|---|
| Text | `"text"` |
| Number | `"number"` |
| True/False | `"true/false"` |
| Date | `"date"` |
| Time | `"time"` |
| Dictionary reference | `"dictionary"` |
| None | `"none"` |

### Usage with Implicit Loop Keywords

`type of` also accepts `current item`, `current key`, and `current value` as its subject, following the same pattern as `convert`:

```
repeat through list names
    set .working to current item
    type of .working as .kind
    show .kind
end repeat
```

Or directly:

```
repeat through list names
    type of current item as .kind
    show .kind
end repeat
```

Both forms are valid.

### Practical Example

```
script .inspect takes .incoming
    type of .incoming as .kind
    if .kind = "number" then run .processnumber.script
    if .kind = "text" then run .processtext.script
end script
```

### Type Checking Error Behaviors

**`type of` on an uninitialized value** — fatal. Error log records the value name and line number.

**`type of current item` outside a `repeat through list` block** — fatal.

**`type of current key` outside a `repeat through dictionary` block** — fatal.

**`type of current value` outside a `repeat through dictionary` block** — fatal.

**`type` used outside the `type of` compound** — fatal. `type` is only valid as the first word of `type of`.

**`of` in any position other than its two documented valid positions** — fatal.

---

## None Type

`none` is a sixth primitive type representing an intentionally empty value. It is distinct from an uninitialized value (which is always fatal to reference) and from an empty string (which is a valid text value).

### Declaring a None Value

```
set .result to none
```

A value holding `none` is initialized and exists — it simply holds no data.

### Checking for None

```
if .result = none then show "nothing found"
if .result != none then run .process.script
```

`none` is comparable with `=` and `!=` in any `if` condition.

### Using None in Operations

Using a `none` value in any operation expecting a real type is fatal — consistent with all other type conflicts. The programmer must check and assign a default first:

```
if .result = none then set .result to 0
set .total to .result + 10
```

### None and show

`show` displays `none` as the literal text `none` without quotes. Consistent with how `true` and `false` are displayed.

### None and convert

`convert` on a `none` value is fatal. Assign a real value first.

### None in Lists and Dictionaries

`none` is valid in lists and dictionaries subject to the homogeneity rule. A list or dictionary of `none` values is valid. Mixing `none` with other types is fatal.

### None as a Return Value

A script may `return .result` where `.result` holds `none` to signal no result was produced.

### Reserved Word

`none` is added to the reserved word list.

**Positional rule:** valid as a value in `set`, as a comparison target in `if` conditions, as a `return` value, and as a list or dictionary item. Any other position is fatal.

### Error Behaviors

- Using `none` in a math, string, date, or time operation — fatal
- `convert` on `none` — fatal
- Mixing `none` with other types in a list or dictionary — fatal

---

## Number Formatting for Display

The `format` instruction is extended to handle number values in addition to dates and times. Number formatting prepares a number for display by controlling decimal places, thousands separators, and minimum display width. The result is always a text value assigned to a new named value via `as`. The original number is never modified.

The parser distinguishes number formatting from date/time formatting by what follows the result reference — date/time formatting is always followed by `using`, number formatting is followed by one or more of: `decimals`, `thousands`, or `padded`.

### Syntax

```
format .number as .result decimals 2
format .number as .result thousands
format .number as .result decimals 2 thousands
format .number as .result padded 8
format .number as .result decimals 2 thousands padded 10
```

Modifiers may be combined in any order. At least one modifier must be present — `format .number as .result` with no modifiers following is fatal.

### Modifiers

**`decimals n`** — rounds the number to `n` decimal places and displays exactly `n` digits after the decimal point. Rounding follows standard mathematical rounding — 0.5 rounds up. `n` must be a whole number greater than or equal to 0. `decimals 0` rounds to a whole number and displays no decimal point. When combined with `thousands`, `decimals` is always processed first regardless of the order the modifiers are written.

```
set .price to 3.14159
format .price as .display decimals 2
// .display is "3.14"

set .total to 1.5
format .total as .display decimals 0
// .display is "2"
```

**`thousands`** — inserts a comma `,` as a thousands separator every three digits to the left of the decimal point. When combined with `decimals`, the thousands separator is applied after rounding and decimal formatting regardless of the order the modifiers are written.

```
set .population to 1234567
format .population as .display thousands
// .display is "1,234,567"
```

**`padded n`** — pads the result with spaces on the left until the total display width reaches `n` characters. Useful for aligning columns of numbers in output. If the formatted number is already `n` characters or longer, no padding is added — not an error.

```
set .score to 42
format .score as .display padded 6
// .display is "    42"
```

### Combining Modifiers

```
set .amount to 9876543.2
format .amount as .display decimals 2 thousands
// .display is "9,876,543.20"

format .amount as .display decimals 2 thousands padded 15
// .display is "  9,876,543.20"
```

When `decimals` and `thousands` are both present, `decimals` is processed first then `thousands` is applied, regardless of the order written. When `padded` is present, padding is applied last to the fully formatted string.

### Separator Characters

The decimal separator is `.` and the thousands separator is `,`. These are fixed. Locale-specific separator characters are a known limitation of v0.6 — this will be addressed by the container system in a future version.

### Number Formatting Error Behaviors

**`format` on a non-number value with number formatting modifiers** — fatal. Error log records the value, its type, and the line number.

**`decimals` with a negative number** — fatal.

**`decimals` with a non-whole number** — fatal.

**`padded` with a value less than or equal to zero** — fatal.

**`padded` with a non-whole number** — fatal.

**`format .number as .result` with no modifiers following** — fatal. At least one modifier is required for number formatting.

**`decimals`, `thousands`, or `padded` outside a `format` instruction** — fatal.

---

## Multi-Line Text

A text block declares a value that holds text spanning multiple lines. This allows long or structured text to be written directly in the source file without concatenation. The result is a text type value — it behaves identically to any other text value once assigned.

### Syntax

```
text .valuename
    first line of content
    second line of content
    third line of content
end text
```

The block opens with `text .valuename` and closes with `end text`. Everything between the opening and closing lines is treated as raw text content. Reserved words inside a text block are not parsed as keywords — they are literal content.

The value `.valuename` is assigned the full content of the block with a newline character between each line. Leading whitespace on each line is stripped — indentation inside the block is cosmetic, consistent with the rest of the language.

### Where Text Blocks Live

Text blocks are declared at the file level only, the same as lists and dictionaries. They cannot be declared inside a script. Like file-level values, the declared value is accessible to all scripts within the file.

### Display

When shown, the newlines in the value are honored — each line displays on its own line:

```
text .welcome
    welcome to the program
    please read the instructions carefully
    press enter to continue
end text

script .main
    show .welcome
end script
```

Output:
```
welcome to the program
please read the instructions carefully
press enter to continue
```

### Display with Mixed Values

When a multi-line text value appears in a `show` instruction alongside other values, newlines inside the value are honored as-is. Each value in the comma-separated list is displayed in sequence:

```
set .greeting to "hello"
set .farewell to "goodbye"

text .message
    line one
    line two
end text

show .greeting, .message, .farewell
```

Output:
```
hello
line one
line two
goodbye
```

### Using a Text Block Value

The assigned value is a standard text type. All string operations apply — `length of`, `find`, `extract`, `replace`, `trim`, `uppercase`, `lowercase`, `starts with`, `ends with`, `split`. Concatenation with `+` is valid.

```
text .template
    hello
    your score is
    thank you for playing
end text

length of .template as .len
```

### Known Limitation

Leading whitespace on any line inside a text block is stripped. If leading spaces are required in the content, build the text using concatenation instead.

### Multi-Line Text Error Behaviors

**`end text` with no matching opening `text` block** — fatal.

**`text` block opened but never closed** — fatal. Error log records the line where the block opened.

**`text` block declared inside a script** — fatal. Text blocks are file-level only.

**`text` used as a standalone keyword outside a block declaration** — fatal. `text` in this position is only valid as the opening of a `text .valuename` block declaration.

**Empty text block** — the value is assigned an empty string. Not an error.

---

## Networking

VERN supports four HTTP methods as core language operations.

| Keyword | HTTP Method | Purpose |
|---|---|---|
| `fetch` | GET | Retrieve data from a URL |
| `send` | POST | Send data to a URL, create a resource |
| `update` | PUT | Send data to a URL, update an existing resource |
| `delete` (URL form) | DELETE | Tell a URL to remove a resource |

### fetch — HTTP GET

```
fetch .url as .response
fetch .url as .response status .code
fetch .url with headers dictionary headersdict as .response
fetch .url with headers dictionary headersdict as .response response headers .responseheaders status .code
```

### send — HTTP POST

```
send .data to .url
send .data to .url status .code
send .data to .url with headers dictionary headersdict status .code
```

### update — HTTP PUT

```
update .data to .url
update .data to .url status .code
update .data to .url with headers dictionary headersdict status .code
```

No response body is captured from `update`.

### delete — HTTP DELETE (URL form)

```
delete .url
delete .url status .code
delete .url with headers dictionary headersdict status .code
```

**Contextual resolution for `delete`:**
- `delete` followed by a chain containing `.vern` — file deletion (existing behavior)
- `delete` followed by a single period-prefixed value name with no `.vern` — HTTP DELETE

The distinction is enforced by existing syntax rules — file references always contain `.vern`.

### Request Headers

Declare headers as a standard VERN dictionary. Pass with `with headers dictionary`:

```
dictionary authheaders
    "Authorization" : "Bearer mytoken"
    "Content-Type" : "application/json"
end dictionary

fetch .url with headers dictionary authheaders as .response
```

`with headers dictionary` comes after the URL and before `as` in `fetch`. Comes after `to .url` in `send` and `update`. Comes after `.url` in `delete`.

### Status Codes

Capture the server's response code with `status`:

```
fetch .url as .response status .code
```

`.code` receives a number type value. Non-200 status codes are not automatically fatal — the program is responsible for checking.

### Response Headers

Capture response headers with `response headers`:

```
fetch .url as .response response headers .responseheaders status .code
get dictionary .responseheaders key "Content-Type" as .contenttype
```

Response headers only available on `fetch`. Comes after `as .response` and before `status`.

### Full Combination Order

```
fetch .url with headers dictionary headersdict as .response response headers .responseheaders status .code
```

### New Reserved Words

`update`, `headers`, `status`, `response` are added to the reserved word list.

**Positional rules:**
- `update` — valid only as opening keyword of an update instruction
- `with headers dictionary` — after URL and before `as` in fetch; after `to .url` in send/update; after `.url` in delete
- `response headers` — after `as .result` in fetch only
- `status` — after `as .result` and `response headers` where applicable, or directly after URL on operations with no response body

### URL Values

URLs are plain text values. They follow no special syntax rules in VERN — the language passes them to the underlying HTTP implementation as-is. Constructing a URL dynamically uses standard concatenation:

```
set .base to "https://api.example.com/user/"
set .userid to "gabriel"
set .url to .base + .userid
fetch .url as .response
```

### Error Behaviors

- Non-text URL value — fatal. Error log records the value and its type.
- Uninitialized URL value — fatal. Error log records the value name and line number.
- Headers dictionary contains non-text values — fatal
- `with headers dictionary` followed by undeclared dictionary name — fatal
- Network failure at runtime — fatal by default, recoverable inside `attempt`, `fail type` resolves to `"network"`
- `response headers` used on `send`, `update`, or `delete` — fatal
- `fetch` returns an empty response body — result assigned empty string, not an error

---

## Parse and Inspect

`parse` and `inspect` are core language operations built into the interpreter. No import required.

### parse

Converts raw structured text into VERN dictionaries and lists.

```
parse json .valuename as dictionary resultname
parse json .valuename as list resultname
parse csv .valuename as list resultname
parse xml .valuename as dictionary resultname
parse ini .valuename as dictionary resultname
```

**Supported formats:**

| Identifier | Format | Returns |
|---|---|---|
| `json` | JavaScript Object Notation | list or dictionary |
| `csv` | Comma-Separated Values | list |
| `xml` | Extensible Markup Language | dictionary |
| `ini` | Configuration file format | dictionary |

Format identifiers are proper nouns — not translated in any language binding.

**Type rule:** All parsed values are always text type. No type inference. The homogeneity rule is always satisfied.

**Three supported data patterns:**
1. Single record → dictionary
2. List of records → list of dictionaries
3. Record containing lists → dictionary whose values may be lists

**CSV specifics:** First row is the header. Each subsequent row becomes a dictionary. Empty CSV (header only) returns empty list.

**XML specifics:** Attributes included as dictionary keys. Attribute/child key collision — attribute wins, warning logged. Structures exceeding four nesting levels — fatal.

**INI specifics:** Each section becomes a key. Keys outside any section grouped under `"default"`. Both `=` and `:` separators supported. Comments with `;` or `#` ignored. Duplicate keys — last wins, warning logged. Empty INI returns empty dictionary.

**JSON specifics:** Declare `as list` or `as dictionary` based on the actual data structure. Use `inspect json` first when the structure is unknown.

**Nested dictionary access after parse:** Values retrieved from parsed structures that are themselves dictionaries must be accessed using the dot-ref form:
```
parse json .response as dictionary data
get dictionary data key "details" as .details
get dictionary .details key "city" as .city
```

### inspect

Prints the structure of raw structured text to the terminal. Development tool only.

```
inspect json .valuename
inspect csv .valuename
inspect xml .valuename
inspect ini .valuename
```

No `as` clause. Returns nothing. Not for use in production programs.

**Output format:**
```
dictionary — 3 keys
  "city" — text
  "temperature" — text
  "condition" — text
```

### Reserved Words

`parse`, `inspect`, `json`, `csv`, `xml`, `ini` are added to the reserved word list. Format identifiers are proper nouns and not translated.

**Positional rules:**
- `parse` — valid only as opening keyword of a parse instruction
- `inspect` — valid only as opening keyword of an inspect instruction
- Format identifiers — valid only immediately after `parse` or `inspect`

### Error Behaviors

- Value is not text — fatal
- Empty string — fatal for json/csv/xml; non-fatal for ini (returns empty dictionary)
- Invalid format content — fatal
- Structure outside three supported patterns — fatal
- `as list` when JSON is a single object — fatal
- `as dictionary` when JSON is an array — fatal
- CSV rows with inconsistent field counts — fatal
- XML nesting exceeds four levels — fatal
- `inspect` used with `as` — fatal

---

## Nested Data Structures

VERN supports two forms of nested data structures: dictionaries whose values are dictionaries, and lists whose items are dictionaries. Both are built from flat file-level declarations linked by reference — nothing is physically nested in the source file.

### Dictionary of Dictionaries

Inner dictionaries are declared at the file level as normal dictionaries. The outer dictionary references them by name as its values. All values in the outer dictionary must be dictionaries — the homogeneity rule applies.

```
dictionary alicedata
    "name" : "alice"
    "age" : 30
    "score" : 95
end dictionary

dictionary bobdata
    "name" : "bob"
    "age" : 25
    "score" : 87
end dictionary

dictionary people
    "alice" : alicedata
    "bob" : bobdata
end dictionary
```

### Accessing a Value in a Dictionary of Dictionaries

Access is two steps. The first retrieves the inner dictionary into a named value. The second retrieves the target value from that dictionary.

```
get dictionary people key "alice" as .alicedata
get dictionary .alicedata key "score" as .result
show .result
// displays 95
```

The intermediate value `.alicedata` holds a dictionary reference. It behaves as a dictionary for all subsequent operations — `get`, `put`, `remove`, `count`, `is in`, `not in`, and `repeat through` all apply.

### Modifying a Value in a Nested Dictionary

```
get dictionary people key "alice" as .alicedata
put 100 in dictionary .alicedata key "score"
```

Because `.alicedata` is a reference to the actual `alicedata` dictionary, modifications through it affect the original. There is no copy — the reference and the original are the same data.

### Iterating Through a Dictionary of Dictionaries

```
repeat through dictionary people
    set .person to current value
    get dictionary .person key "name" as .name
    get dictionary .person key "score" as .score
    show .name, .score
end repeat
```

`current value` inside the loop holds a dictionary reference. Assign it to a named value first, then operate on it as a dictionary.

### List of Dictionaries

Inner dictionaries are declared at the file level. The list references them by name as its items. All items in the list must be dictionaries — the homogeneity rule applies.

```
dictionary alicedata
    "name" : "alice"
    "score" : 95
end dictionary

dictionary bobdata
    "name" : "bob"
    "score" : 87
end dictionary

list people
    alicedata
    bobdata
end list
```

A bare unquoted word inside a `list` block that matches the name of a declared dictionary is resolved as a dictionary reference. A bare unquoted word that does not match any declared dictionary name is fatal. Error log records the name and line number. This is the only position in the language where a bare unquoted word inside a block is resolved as a structure reference rather than a literal value.

### Accessing a Value in a List of Dictionaries

```
get list people 1 as .person
get dictionary .person key "name" as .name
show .name
// displays alice
```

The first step retrieves the dictionary at position 1. The second retrieves the target value from it.

### Iterating Through a List of Dictionaries

```
repeat through list people
    set .person to current item
    get dictionary .person key "name" as .name
    get dictionary .person key "score" as .score
    show .name, .score
end repeat
```

`current item` inside the loop holds a dictionary reference. Assign it to a named value first, then operate on it as a dictionary.

### Adding to a Nested Structure at Runtime

New inner dictionaries can be declared at the file level and added to an outer dictionary or list at runtime using `put` with the `dictionary` keyword:

```
dictionary charliedata
    "name" : "charlie"
    "score" : 72
end dictionary

put dictionary charliedata in list people
put dictionary charliedata in dictionary people key "charlie"
```

The `dictionary` keyword before the name identifies it as a dictionary reference, consistent with `get dictionary`, `count dictionary`, and `repeat through dictionary`. Without the `dictionary` keyword, a bare name in a `put` instruction would be ambiguous.

### Homogeneity Rules

A dictionary of dictionaries must have all values be dictionary references — mixing scalar values and dictionary references in the same dictionary is fatal. A list of dictionaries must have all items be dictionary references — mixing scalars and dictionary references in the same list is fatal. These follow the existing homogeneity rules exactly.

### Nested Structure Error Behaviors

**Type mismatch on put — scalar into a dictionary-type dictionary** — fatal. Error log records the value, its type, and the expected type.

**Type mismatch on put — scalar into a dictionary-type list** — fatal.

**`get` on an inner dictionary reference returning a non-dictionary value** — fatal. Error log records the key and the actual type returned.

**Referencing an undeclared dictionary by name in a declaration** — fatal. Error log records the name and line number.

**Bare unquoted word in a `list` block that does not match a declared dictionary name** — fatal. Error log records the name and line number.

**Modifying an inner dictionary through a reference modifies the original** — this is intended behavior, not an error. There are no copies.

VERN supports nesting up to four levels deep. Attempting to nest beyond four levels is fatal at load time.

The four levels are:
- **Level 1** — a plain dictionary or list containing scalar values
- **Level 2** — a dictionary or list whose items are Level 1 dictionaries
- **Level 3** — a dictionary or list whose items are Level 2 dictionaries
- **Level 4** — a dictionary or list whose items are Level 3 dictionaries

Every level is declared flat at the file level. The depth is determined by how many levels of dictionary references are chained, not by physical nesting in the source file.

Access is one `get` per level. Each step retrieves a dictionary reference which the next step operates on:

```
get dictionary students key "alice" as .alicedata
get dictionary .alicedata key "math" as .alicemath
get dictionary .alicemath key "term1" as .aliceterm1
get dictionary .aliceterm1 key "algebra" as .algebrascore
show .algebrascore
```

Values holding dictionary references behave as dictionaries for all subsequent operations — `get`, `put`, `remove`, `count`, `is in`, `not in`, and `repeat through` all apply.

**Error behavior:** Nesting beyond four levels — fatal at load time. Error log records the dictionary name and depth.


---

## v0.7 Limitations

The following behaviors are intentionally constrained or deferred.

**Unary minus not supported** — `-1` cannot be written directly. Use `set .neg to 0 - 1` or an intermediate variable.

**Parentheses not supported in expressions** — use intermediate variables to control evaluation order.

**Empty vs. Uninitialized Values** — an empty string (`""`) is a valid text value. An uninitialized value is always fatal to reference. `none` is an explicitly empty value distinct from both.

**Locale-specific number separators** — decimal is `.` and thousands is `,`. These are fixed. Locale-aware separators will be addressed through language bindings.

**`type of` on imported script references** — scripts imported from library files live in the interpreter's script registry, not file scope. `type of .scriptname.script` does not resolve correctly for imported scripts. Test functionality directly rather than checking script type.

**validate.vern `.targettype` parameter** — currently converts to number only. Date and time support deferred. Calling programs use the parameter now so no rewrite needed when support arrives.

**dictsearch.vern empty string ambiguity** — `.searchdict` returns empty string when key not found. Use `.haskey` check first when actual values may also be empty strings.

**Package System** — deferred until public release and usage patterns emerge.

---

## Reserved Words

The following words are reserved by the language and cannot be used as value names, script names, or list names:

`set`, `to`, `show`, `ask`, `read`, `write`, `append`, `from`, `if`, `then`, `repeat`, `times`, `end`, `stop`, `start`, `at`, `run`, `define`, `as`, `script`, `and`, `or`, `not`, `is`, `true`, `false`, `add`, `subtract`, `multiply`, `divide`, `convert`, `number`, `text`, `return`, `pass`, `loop`, `import`, `list`, `put`, `in`, `not in`, `remove`, `through`, `get`, `current`, `item`, `count`, `round`, `floor`, `ceiling`, `power`, `root`, `remainder`, `random`, `absolute`, `minimum`, `maximum`, `percent`, `of`, `length`, `find`, `extract`, `replace`, `with`, `beginning`, `finishing`, `attempt`, `fail`, `reason`, `date`, `time`, `difference`, `between`, `days`, `hours`, `minutes`, `format`, `using`, `while`, `otherwise`, `exist`, `delete`, `files`, `folder`, `parent`, `sine`, `cosine`, `tangent`, `arcsine`, `arccosine`, `arctangent`, `hyperbolic`, `arc`, `ln`, `log`, `base`, `pi`, `e`, `tau`, `infinity`, `degrees`, `radians`, `sum`, `factorial`, `combinations`, `permutations`, `sign`, `exit`, `next`, `by`, `split`, `join`, `trim`, `uppercase`, `lowercase`, `starts`, `ends`, `ascending`, `descending`, `sort`, `reverse`, `slice`, `combine`, `dictionary`, `key`, `value`, `takes`, `type`, `fetch`, `send`, `decimals`, `thousands`, `padded`, `path`, `none`, `invoke`, `update`, `headers`, `status`, `response`, `parse`, `inspect`, `json`, `csv`, `xml`, `ini`

**Contextual resolution notes:**

- `is`, `not`, `equal`, `to`, `greater`, `less`, `than`, `or` are reserved as standalone tokens but also appear as components of compound comparison operators. When adjacent in a recognized compound sequence, they are parsed as a single token.
- `from` is valid in exactly three positions: (1) after a value reference in `read .value from .file`, (2) after a value reference in `remove .value from list`, (3) after a key reference in `remove key .key from dictionary`. Any other position is fatal.
- `in` is valid in exactly these positions: (1) after a value reference in `put .value in list`, (2) after a text literal or value reference in `find "text" in .value`, (3) after the `files` keyword in `get files in`, (4) as part of the compound `is in` in membership checks, (5) after a value reference in `put .value in dictionary`, (6) after a dictionary reference in `put dictionary name in list`, (7) after a dictionary reference in `put dictionary name in dictionary`. Any other position is fatal.
- `and` is valid in exactly two positions: (1) as a boolean conjunction between two conditions in `if`, `while`, and compound condition expressions, (2) as a separator between two value references in `difference between .ref and .ref`. The parser distinguishes these by whether `and` is preceded by a complete condition expression (boolean conjunction) or by a value reference following `between` (separator). Any other position is fatal.
- `days`, `hours`, and `minutes` are reserved as unit keywords. User-defined values named `.days`, `.hours`, or `.minutes` are not affected — the period prefix makes user references unambiguous from bare reserved keywords.
- `exist` is used only as a condition in `if` statements. `exist` outside an `if` statement is a fatal error.
- `folder` and `parent` are descriptor keywords in the period chain. User-defined values use the period prefix and cannot conflict.
- `files` is used only in `get files in`. User-defined values use the period prefix and cannot conflict.
- `otherwise` is used only inside `if` block form. `otherwise` outside an `if` block is a fatal error.
- `to` is valid in two instruction-leading positions: (1) `to degrees .value as .result` and (2) `to radians .value as .result`. In all other positions `to` is a mid-instruction destination marker. The parser resolves by whether `to` is the first token on a line.
- `radians` is valid in exactly two positions: (1) as an optional modifier between a value reference and `as` in trig operations, (2) as the target word in `to radians`. Any other position is fatal.
- `degrees` is valid only as the target word in `to degrees`. Any other position is fatal. Trig operations default to degrees without requiring the word.
- `base` is valid only after a value reference in `log .value base n`. Any other position is fatal.
- `log` with no `base` modifier is base 10. `log` with a `base` modifier is arbitrary base. The parser resolves by whether `base` follows the value reference.
- `arctangent` with one value reference before `as` or `radians` is single-argument. `arctangent` with two value references is two-argument. The parser resolves by count of references.
- `hyperbolic` is valid only as the first word of `hyperbolic sine`, `hyperbolic cosine`, or `hyperbolic tangent`. Any other position is fatal.
- `arc` is valid only as the first word of `arc hyperbolic sine`, `arc hyperbolic cosine`, or `arc hyperbolic tangent`. Any other position is fatal.
- `e` is a reserved constant. User-defined values use the period prefix and cannot conflict.
- `pi`, `tau`, and `infinity` are reserved constants. User-defined values use the period prefix and cannot conflict.
- `as` is valid in exactly these positions: (1) after a value reference or expression in assignment operations, (2) after a list name and number in `get list name n as`, (3) after a text literal in `define "word" as`, (4) after a list operation keyword (`sort`, `reverse`, `slice`, `combine`, `split`) followed by a list reference — in this position `as list` assigns the result to the named list that follows, (5) after a `type of` expression in type checking operations. Any other position is fatal.
- `with` is valid in exactly three positions: (1) as the replacement marker in `replace "old" with "new"`, (2) as the parameter passing marker in `run .script with`, (3) as the list separator in `combine list first with list second`. The parser resolves by position — following `replace` it is a replacement marker; following a `run` script reference it is a parameter marker; following a list reference after `combine list` it is a list separator.
- `exit` is valid only immediately preceding `loop`. `exit` alone is fatal.
- `next` is valid only immediately preceding `item`. `next` alone is fatal.
- `current` is valid as the first word of `current item`, `current key`, or `current value`. The compound is resolved by what follows `current`. Any other position is fatal.
- `key` is valid only in dictionary operations — after a dictionary reference in `put`, `get`, and `remove` instructions. Any other position is fatal.
- `value` is valid only as the second word of `current value` inside a `repeat through dictionary` block. Any other position is fatal.
- `takes` is valid only in script definitions, immediately following the script reference. Any other position is fatal.
- `starts` is valid only as the first word of the compound `starts with` in `if` statements. Any other position is fatal.
- `ends` is valid only as the first word of the compound `ends with` in `if` statements. Any other position is fatal.
- `by` is valid in exactly two positions: (1) as the delimiter marker in `split .text by "delimiter"`, (2) as the separator marker in `join list names by "separator"`. Any other position is fatal.
- `descending` is valid only as a modifier immediately following a list name in a `sort` instruction. Any other position is fatal.
- `dictionary` follows the same positional patterns as `list` — as a block opener, in `put`, `get`, `remove`, `count`, `repeat through`, and membership checks. Resolved identically to `list` by surrounding tokens.
- `type` is valid only as the first word of `type of`. Any other position is fatal.
- `of` is valid in exactly two positions: (1) after `percent .value` as the connector to the total in `percent .value of .total`, (2) after `type` as the connector to the subject value reference in `type of .value`. Any other position is fatal.
- `text` is valid as a type keyword in its existing positions (`convert .value to text`, type references), and as the opening of a `text .valuename` block declaration when it is the first token on a line followed by a value reference. The parser resolves by position — `text` opening a line followed by `.valuename` is a block declaration; `text` in any other position is the existing type keyword.
- `end` is valid as the opening of these compounds: `end script`, `end list`, `end dictionary`, `end repeat`, `end while`, `end if`, `end attempt`, `end fail`, `end text`. Any other word following `end` is fatal.
- `format` is extended to handle number values in addition to dates and times. Date/time formatting is followed by `using`. Number formatting is followed by one or more of `decimals`, `thousands`, or `padded`. The parser resolves by what follows the result reference.
- `fetch` is valid only as the opening keyword of a fetch instruction. Any other position is fatal.
- `send` is valid only as the opening keyword of a send instruction. Any other position is fatal.
- `decimals`, `thousands`, `padded` are valid only as modifiers following the result reference in a number `format` instruction. Any other position is fatal.
- `put` is valid in four forms: (1) `put .value in list name` — adds a scalar value to a list, (2) `put .value in dictionary name key "key"` — adds a scalar value to a dictionary, (3) `put dictionary name in list name` — adds a dictionary reference to a list, (4) `put dictionary name in dictionary name key "key"` — adds a dictionary reference to a dictionary. The parser resolves by whether a `.` prefixed value reference or the `dictionary` keyword follows `put`.
- `fail` is extended: now valid in five positions: (1) as the second word of `if fail`, (2) as the second word of `end fail`, (3) as the first word of `fail reason`, (4) as the first word of `fail type`, (5) as the second word of a typed handler `if fail "category"`. Any other position is fatal.
- `path` is valid in exactly four positions: (1) immediately after `to` in write/append, (2) immediately after `from` in read, (3) as first token after `delete` when file context (chain contains `.vern`), (4) as first token after `if` in an exist check. Any other position is fatal.
- `none` is valid as a value in `set`, as a comparison target in `if` conditions, as a `return` value, and as a list or dictionary item. Any other position is fatal.
- `invoke` is valid only as the opening keyword of an invoke instruction inside a script. Must be followed by `script` and a declared script parameter name. Any other position is fatal.
- `update` is valid only as the opening keyword of an update instruction. Any other position is fatal.
- `headers` is valid only as the second word of `with headers dictionary`. Any other position is fatal.
- `status` is valid only after `as .result` and `response headers` where applicable, or after the URL on operations with no response body. Any other position is fatal.
- `response` is valid only as the first word of `response headers`. Any other position is fatal.
- `parse` is valid only as the opening keyword of a parse instruction. Must be followed by a format identifier, a value reference, `as`, a type keyword (`list` or `dictionary`), and a result name. Any other position is fatal.
- `inspect` is valid only as the opening keyword of an inspect instruction. Must be followed by a format identifier and a value reference. Any other position is fatal.
- `json`, `csv`, `xml`, `ini` are valid only immediately after `parse` or `inspect`. Any other position is fatal.
- `script` has three new positional contexts: (1) following `with` or comma in a `run` call — script parameter passing, (2) following `takes` or comma in a `takes` declaration — script parameter declaration, (3) following `invoke` — script parameter execution.
- `list` has two new positional contexts: (1) in `takes` declarations immediately before a parameter name, (2) in `with` clauses on `run` calls as a parameter passing marker.
- `dictionary` has two new positional contexts matching `list` above.
- `delete` contextual resolution extended: `delete` followed by a chain containing `.vern` is file deletion; `delete` followed by a single period-prefixed value name with no `.vern` is HTTP DELETE.
- `as` extended: valid in two additional positions: (1) in `run` calls after parameters as an inline return destination, (2) as `as list` or `as dictionary` in `parse` instructions to declare the result type and name.
- `with` extended: valid in one additional position: after the URL in `fetch`, `send`, `update`, or `delete` networking instructions as `with headers dictionary`.
- `return` extended: bare `return .valuename` with no `pass to` is now valid for Form 2 inline return assignment. Multiple `return` statements are valid in a script when the calling side uses a comma-separated `as` list.

### Reserved Symbols

| Symbol | Use |
|---|---|
| `.` | Period — denotes containment in the file, script, folder, and value hierarchy. Exclusive to this hierarchy. |
| `#` | Hash — denotes a container tag. Not part of the period chain. |

No other special characters are used by the language.

### Script Self-Reference

`.scriptname.script` used from within `.scriptname` resolves to the script's own identity, not its contents. Self-reference has no practical use in v0.6 and is reserved for future introspection features.

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
// Safe number input with recovery — retries until valid

set .value to 0
set .succeeded to false

script .main
    while .succeeded = false
        attempt
            ask .input
            convert .input to number as .value
            set .succeeded to true
        if fail
            show "invalid input, please enter a number"
        end fail
        end attempt
    end while
    run .calculate.script
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

### Validated Date Input

```
// Accept a date from the user, validate it, display it formatted

set .valid to false

script .main
    while .valid = false
        ask .inputdate
        attempt
            convert .inputdate to date as .cleandate
            set .valid to true
        if fail
            show "invalid format, please use YYYY-MM-DD"
        end fail
        end attempt
    end while
    format .cleandate as .displaydate using "DD/MO/YYYY"
    show "date entered: " + .displaydate
end script

start at .main.script
stop
```

### File Existence Check

```
// Read a file if it exists, create it if it does not

script .main
    if .records.vern exist
        read .name, .score from .records.vern
        show .name, .score
    otherwise
        show "no records found, creating file"
        ask .name
        ask .scoreinput
        convert .scoreinput to number as .score
        write .name, .score to .records.vern
    end if
end script

start at .main.script
stop
```
