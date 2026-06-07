# VERN — What It Is and How It Thinks

## Overview

VERN is a programming language where the code itself is written in your own language — not English translated for you, not English with a different interface, but actual executable code in the words you already know. It is designed for people who want to make computers do things but have never been able to get past the wall that programming languages put up. That wall is mostly made of English.

This document explains what VERN is, what makes it different, and how it thinks — so that by the time you write your first line of code, you already understand what you are doing and why it works.

---

## The Short Version

VERN is a language that runs on a fixed grammar and swappable words. The grammar — the rules about how instructions are structured — never changes. The words are just one possible set. Swap the English words for Swahili words, and the program still runs. Swap them for Japanese, same thing. The machine cares about the grammar. The words are for you.

If that is enough to orient you, you can stop here and go to the plain-language reference. If you want to understand why it works this way and what it means in practice, keep reading.

---

## The Problem VERN Is Solving

Every programming language in widespread use requires you to learn English. Not conversational English — a specific set of English commands that the computer recognizes. `if`, `then`, `else`, `return`, `function`, `while`. These are English words. A programmer in Japan, a programmer in Kenya, a programmer in Egypt — all of them have to learn these English words before they can make a computer do anything. The code is in English even when the programmer is not.

This is not a translation problem. Plenty of programming tools have been translated — menus, error messages, documentation. But the code itself stays English. When you write a program, you write it in English keywords, regardless of what language you think in.

VERN treats that as a design flaw worth fixing. The words a program uses to give instructions are just a surface — they could be any words, in any language, as long as they map to the same underlying actions. VERN makes that mapping explicit and replaceable. The English word `show` and the Swahili word `onyesha` and the Japanese `表示する` all mean the same thing to the machine. A program written in any of them runs the same way.

---

## What Controlled Natural Language Means

VERN is described as a controlled natural language. Both words matter.

**Natural language** means the instructions look like something a person would actually say or write. `show .name` reads like an instruction a person would give. `set .score to 0` reads like a sentence. There are no symbols standing in for concepts — no curly braces, no semicolons, no parentheses required to make the language work. The period and the hash symbol are the only special characters, and they each do exactly one thing.

**Controlled** means the language is strict about form. Natural language — the kind humans use with each other — is flexible, ambiguous, full of synonyms and implied meaning. That flexibility is what makes human conversation work. It is also what makes natural language impossible for a computer to parse reliably. VERN solves this by being controlled: one form per instruction, no synonyms, no optional words, no free-form phrasing. Every instruction has one correct shape. If you write it that shape, it runs. If you write it any other way, it does not.

The result is a language that reads like plain speech but behaves like precise code.

---

## How the Grammar Works

Every VERN instruction follows the same logic: a command word first, then what the command applies to, then any additional information the command needs.

`show .name` — show is the command, .name is what to show.  
`set .score to 100` — set is the command, .score is what to set, 100 is the value.  
`ask .answer` — ask is the command, .answer is where to put what the user types.

The grammar is what defines these shapes. It says: a show instruction starts with the show keyword, followed by what to show. A set instruction starts with set, followed by a reference, followed by to, followed by a value. These rules do not change. They are the same in every language VERN supports.

What changes is the words. In a Swahili binding, `show` becomes `onyesha`. In a Japanese binding, it becomes `表示する`. The grammar rule — show keyword first, then what to show — stays identical. The machine applies the same rule regardless of which word fills the show position.

This is the invariant grammar. Invariant means it does not vary. It is the fixed part. Everything else is a surface.

---

## How References Work

VERN uses a period before any name that refers to something — a value, a script, a file. The period is not decoration. It means: what follows belongs to something, or something belongs to it.

`.name` is a value called name.  
`.greeting.script` is a script called greeting.  
`.score.quiz.script` is a value called score, inside a script called quiz.

Chains read from most specific to least specific, left to right. `.score.quiz.script` says: score, which is inside quiz, which is a script. You only need to provide as much of the chain as the system needs to find what you mean without confusion. If score only exists in one place, `.score` is enough. If it exists in multiple places, you add more of the chain until it is unambiguous.

This is called the minimum context rule. Provide exactly as much context as needed — no more.

---

## How Values Work

A value in VERN holds one piece of information: a number, a word or sentence, a true/false answer, a date, or a time. You set a value with `set`, and you can use it anywhere after that by referring to it with its name.

```
set .greeting to "Hello"
show .greeting
```

Values are not modified in place. If you want to change something — convert it, combine it, calculate from it — the result goes to a new value. The original stays as it was.

```
set .price to 9.99
set .tax to .price * 0.08
set .total to .price + .tax
show .total
```

Nothing here destroys .price or .tax. They remain available. Only .total is new.

---

## How Scripts Work

A script is a named block of instructions. You define it once, run it as many times as you need. Scripts are how you organize a program into pieces that each do one thing.

```
script .greeting
    ask .username
    show "Hello", .username
end script

start at .greeting.script
```

Scripts can also accept input and return output, making them reusable tools rather than just labeled sections.

---

## How the Language Stays Readable

One instruction per line. No nesting of instructions inside each other. No symbolic punctuation. Whitespace and indentation have no effect on how the code runs — they are for the reader, not the machine.

This means a VERN program read top to bottom reads like a list of instructions written by a person. That is intentional. The goal is that a reader who has never programmed before can look at a VERN program and understand roughly what it does before they know any of the rules.

---

## What VERN Is Not

VERN is not a beginner language that you graduate out of. It is a general-purpose language — it can read and write files, do math, handle lists, make decisions, repeat actions, connect to the internet, and be extended with your own defined vocabulary. The simplicity is not a limitation. It is the design.

VERN is not a natural language interface — it does not accept free-form sentences and guess what you mean. The grammar is strict. What looks like plain speech is actually a precise pidgin.

VERN is not a translation of English programming. It is not English with a different skin. The grammar exists independently of any language. English is one vocabulary that can instantiate it. So is Swahili. So is Japanese. So is Arabic. None of them is the original.

---

## The Practical Result

You write a program in the language you already know. You run it. The machine runs the same invariant grammar that every VERN program runs, regardless of which vocabulary was used to write it.

That is the whole idea. The vocabulary is for you. The grammar is for the machine. They do not have to be the same language.

---

*The VERN Project — 2026*
