# VERN — Getting Started

## Overview

This guide walks you through writing and running your first VERN programs. It assumes you have read the concept overview and have VERN installed on your machine. By the end you will have written two working programs — a short one that covers the basics, and a longer one that shows more of what the language can do.

You do not need to know how to program. That is the point.

---

## Before You Start

You need two things:

1. **`vern.exe`** — the VERN interpreter. This is a single file, no installation required. Put it somewhere you can find it, or add it to your system path so you can run it from anywhere.
2. **A place to write code** — any plain text editor works. If you have VS Code, the VERN syntax highlighting extension makes reading your code significantly easier.

VERN programs are plain text files saved with the `.vern` extension. You write the program, save the file, and run it with the interpreter.

---

## Running a Program

Open a terminal — Command Prompt or PowerShell on Windows. Navigate to the folder where your `.vern` file is saved. Run:

```
vern yourfilename.vern
```

That is it. The interpreter reads the file and executes it. If something goes wrong, it writes an error log in the same folder telling you what happened and on which line.

---

## Your First Program

Open a new file, name it `hello.vern`, and type the following exactly:

```
script .main
    ask .name
    show "hello, ", .name
end script

start at .main.script
stop
```

Save it and run it. The program will pause and wait for you to type something. Type your name and press enter. It will greet you by name.

That is a complete VERN program. Let's look at what each part does.

---

### Breaking It Down

**`script .main`**

This starts a script — a named block of instructions. The name here is `.main`. The period before the name is required — it tells VERN this is a reference to something in the program, not a reserved word. The name is your choice.

**`ask .name`**

Pauses the program and waits for the user to type something. Whatever they type is stored in a value called `.name`. `ask` always stores the input as text.

**`show "hello, ", .name`**

Displays text on screen. The comma separates two things being shown: the literal text `"hello, "` and the value stored in `.name`. They display one after the other on the same line.

**`end script`**

Closes the script block. Every `script` has an `end script`.

**`start at .main.script`**

Tells VERN where to begin. Without this, execution starts at the first line of the file and reads down. `start at` gives you explicit control over the entry point. `.main.script` means: the script named `.main`.

**`stop`**

Ends the program. VERN adds this automatically at the end of every file, but writing it explicitly is good practice.

---

### What You Just Learned

In six lines of code you used three of the most common things in VERN:

- **A script** — a named, reusable block of instructions
- **A value** — a named container for data, created the moment you used it
- **Input and output** — asking the user for something, then displaying something back

Every VERN program is built from these same pieces. The language gets more capable but the structure stays the same.

---

## Your Second Program

This one does more. It asks the user to enter a list of words, keeps track of them, and at the end shows the full list and a count of how many were entered.

Create a new file called `collector.vern` and type the following:

```
list words
end list

script .collect
    set .running to true
    while .running = true
        ask .input
        if .input = "done" then set .running to false
        if .input is not "done" then put .input in list words
    end while
end script

script .report
    count list words as .total
    convert .total to text as .totaltext
    show "you entered ", .totaltext, " words"
    show "here they are:"
    repeat through list words
        show current item
    end repeat
end script

script .main
    show "type words one at a time. type done when you are finished."
    run .collect.script
    run .report.script
end script

start at .main.script
stop
```

Save it and run it. Type a few words, pressing enter after each one. When you are done, type `done` and press enter. The program will show you everything you entered and how many items there were.

---

### Breaking It Down

**`list words` / `end list`**

This declares a list called `words`. A list is an ordered collection of values, all the same type. This one starts empty — items get added while the program runs. Lists live outside of scripts, at the top of the file, so all scripts can use them.

**`set .running to true`**

Creates a value called `.running` and sets it to `true`. This is going to control the loop — as long as `.running` is true, the loop keeps going.

**`while .running = true`**

A while loop runs its instructions over and over as long as the condition holds. This one keeps going as long as `.running` is true. As soon as something changes `.running` to false, the loop stops.

**`ask .input`**

Waits for the user to type something and stores it in `.input`. This is inside the loop, so it asks again every pass.

**`if .input = "done" then set .running to false`**

Checks whether what the user typed is the word `done`. If it is, it sets `.running` to false — which will stop the loop after this pass finishes.

**`if .input is not "done" then put .input in list words`**

If what the user typed is not `done`, adds it to the list. `put ... in list` always adds to the end. Notice the two `if` lines work as a pair — one handles the exit case, the other handles the normal case.

**`count list words as .total`**

Counts how many items are in the list and stores the result in `.total` as a number.

**`convert .total to text as .totaltext`**

Converts the number to text so it can be shown alongside other text using `+` or in a `show` instruction with a comma. VERN never converts types automatically — you do it explicitly.

**`show "you entered ", .totaltext, " words"`**

Shows three things in sequence: a piece of text, the count, and another piece of text.

**`repeat through list words`**

Loops through every item in the list from first to last. On each pass, `current item` holds that item's value.

**`show current item`**

Displays the current item. `current item` is a special read-only keyword available only inside this kind of loop.

**`run .collect.script` / `run .report.script`**

Calls the other scripts in order. This is how `.main` works — it orchestrates the other scripts rather than doing the work itself. Each script has one job.

---

### What You Just Learned

The second program introduced:

- **Lists** — ordered collections you can add to, count, and loop through
- **While loops** — repeat until a condition changes
- **Decisions** — `if` checks that branch the program based on what is true
- **Multiple scripts** — breaking a program into named pieces that each do one thing
- **Type conversion** — changing a number to text before displaying it

Put together, these cover the core of how most programs work: collect input, process it, report back.

---

## What to Do Next

From here, the plain-language reference covers every instruction in VERN — what it does, what it looks like, and a working example. You do not need to read it all at once. Use it as a lookup tool: when you want to do something you have not done before, find the section for it.

A few things worth exploring next:

- **`if` with `otherwise`** — handle both the true and false case in one block
- **Script parameters** — pass values directly into a script when you call it
- **`attempt`** — handle errors gracefully so a bad input does not crash the program
- **Dictionaries** — store key-value pairs, like a name paired with a score
- **File operations** — read from and write to files so data persists between runs

None of these require more than what you already know to understand. Pick something that sounds useful and look it up.

---

*The VERN Project — 2026*
