# VERN Plain-Language Reference

## Overview

This document covers every instruction in VERN in plain language — what each instruction does, what it looks like, and a working example. It is organized by category. You do not need to read it start to finish. Find the section for what you are trying to do and read that.

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

---

## The None Value

Sometimes a value intentionally holds nothing. VERN has a special value for this — `none`. It is not an error. It is not an empty string. It is a deliberate declaration that a value has no data yet.

```
set .result to none
```

You can check for it the same way you check anything else:

```
if .result = none then show "nothing found"
if .result != none then show .result
```

If you need to use a `none` value as a number or text, assign it a real value first:

```
if .result = none then set .result to 0
set .total to .result + 10
```

Using a `none` value directly in an operation without checking first is a fatal error.

---

## Dynamic File References

Normally when you read or write a file, you write the file name directly in the instruction. Dynamic file references let you build the file name from a value at runtime — useful when the file name depends on something the program figures out while running, like today's date or something the user typed.

Use `path` before the value that holds the file name:

```
set .filename to "mylog.vern"
write .entry to path .filename
```

```
read .data from path .filename
```

```
if path .filename exist then run .process.script
```

```
delete path .filename
```

The value must contain a complete, valid file reference string — including `.vern` and any folder information needed to locate the file.

Building a filename from the current date:

```
get date as .today
format .today as .datetext using "YYYY-MM-DD"
set .filename to .datetext + ".vern.logs.folder"
write .entry to path .filename
```

---

## Typed Error Handling

The `attempt` block already lets you catch errors. This extends it so you can respond differently to different kinds of errors.

Inside any `if fail` block, `fail type` tells you what category of error occurred:

- `"type"` — a type conversion or type conflict
- `"file"` — a file not found or directory missing
- `"network"` — a connection failure or timeout
- `"value"` — an undefined value or invalid math

```
attempt
    fetch .url as .response
if fail
    show fail type
    show fail reason
end fail
end attempt
```

You can also set up typed handlers that run automatically for specific error types. The right handler runs without you having to check manually:

```
attempt
    fetch .url as .response
if fail "network"
    show "connection failed, trying again"
if fail "type"
    show "wrong data type"
if fail
    show "unexpected error:", fail reason
end fail
end attempt
```

Typed handlers must appear before the bare `if fail` catch-all. The catch-all runs for any error that doesn't match a typed handler. If there's no catch-all and the error doesn't match any typed handler, the error is unhandled.

---

## Expanded Networking

### Sending Data with Headers

Some web services require you to identify yourself with a key or token. You do this by sending headers alongside your request. Declare your headers as a dictionary, then attach them to any request using `with headers dictionary`:

```
dictionary authheaders
    "Authorization" : "Bearer myapikey"
    "Content-Type" : "application/json"
end dictionary

fetch .url with headers dictionary authheaders as .response
```

Headers work with all four request types — `fetch`, `send`, `update`, and `delete`.

### Checking Status Codes

Every response from a web server includes a status code — a number that tells you whether the request worked. Use `status` to capture it:

```
fetch .url as .response status .code
show .code
```

Common codes: `200` means success. `404` means not found. `500` means the server had a problem. A code other than 200 is not automatically an error — the program decides what to do with it.

### Reading Response Headers

If you need to see the headers the server sent back:

```
fetch .url as .response response headers .responseheaders status .code
get dictionary .responseheaders key "Content-Type" as .contenttype
show .contenttype
```

### Updating and Deleting

`update` sends data to a URL to update something that already exists (HTTP PUT):

```
update .data to .url
update .data to .url status .code
```

`delete` with a URL value removes a resource (HTTP DELETE). This is different from file deletion — a URL value has no `.vern` in it:

```
delete .url
delete .url status .code
```

---

## Parsing Structured Data

When your program fetches data from the internet or reads a data file, it often comes back as structured text — JSON, CSV, XML, or INI format. `parse` converts that text into VERN dictionaries and lists you can actually work with.

### parse

