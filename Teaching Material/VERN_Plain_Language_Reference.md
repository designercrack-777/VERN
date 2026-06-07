# VERN Plain-Language Reference

## Overview

This document covers every instruction in VERN v0.6 in plain language — what each instruction does, what it looks like, and a working example. It is organized by category. You do not need to read it start to finish. Find the section for what you are trying to do and read that.

If you are new to VERN and have not read the concept overview, start there first. This document assumes you understand what a value, a script, and a reference are.

---

## How to Read This Document

Each instruction is shown in two forms: the pattern, which shows the shape of the instruction with placeholders, and an example, which shows what actual code looks like. Placeholders in the pattern look like `name` or `value` — they represent something you supply. Actual keywords — words VERN recognizes — appear as-is.

---

## The Basics

### Setting a Value

```
set .name to data
```

Stores a piece of data under a name. The data can be text in quotes, a number, true or false, a date, or a time.

```
set .greeting to "hello"
set .score to 0
set .active to true
set .birthday to 1990-03-15
set .alarm to 07:30:00
```

A period before a name means: this is something the program can refer to. The name is yours to choose — use something that makes sense to read.

---

### Showing Something on Screen

```
show .name
show .name, .othername
show "some text"
show "label: ", .value
```

Displays a value, a piece of text, or several things at once. When showing multiple things, separate them with commas — they display in order on the same line.

```
set .name to "Gabriel"
show "hello, ", .name
// displays: hello, Gabriel
```

---

### Asking for Input

```
ask .name
```

Pauses the program and waits for the user to type something. Whatever they type is stored in the named value as text. If you need a number, convert it after asking.

```
ask .userinput
convert .userinput to number as .age
```

---

### Comments

```
// this is a comment
set .name to "Gabriel"  // this part is also ignored
```

Anything after `//` on a line is ignored. Use comments to explain what your code is doing.

---

### Ending a Program

```
stop
```

Stops the program. VERN adds `stop` automatically at the end of every file, but you can also place it anywhere to end early.

---

## Values and Types

A value holds one piece of data. Its type — text, number, true/false, date, time — is determined by what you put in it.

| Type | Example | What it's for |
|---|---|---|
| Text | `"hello"` | words, sentences, anything in quotes |
| Number | `42` or `3.14` | math and counting |
| True/False | `true` or `false` | yes/no decisions |
| Date | `2026-06-06` | calendar dates — always YYYY-MM-DD |
| Time | `14:30:00` | time of day — always HH:MI:SS, 24-hour |

### Converting Between Types

VERN never converts types automatically. If you have a number stored as text — which happens when a user types something — you have to convert it explicitly. The result always goes to a new value. The original is unchanged.

```
convert .valuename to number as .newname
convert .valuename to text as .newname
convert .valuename to date as .newname
convert .valuename to time as .newname
```

```
ask .input
convert .input to number as .amount
set .doubled to .amount * 2
show .doubled
```

### Checking a Value's Type

```
type of .valuename as .result
```

Returns the type of whatever is in `.valuename` as a text value: `"text"`, `"number"`, `"true/false"`, `"date"`, or `"time"`.

```
type of .input as .kind
if .kind = "number" then show "it is a number"
```

---

## Math

### Basic Math

Both word forms and symbols work. Use whichever reads better to you.

```
set .result to .a + .b        // addition
set .result to .a - .b        // subtraction
set .result to .a * .b        // multiplication
set .result to .a / .b        // division
set .result to .a power 2     // exponent
set .result to .a root 2      // root
set .result to .a remainder .b // remainder after division
```

The `+` operator also joins two pieces of text end to end:

```
set .full to "hello " + "world"
// .full is "hello world"
```

It does not join a number and text — that requires converting the number to text first.

### Rounding

```
round .number as .result
round .number to 2 as .result     // round to 2 decimal places
floor .number as .result           // always round down
ceiling .number as .result         // always round up
```

### Other Math Operations

```
absolute .number as .result        // removes negative sign
random .min to .max as .result     // random whole number in range
percent .value of .total as .result
minimum .a .b as .result           // smaller of two numbers
maximum .a .b as .result           // larger of two numbers
minimum list numbers as .result    // smallest in a numeric list
maximum list numbers as .result    // largest in a numeric list
sum list numbers as .result        // total of all items in a numeric list
factorial .number as .result
combinations .n .k as .result
permutations .n .k as .result
sign .number as .result            // returns -1, 0, or 1
```

### Math Constants

These are built in and ready to use anywhere a number is valid:

| Constant | Value |
|---|---|
| `pi` | 3.14159... |
| `e` | 2.71828... |
| `tau` | 6.28318... (2π) |
| `infinity` | positive infinity |

```
set .area to pi * .radius power 2
```