```
parse json .response as dictionary data
parse csv .content as list rows
parse xml .response as dictionary data
parse ini .content as dictionary config
```

Everything comes in as text type — if you need a number, convert it explicitly after parsing.

**JSON example:**

```
fetch .url as .response
parse json .response as dictionary data
get dictionary data key "name" as .username
show .username
```

**CSV example:**

```
read .content from .datafile.vern
parse csv .content as list rows
repeat through list rows
    set .row to current item
    get dictionary .row key "name" as .name
    show .name
end repeat
```

**INI example:**

```
read .content from .config.vern
parse ini .content as dictionary config
get dictionary config key "database" as .dbsection
get dictionary .dbsection key "host" as .host
show .host
```

CSV always produces a list. XML and INI always produce a dictionary. JSON produces either — you declare which one you expect, and `inspect` helps you figure that out.

### inspect

`inspect` is a development tool. Use it when you're working with data you haven't seen before and you want to understand its structure before writing code that uses it. It prints the shape of the data to the terminal.

```
fetch .url as .response
inspect json .response
```

Output:
```
dictionary — 3 keys
  "city" — text
  "temperature" — text
  "condition" — text
```

Once you know the structure, write your `parse` call. Remove `inspect` before you ship your program.

---

## Script Return Values

### Returning a Single Value

Scripts can hand a result back to the program that called them. Use `return` inside the script and `as` on the calling line:

```
script .double takes .n
    set .result to .n * 2
    return .result
end script

run .double.script with 10 as .answer
show .answer
// displays 20
```

### Returning Multiple Values

A script can hand back more than one result. List the destination names after `as`, separated by commas. The first `return` goes to the first name, second to second, and so on:

```
script .splitname takes .fullname
    find " " in .fullname as .spacepos
    set .firstend to .spacepos - 1
    set .laststart to .spacepos + 1
    length of .fullname as .namelen
    extract from .fullname beginning 1 finishing .firstend as .firstname
    extract from .fullname beginning .laststart finishing .namelen as .lastname
    return .firstname
    return .lastname
end script

run .splitname.script with "Gabriel Moreau" as .first, .last
show .first
// displays: Gabriel
show .last
// displays: Moreau
```

---

## Passing Lists and Dictionaries to Scripts

Scripts can accept lists and dictionaries as parameters, not just values. Use the type keyword in both the declaration and the call:

```
script .showlist takes list items
    repeat through list items
        show current item
    end repeat
end script

run .showlist.script with list names
```

```
script .showentry takes dictionary record, .key
    get dictionary record key .key as .value
    show .value
end script

run .showentry.script with dictionary scores, "alice"
```

List and dictionary parameter names have no period prefix — consistent with how lists and dictionaries are always referenced throughout the language.

---

## First-Class Functions

A script can accept another script as a parameter and run it. This lets you write one general-purpose script that works with any operation you pass to it.

Declare a script parameter with `script parametername` in `takes`. Pass a script reference with `script .scriptname.script` in `with`. Run it inside the receiving script with `invoke script parametername`.

```
script .double takes .n
    set .result to .n * 2
    return .result
end script

script .applytolist takes list numbers, script operation
    repeat through list numbers
        set .current to current item
        invoke script operation with .current as .result
        show .result
    end repeat
end script

list numbers
    4
    8
    12
end list

run .applytolist.script with list numbers, script .double.script
// displays: 8, 16, 24
```

The scripts being passed in are always declared at the file level — nothing changes about how they're written. `invoke` just runs whatever script was passed in instead of a hardcoded name.

---

## Execution Modes

By default a VERN program runs once and stops. Execution modes change that ending behavior — a program can loop immediately, pause and wait for input, and choose whether to carry its state forward or start fresh each time.

The execution mode is declared at the very end of the file, after all scripts and the `start at` line.

### Run Once and Stop

```
start at .main.script
stop
```

The default. Runs once and exits. No change from the basic behavior you already know.

### Cycle — Loop Immediately