### Trigonometry

All trig operations use degrees by default. Add `radians` to use radians instead.

```
sine .angle as .result
cosine .angle as .result
tangent .angle as .result
arcsine .value as .result
arccosine .value as .result
arctangent .value as .result
arctangent .y .x as .result        // two-argument form
```

```
sine .angle radians as .result     // radians mode
```

Hyperbolic trig:

```
hyperbolic sine .value as .result
hyperbolic cosine .value as .result
hyperbolic tangent .value as .result
arc hyperbolic sine .value as .result
arc hyperbolic cosine .value as .result
arc hyperbolic tangent .value as .result
```

### Angle Conversion

```
to degrees .value as .result
to radians .value as .result
```

### Logarithms

```
ln .value as .result               // natural log
log .value as .result              // base 10
log .value base 2 as .result       // any base
```

---

## Comparison and Logic

Comparisons are used in `if` and `while` statements to check conditions.

### Comparison Operators

Both word and symbol forms work:

| Word form | Symbol | Meaning |
|---|---|---|
| `is equal to` | `=` | equal |
| `is not` | `!=` | not equal |
| `is greater than` | `>` | greater than |
| `is less than` | `<` | less than |
| `is greater than or equal to` | `>=` | greater or equal |
| `is less than or equal to` | `<=` | less or equal |

```
if .score is greater than 90 then show "excellent"
if .name = "Gabriel" then show "welcome"
```

### Combining Conditions

```
if condition and condition then action
if condition or condition then action
if not .active then show "inactive"
```

Conditions are evaluated left to right. With `and`, the second condition is only checked if the first is true. With `or`, the second is only checked if the first is false.

---

## Decisions — if, otherwise

### Single Action

```
if condition then action
```

```
if .score >= 60 then show "passing"
```

### Multiple Actions

```
if condition
    instructions
end if
```

```
if .score is greater than 90
    show "excellent"
    set .grade to "A"
end if
```

### Two Branches

```
if condition
    instructions
otherwise
    instructions
end if
```

```
if .score is greater than 90
    show "excellent"
otherwise
    show "keep trying"
end if
```

### Nesting

`if` blocks can contain other `if` blocks:

```
if .score is greater than 50
    show "passing"
    if .score is greater than 90
        show "with distinction"
    end if
end if
```

---

## Repetition

### Repeat a Set Number of Times

```
repeat n times
    instructions
end repeat
```

The keyword `loop` holds the current count, starting at 1. It is read-only.

```
repeat 5 times
    show loop
end repeat
// displays 1, 2, 3, 4, 5
```

If you need to combine `loop` with text, convert it first:

```
repeat 5 times
    convert loop to text as .looptext
    show "round " + .looptext
end repeat
```

### Repeat While a Condition is True

```
while condition
    instructions
end while
```

```
set .count to 0
while .count is less than 5
    set .count to .count + 1
    show .count
end while
```

The loop stops as soon as the condition becomes false. If it is false on the first check, the loop never runs. A condition that never becomes false loops forever — that is intentional behavior for programs that need it.

### Loop Control

`exit loop` — stops the loop immediately and continues after it:

```
repeat 10 times
    if loop = 5 then exit loop
    show loop
end repeat
// displays 1, 2, 3, 4
```

`next item` — skips the rest of the current pass and goes to the next one:

```
repeat 5 times
    if loop = 3 then next item
    show loop
end repeat
// displays 1, 2, 4, 5
```

---

## Scripts

A script is a named, reusable block of instructions. Define it once, run it as many times as needed from anywhere in the file.

### Defining a Script

```
script .name
    instructions
end script
```

### Running a Script

```
run .name.script
```

### Entry Point

```
start at .name.script
stop
```

Tells VERN which script to start from. Without this, execution starts at the first line of the file and reads down.

### Scripts with Input

A script can accept values when it is called:

```
script .greet takes .name
    show "hello, ", .name
end script

run .greet.script with "Gabriel"
```

Multiple inputs, separated by commas:

```
script .add takes .first, .second
    set .total to .first + .second
    return .total pass to .answer
end script

set .answer to 0
run .add.script with 10, 20
show .answer
// displays 30
```

### Scripts Returning a Value

```
return .valuename pass to .destination
```

The destination must be a file-level value declared before the script runs.

---

## Lists

A list is an ordered sequence of values, all of the same type. Lists live at the file level.

### Declaring a List

```
list name
    "item one"
    "item two"
    "item three"
end list
```

An empty list:

```
list name
end list
```

### Adding to a List

```
put .value in list name
```

Always adds to the end.

### Removing from a List

```
remove .value from list name
```

Removes the first matching item. If not found, logs a note and continues.

### Getting an Item by Position

Positions start at 1.