```
start at .main.script
cycle reset
```

```
start at .main.script
cycle keep
```

`cycle` completes the program and immediately runs it again without waiting for anything. Useful for programs that monitor, poll, or process a continuous stream of work.

`cycle reset` reinitializes all file-level values at the start of each new cycle — each run starts fresh.
`cycle keep` carries file-level values forward — each run picks up where the last one left off.

### Wait — Pause for Input Between Cycles

```
start at .main.script
wait reset
```

```
start at .main.script
wait keep
```

`wait` completes the program, pauses, and waits for new input before running again. `reset` and `keep` work the same way as with `cycle`.

### Stop Conditions

Any number of stop conditions can appear between `start at` and the execution mode declaration. They are checked after each cycle — the first one that is true exits the program.

```
start at .main.script
if .done = true then stop
if .errorstate = true then stop
cycle keep
```

The flag gets set inside a script. The exit condition lives at the bottom of the file where it is easy to find.

---

## Concurrent Programs

### Launching Another Program

```
launch .programname.vern
```

Starts another VERN program running at the same time as the current one. The current script continues immediately — it does not wait for the launched program to finish. The launched program runs according to its own execution mode.

```
script .main
    launch .worker.vern
    run .dowork.script
    stop .worker.vern
end script
```

The launched program must be in the same folder. Launching a program that is already running is a fatal error. A program cannot launch itself.

### Stopping Another Program

```
stop .programname.vern
```

Sends a halt signal to another named running program. That program stops immediately regardless of its execution mode. Valid only inside a script — this is the only form of `stop` that is valid inside a script.

If the named program is not currently running, this is a fatal error.

### Timed Pauses

```
wait 2 seconds
wait 500 milliseconds
```

Pauses the current script for the specified duration before continuing to the next instruction. The number must be a whole number greater than zero.

```
script .monitor
    repeat through list tasks
        run .process.script
        wait 250 milliseconds
    end repeat
end script
```

---

## Standard Library

VERN ships with a small set of ready-made utility scripts in a `lib` folder. Import any of them to use them in your program.

### validate.vern — Safe Input

Asks the user for input and keeps asking until they give a valid number:

```
import .validate.vern.lib.folder

run .validate.script with "enter your age:", "number" as .age
show "your age is", .age
```

### strings.vern — Padding and Alignment

Pads a value to a fixed width for clean column display. `"left"` puts text on the left, spaces on the right. `"right"` puts text on the right, spaces on the left:

```
import .strings.vern.lib.folder

run .pad.script with .name, 15, "left" as .paddedname
run .pad.script with .score, 6, "right" as .paddedscore
show .paddedname, .paddedscore
```

### datemath.vern — Date Calculations

```
import .datemath.vern.lib.folder

// days between a date and today
run .daysfrom.script with .deadline as .remaining
show "days remaining:", .remaining

// is a date in the past?
run .ispast.script with .deadline as .overdue
if .overdue = true then show "deadline has passed"

// days between two dates
run .daysbetween.script with .start, .finish as .total
show "total days:", .total
```

### listsearch.vern — List Search

```
import .listsearch.vern.lib.folder

// find position of a value — returns 0 if not found
run .finditem.script with list names, "bob" as .position

// check if a value exists in a list
run .hasitem.script with list names, "diana" as .found
if .found = true then show "diana is in the list"
```

### dictsearch.vern — Deep Dictionary Search

Searches through nested dictionaries up to four levels deep without having to chain every `get` manually. `.haskey` performs an independent key search and returns true or false regardless of the value type stored in the dictionary. `.searchdict` retrieves the value for a given key, returning an empty string if the key is not found.

```
import .dictsearch.vern.lib.folder

// check if a key exists anywhere in the structure
run .haskey.script with dictionary students, "algebra" as .found

// retrieve a value by key from any depth
if .found = true
    run .searchdict.script with dictionary students, "algebra" as .score
    show .score
end if
```

---

*The VERN Project — 2026*