```
get list name 3 as .result
```

### Going Through a List

```
repeat through list name
    show current item
end repeat
```

`current item` holds the value for each pass. It is read-only.

### Checking if Something is in a List

```
if .value is in list name then show "found"
if .value not in list name then show "not found"
```

### Counting Items

```
count list name as .total
```

### List Operations

```
sort list name as list sortedname
sort list name descending as list sortedname
reverse list name as list reversedname
slice list name 2 to 4 as list subset
combine list first with list second as list merged
```

All of these produce a new list. The original is never changed. The target list must be declared before the operation runs.

---

## Dictionaries

A dictionary stores key-value pairs. Keys are text. All values must be the same type. Dictionaries live at the file level.

### Declaring a Dictionary

```
dictionary name
    "key" : value
    "key" : value
end dictionary
```

```
dictionary scores
    "alice" : 95
    "bob" : 87
end dictionary
```

### Adding or Updating a Key

```
put .value in dictionary name key "keyname"
```

If the key already exists, its value is replaced.

### Getting a Value by Key

```
get dictionary name key "keyname" as .result
```

### Removing a Key

```
remove key "keyname" from dictionary name
```

### Checking if a Key Exists

```
if "keyname" is in dictionary name then show "found"
if "keyname" not in dictionary name then show "not found"
```

### Counting Pairs

```
count dictionary name as .total
```

### Going Through a Dictionary

```
repeat through dictionary name
    show current key
    show current value
end repeat
```

`current key` and `current value` are read-only. Iteration follows insertion order.

---

## Nested Data

VERN supports two kinds of nested structures: a dictionary whose values are other dictionaries, and a list whose items are dictionaries. Both are built from flat declarations — nothing is physically nested in the file.

### Dictionary of Dictionaries

```
dictionary alicedata
    "name" : "alice"
    "score" : 95
end dictionary

dictionary people
    "alice" : alicedata
end dictionary
```

Getting a value from the inner dictionary:

```
get dictionary people key "alice" as .record
get dictionary .record key "name" as .name
show .name
```

### List of Dictionaries

```
dictionary player1
    "name" : "alice"
    "score" : 95
end dictionary

list players
    player1
end list
```

Getting a value from a dictionary inside the list:

```
get list players 1 as .record
get dictionary .record key "score" as .score
show .score
```

---

## Text Operations

All text operations produce a new value. The original is never changed.

### Length

```
length of .text as .result
```

### Searching

```
if "word" is in .text then show "found"
if "word" not in .text then show "not found"
find "word" in .text as .position    // returns position, or 0 if not found
```

### Extracting a Portion

Positions start at 1. Both the start and end positions are included.

```
extract from .text beginning 1 finishing 5 as .result
```

### Replacing

```
replace "old" with "new" in .text as .result
```

Replaces the first occurrence. If not found, the original text is assigned to the result unchanged.

### Splitting and Joining

```
split .text by "," as list parts
join list parts by ", " as .result
```

`split` breaks text into a list at every occurrence of the delimiter. `join` puts a list back together into a single text value.

### Trimming Whitespace

```
trim .text as .result
```

Removes spaces, tabs, and newlines from the beginning and end.

### Case

```
uppercase .text as .result
lowercase .text as .result
```

### Starts With and Ends With

```
if .text starts with "hello" then show "found"
if .text ends with ".vern" then show "it is a vern file"
```

### Multi-Line Text

A text block lets you write text that spans multiple lines directly in the file. Reserved words inside are treated as literal text, not instructions.

```
text .message
    line one
    line two
    line three
end text

show .message
```

Text blocks are file-level only — they cannot be inside a script.

---

## Formatting for Display

### Formatting Numbers

```
format .number as .result decimals 2
format .number as .result thousands
format .number as .result decimals 2 thousands
format .number as .result padded 8
format .number as .result decimals 2 thousands padded 10
```

The result is always a text value. The original number is unchanged.

- `decimals n` — round to n decimal places and show exactly n digits after the point
- `thousands` — add comma separators every three digits
- `padded n` — pad with spaces on the left to reach a total width of n characters

### Formatting Dates and Times

```
format .today as .displaydate using .dateformat
format .now as .displaytime using .timeformat
```

Date format codes: `YYYY` (year), `MO` (month), `DD` (day)  
Time format codes: `HH` (hour), `MI` (minute), `SS` (second)

```
set .dateformat to "DD/MO/YYYY"
format .today as .display using .dateformat
show .display
// displays: 06/06/2026
```

---

## Dates and Times

### Getting the Current Date and Time

```
get date as .today
get time as .now
```

### Difference Between Two Dates or Times

```
difference between .date1 and .date2 in days as .result
difference between .time1 and .time2 in hours as .result
difference between .time1 and .time2 in minutes as .result
```

The result is always a positive number regardless of which value is earlier.

### Comparing Dates and Times

All comparison operators work on dates and times. An earlier date is less than a later one.

```
if .deadline is less than .today then show "overdue"
```

---

## File Operations

### Checking if a File Exists

```
if .filename.vern exist then run .process.script
```

### Reading from a File

Values are read in order, one per line.

```
read .name from .data.vern
read .name, .score from .data.vern
```

### Writing to a File

Replaces the entire file. Creates the file if it does not exist.

```
write .name to .data.vern
write .name, .score to .data.vern
```

### Appending to a File

Adds to the end without replacing what is already there.

```
append .name to .data.vern
```

### Deleting a File

```
delete .filename.vern
```

### File Paths

Files in the same folder as the program:

```
.filename.vern
```

Files in a subfolder:

```
.filename.vern.subfolder.folder
```

Files at an absolute path from system root:

```
.filename.vern.subfolder.folder.documents.folder.parent
```

Every folder name must be followed by `.folder`. `.parent` means system root — use it once at the end of the chain.

---

## Networking

### Fetching Data from a URL

```
fetch .url as .result
```

Sends an HTTP GET request. The response body is stored as text. Parsing the response is the program's responsibility.

```
set .url to "https://api.example.com/data"
fetch .url as .response
show .response
```

### Sending Data to a URL

```
send .data to .url
```

Sends an HTTP POST request. Both values must be text. No response is captured.

### Network Errors

Network failures are fatal by default but recoverable inside an `attempt` block:

```
attempt
    fetch .url as .response
    show .response
if fail
    show fail reason
end fail
end attempt
```

---

## Error Recovery

The `attempt` block lets you handle failures without stopping the program.

### Basic Form

```
attempt
    instructions
if fail
    instructions
end fail
end attempt
```

If an instruction inside the block fails, execution jumps immediately to `if fail`. After the fail handler runs, execution continues after `end attempt`.

```
attempt
    convert .input to number as .value
if fail
    show "that is not a number"
end fail
end attempt
```

### Try All Form

```
attempt all
    instructions
if fail
    instructions
end fail
end attempt
```

Runs every instruction regardless of failures. After all instructions have been attempted, the fail handler runs once for each failure.

### fail reason

Inside the `if fail` block, `fail reason` holds a text description of what went wrong.

```
if fail
    show fail reason
end fail
```

### Checking if an Attempt Succeeded

```
set .succeeded to false

attempt
    convert .input to number as .value
    set .succeeded to true
if fail
    show fail reason
end fail
end attempt

if .succeeded = true then run .process.script
```

---

## Containers

Containers hold different states of values — they are used to swap out data depending on context. The most common use is localization: the same script can display different language text by switching which container is active.

### Defining a Container

```
#containername
    set .greeting to "hello"
```

### Using a Container on a Script Run

```
run .greet.script #english
run .greet.script #spanish
```

### Container Files

A file can contain nothing but containers. Import it and reference any container from it:

```
import .strings.vern
run .greet.script #english
```

---

## Importing Files

```
import .filename.vern
```

Loads an external file and makes its values, lists, dictionaries, and scripts available. One import per line.

```
import .utilities.vern
import .languages.vern
```

Imports are recommended at the top of the file. If two imported files contain something with the same name, the first imported file wins.

---

## Defining Custom Words

```
define "word" as run .scriptname.script
```

Adds a new word to the language that calls a script. Useful for building your own vocabulary on top of VERN.

```
define "calculate" as run .math.script
```

After this, anywhere in the file you can write `calculate` and it will run `.math.script`.

---

## The Reference System

Every name that refers to something in VERN gets a period in front of it. The period means: this belongs to something, or something belongs to it.

### What Periods Mean

`.name` — a value  
`.name.script` — a script  
`.name.scriptname.script` — a value inside a script  
`.filename.vern` — a file  
`#container` — a container (uses `#` instead of `.`)

### Minimum Context Rule

You only need to write as much of the chain as the system needs to find what you mean without confusion. If `.score` only exists in one place, `.score` is enough. If it exists in multiple scripts, extend the chain: `.score.quiz.script`.

### Scope

Values declared inside a script are local to that script. Values declared outside any script — at the top of the file — are accessible from any script in that file.

The same name can be used in different scripts without conflict. They are separate values that happen to share a name.

---

## Reserved Symbols

Only two symbols carry meaning in VERN:

- `.` — containment hierarchy. Every named element — values, scripts, files, folders — uses this.
- `#` — container tag. Containers only.

No other special characters are required to write VERN programs. Operators (`+`, `-`, `*`, `/`, `=`, etc.) are used in expressions but are not reserved syntax characters.

---

*The VERN Project — 2026*
