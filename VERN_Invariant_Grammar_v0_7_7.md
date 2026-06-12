# VERN Invariant Grammar Specification v0.7.7
## Universal Imperative Grammar with Vocabulary Bindings

**Document Version:** 7.7
**Date:** 2026-06-11
**Author:** The VERN Project
**Status:** Public Prior Art — All rights reserved

---

## Overview

This document defines the VERN invariant grammar: a formal structure for expressing computational intent that is independent of any human language. The grammar is the fixed, non-negotiable substrate. Vocabulary bindings are replaceable surfaces — one per language — that map human language keywords to invariant grammar tokens without altering execution semantics.

This document establishes two things:

1. The invariant grammar in language-agnostic abstract notation
2. Four vocabulary bindings demonstrating that the grammar is equally valid in English, Swahili, Japanese, and Arabic

Programs written in any of these bindings execute identically. The grammar is the same. Only the words change.

This document constitutes a public prior art claim for the architecture described herein. The core claim is:

> A programming language grammar in which the vocabulary is the localization target — not the user interface, not the documentation, not the error messages, but the executable keywords themselves — such that code written natively in any human language executes identically to code written in any other.

---

## Part I: The Invariant Grammar

### Design Constraints

The invariant grammar is designed to satisfy the following constraints without exception:

1. **Morphology-agnostic** — no inflection, no tense, no plurality, no articles, no case marking required
2. **Script-agnostic** — works with Latin, Arabic, Japanese, Cyrillic, Devanagari, or any Unicode script
3. **Direction-agnostic** — accommodates left-to-right and right-to-left scripts
4. **No natural language parsing** — the parser resolves token positions, not linguistic meaning
5. **One instruction per line** — no continuations, no semicolons, no implicit line joining
6. **Keyword-driven** — every instruction begins with a keyword token; the parser never guesses
7. **Case-insensitive** — all keyword matching is case-normalized before comparison
8. **Two structural symbols only** — `.` for containment hierarchy, `#` for container tags. Grouping delimiters `(` and `)` are valid in math expressions but carry no structural meaning in the reference or container systems.

### Abstract Syntax

The following notation uses invariant token names in ALL CAPS. These are not English words — they are abstract labels for grammar positions. Each is replaced by a vocabulary binding's equivalent word or phrase.

```
PROGRAM ::= (IMPORT | FILE_VALUE | LIST | CONTAINER | SCRIPT | COMMENT)* [ROUTE_TABLE] [ENTRY_POINT] [STOP_OR_MODE] [SERVE_DECLARATION]

STOP_OR_MODE ::= STOP_KW
               | WAIT_KW RESET_KW
               | WAIT_KW KEEP_KW
               | CYCLE_KW RESET_KW
               | CYCLE_KW KEEP_KW

ROUTE_TABLE ::= ROUTE_DECLARATION+
ROUTE_DECLARATION ::= ROUTE_KW TEXT TO_KW REFERENCE

SERVE_DECLARATION ::= SERVE_KW NUMBER

IMPORT ::= IMPORT_KW REFERENCE

FILE_VALUE ::= SET_KW REFERENCE TO_KW EXPRESSION
             | DEFINE_KW TEXT AS_KW RUN_KW REFERENCE

LIST ::= LIST_KW IDENTIFIER (REFERENCE)?
         VALUE*
         END_KW LIST_KW

CONTAINER ::= HASH IDENTIFIER
              (SET_KW REFERENCE TO_KW VALUE)*

SCRIPT ::= SCRIPT_HEADER [CONTAINER_TAG] INSTRUCTION* END_SCRIPT
SCRIPT_HEADER ::= SCRIPT_KW REFERENCE [TAKES_KW PARAM_DECL (SEPARATOR PARAM_DECL)*]

PARAM_DECL ::= REFERENCE | LIST_KW IDENTIFIER | DICTIONARY_KW IDENTIFIER | SCRIPT_KW IDENTIFIER
END_SCRIPT ::= END_KW SCRIPT_KW
CONTAINER_TAG ::= HASH IDENTIFIER

ENTRY_POINT ::= START_KW AT_KW REFERENCE

INSTRUCTION ::= SHOW_INSTRUCTION
              | ASK_INSTRUCTION
              | READ_INSTRUCTION
              | WRITE_INSTRUCTION
              | APPEND_INSTRUCTION
              | SET_INSTRUCTION
              | IF_INSTRUCTION
              | IF_BLOCK_INSTRUCTION
              | WHILE_INSTRUCTION
              | REPEAT_INSTRUCTION
              | REPEAT_THROUGH_INSTRUCTION
              | RUN_INSTRUCTION
              | CONVERT_INSTRUCTION
              | RETURN_INSTRUCTION
              | STOP_INSTRUCTION
              | PUT_INSTRUCTION
              | REMOVE_INSTRUCTION
              | GET_LIST_INSTRUCTION
              | COUNT_INSTRUCTION
              | ROUND_INSTRUCTION
              | FLOOR_INSTRUCTION
              | CEILING_INSTRUCTION
              | RANDOM_INSTRUCTION
              | ABSOLUTE_INSTRUCTION
              | MINIMUM_INSTRUCTION
              | MAXIMUM_INSTRUCTION
              | PERCENT_INSTRUCTION
              | LENGTH_INSTRUCTION
              | FIND_INSTRUCTION
              | EXTRACT_INSTRUCTION
              | REPLACE_INSTRUCTION
              | GET_DATE_INSTRUCTION
              | GET_TIME_INSTRUCTION
              | DIFFERENCE_INSTRUCTION
              | FORMAT_INSTRUCTION
              | ATTEMPT_INSTRUCTION
              | DELETE_INSTRUCTION
              | EXIST_INSTRUCTION
              | GET_FILES_INSTRUCTION
              | SINE_INSTRUCTION
              | COSINE_INSTRUCTION
              | TANGENT_INSTRUCTION
              | ARCSINE_INSTRUCTION
              | ARCCOSINE_INSTRUCTION
              | ARCTANGENT_INSTRUCTION
              | HYPERBOLIC_SINE_INSTRUCTION
              | HYPERBOLIC_COSINE_INSTRUCTION
              | HYPERBOLIC_TANGENT_INSTRUCTION
              | ARC_HYPERBOLIC_SINE_INSTRUCTION
              | ARC_HYPERBOLIC_COSINE_INSTRUCTION
              | ARC_HYPERBOLIC_TANGENT_INSTRUCTION
              | LN_INSTRUCTION
              | LOG_INSTRUCTION
              | TO_DEGREES_INSTRUCTION
              | TO_RADIANS_INSTRUCTION
              | SUM_INSTRUCTION
              | FACTORIAL_INSTRUCTION
              | COMBINATIONS_INSTRUCTION
              | PERMUTATIONS_INSTRUCTION
              | SIGN_INSTRUCTION
              | EXIT_LOOP_INSTRUCTION
              | NEXT_ITEM_INSTRUCTION
              | SPLIT_INSTRUCTION
              | JOIN_INSTRUCTION
              | TRIM_INSTRUCTION
              | UPPERCASE_INSTRUCTION
              | LOWERCASE_INSTRUCTION
              | SORT_INSTRUCTION
              | REVERSE_INSTRUCTION
              | SLICE_INSTRUCTION
              | COMBINE_INSTRUCTION
              | REPEAT_THROUGH_DICTIONARY_INSTRUCTION
              | GET_DICTIONARY_INSTRUCTION
              | PUT_DICTIONARY_INSTRUCTION
              | REMOVE_DICTIONARY_INSTRUCTION
              | COUNT_DICTIONARY_INSTRUCTION
              | TYPE_OF_INSTRUCTION
              | FORMAT_NUMBER_INSTRUCTION
              | TEXT_BLOCK
              | FETCH_INSTRUCTION
              | SEND_INSTRUCTION
              | PUT_DICT_IN_LIST_INSTRUCTION
              | PUT_DICT_IN_DICT_INSTRUCTION
              | DYNAMIC_READ_INSTRUCTION
              | DYNAMIC_WRITE_INSTRUCTION
              | DYNAMIC_APPEND_INSTRUCTION
              | DYNAMIC_EXIST_INSTRUCTION
              | UPDATE_INSTRUCTION
              | DELETE_URL_INSTRUCTION
              | FETCH_WITH_HEADERS_INSTRUCTION
              | SEND_WITH_HEADERS_INSTRUCTION
              | PARSE_INSTRUCTION
              | INSPECT_INSTRUCTION
              | INVOKE_INSTRUCTION
              | SET_NONE_INSTRUCTION
              | RESPOND_INSTRUCTION
              | LAUNCH_INSTRUCTION
              | WAIT_INSTRUCTION

SHOW_INSTRUCTION   ::= SHOW_KW (REFERENCE | VALUE) (SEPARATOR (REFERENCE | VALUE))*
ASK_INSTRUCTION    ::= ASK_KW REFERENCE
READ_INSTRUCTION   ::= READ_KW REFERENCE (SEPARATOR REFERENCE)* FROM_KW REFERENCE
WRITE_INSTRUCTION  ::= WRITE_KW REFERENCE (SEPARATOR REFERENCE)* TO_KW REFERENCE
APPEND_INSTRUCTION ::= APPEND_KW REFERENCE (SEPARATOR REFERENCE)* TO_KW REFERENCE
SET_INSTRUCTION    ::= SET_KW REFERENCE TO_KW EXPRESSION
IF_INSTRUCTION     ::= IF_KW CONDITION THEN_KW INSTRUCTION
IF_BLOCK_INSTRUCTION ::= IF_KW CONDITION INSTRUCTION* [OTHERWISE_KW INSTRUCTION*] END_IF
END_IF             ::= END_KW IF_KW
WHILE_INSTRUCTION  ::= WHILE_KW CONDITION INSTRUCTION* END_WHILE
END_WHILE          ::= END_KW WHILE_KW
RUN_INSTRUCTION    ::= RUN_KW REFERENCE [WITH_KW PARAM_ARG (SEPARATOR PARAM_ARG)*] [CONTAINER_TAG] [AS_KW REFERENCE (SEPARATOR REFERENCE)*]

PARAM_ARG ::= VALUE | REFERENCE | LIST_KW LIST_REF | DICTIONARY_KW DICT_REF | SCRIPT_KW REFERENCE
STOP_INSTRUCTION   ::= STOP_KW
                     | STOP_KW FILE_REFERENCE

LAUNCH_INSTRUCTION ::= LAUNCH_KW FILE_REFERENCE

WAIT_INSTRUCTION   ::= WAIT_KW NUMBER SECONDS_KW
                     | WAIT_KW NUMBER MILLISECONDS_KW

RESPOND_INSTRUCTION ::= RESPOND_KW (REFERENCE | TEXT | NUMBER)  [STATUS_KW NUMBER]
                       | RESPOND_KW FILE_KW FILE_REFERENCE [STATUS_KW NUMBER]
                       | RESPOND_KW FILE_KW PATH_KW REFERENCE [STATUS_KW NUMBER]
                       | RESPOND_KW TEXT [STATUS_KW NUMBER]

CONVERT_INSTRUCTION ::= CONVERT_KW (REFERENCE | LOOP_KW | CURRENT_ITEM_KW | CURRENT_KEY_KW | CURRENT_VALUE_KW) TO_KW TYPE_KW AS_KW REFERENCE
TYPE_KW ::= NUMBER_KW | TEXT_KW | DATE_KW | TIME_KW

RETURN_INSTRUCTION ::= RETURN_KW REFERENCE PASS_KW TO_KW REFERENCE
                     | RETURN_KW REFERENCE

REPEAT_INSTRUCTION         ::= REPEAT_KW NUMBER TIMES_KW INSTRUCTION* END_REPEAT
REPEAT_THROUGH_INSTRUCTION ::= REPEAT_KW THROUGH_KW LIST_KW LIST_REF INSTRUCTION* END_REPEAT
END_REPEAT ::= END_KW REPEAT_KW

LIST_REF ::= IDENTIFIER (REFERENCE)?

PUT_INSTRUCTION    ::= PUT_KW REFERENCE IN_KW LIST_KW LIST_REF
REMOVE_INSTRUCTION ::= REMOVE_KW REFERENCE FROM_KW LIST_KW LIST_REF
GET_LIST_INSTRUCTION ::= GET_KW LIST_KW LIST_REF NUMBER AS_KW REFERENCE
COUNT_INSTRUCTION  ::= COUNT_KW LIST_KW LIST_REF AS_KW REFERENCE

ROUND_INSTRUCTION   ::= ROUND_KW REFERENCE [TO_KW NUMBER] AS_KW REFERENCE
FLOOR_INSTRUCTION   ::= FLOOR_KW REFERENCE [TO_KW NUMBER] AS_KW REFERENCE
CEILING_INSTRUCTION ::= CEILING_KW REFERENCE [TO_KW NUMBER] AS_KW REFERENCE
RANDOM_INSTRUCTION  ::= RANDOM_KW (NUMBER | REFERENCE) TO_KW (NUMBER | REFERENCE) AS_KW REFERENCE
ABSOLUTE_INSTRUCTION ::= ABSOLUTE_KW REFERENCE AS_KW REFERENCE
MINIMUM_INSTRUCTION ::= MINIMUM_KW (REFERENCE REFERENCE | LIST_KW LIST_REF) AS_KW REFERENCE
MAXIMUM_INSTRUCTION ::= MAXIMUM_KW (REFERENCE REFERENCE | LIST_KW LIST_REF) AS_KW REFERENCE
PERCENT_INSTRUCTION ::= PERCENT_KW REFERENCE OF_KW REFERENCE AS_KW REFERENCE

LENGTH_INSTRUCTION  ::= LENGTH_KW OF_KW REFERENCE AS_KW REFERENCE
FIND_INSTRUCTION    ::= FIND_KW (TEXT | REFERENCE) IN_KW REFERENCE AS_KW REFERENCE
EXTRACT_INSTRUCTION ::= EXTRACT_KW FROM_KW REFERENCE BEGINNING_KW (NUMBER | REFERENCE) FINISHING_KW (NUMBER | REFERENCE) AS_KW REFERENCE
REPLACE_INSTRUCTION ::= REPLACE_KW (TEXT | REFERENCE) WITH_KW (TEXT | REFERENCE) IN_KW REFERENCE AS_KW REFERENCE

GET_DATE_INSTRUCTION ::= GET_KW DATE_KW AS_KW REFERENCE
GET_TIME_INSTRUCTION ::= GET_KW TIME_KW AS_KW REFERENCE
DIFFERENCE_INSTRUCTION ::= DIFFERENCE_KW BETWEEN_KW REFERENCE AND_KW REFERENCE IN_KW UNIT_KW AS_KW REFERENCE
UNIT_KW ::= DAYS_KW | HOURS_KW | MINUTES_KW
FORMAT_INSTRUCTION ::= FORMAT_KW REFERENCE AS_KW REFERENCE USING_KW (TEXT | REFERENCE)

ATTEMPT_INSTRUCTION ::= ATTEMPT_KW [ALL_KW] INSTRUCTION* FAIL_HANDLER+ END_FAIL END_ATTEMPT

FAIL_HANDLER ::= TYPED_FAIL_HANDLER | CATCHALL_FAIL_HANDLER
TYPED_FAIL_HANDLER    ::= IF_KW FAIL_KW TEXT INSTRUCTION*
CATCHALL_FAIL_HANDLER ::= IF_KW FAIL_KW INSTRUCTION*

IF_FAIL     ::= IF_KW FAIL_KW
END_FAIL    ::= END_KW FAIL_KW
END_ATTEMPT ::= END_KW ATTEMPT_KW

DELETE_INSTRUCTION    ::= DELETE_KW FILE_REFERENCE
                        | DELETE_KW PATH_KW REFERENCE
EXIST_INSTRUCTION     ::= IF_KW FILE_REFERENCE EXIST_KW THEN_KW INSTRUCTION
                        | IF_KW FILE_REFERENCE EXIST_KW INSTRUCTION* [OTHERWISE_KW INSTRUCTION*] END_IF
GET_FILES_INSTRUCTION ::= GET_KW FILES_KW IN_KW DIR_REFERENCE AS_KW LIST_KW LIST_REF

DYNAMIC_READ_INSTRUCTION   ::= READ_KW REFERENCE FROM_KW PATH_KW REFERENCE
DYNAMIC_WRITE_INSTRUCTION  ::= WRITE_KW REFERENCE TO_KW PATH_KW REFERENCE
DYNAMIC_APPEND_INSTRUCTION ::= APPEND_KW REFERENCE TO_KW PATH_KW REFERENCE
DYNAMIC_EXIST_INSTRUCTION  ::= IF_KW PATH_KW REFERENCE EXIST_KW THEN_KW INSTRUCTION
                              | IF_KW PATH_KW REFERENCE EXIST_KW INSTRUCTION* [OTHERWISE_KW INSTRUCTION*] END_IF

FILE_REFERENCE ::= PERIOD IDENTIFIER PERIOD FILE_EXT_KW (PERIOD IDENTIFIER PERIOD FOLDER_KW)* (PERIOD PARENT_KW)?
FILE_EXT_KW    ::= VERN_KW | TEXT_EXT_KW | BINARY_EXT_KW
TEXT_EXT_KW    ::= "txt" | "json" | "csv" | "xml" | "ini" | "html" | "md" | "log" | "yaml" | "yml" | "toml" | "sql"
BINARY_EXT_KW  ::= "png" | "jpg" | "jpeg" | "gif" | "webp" | "svg" | "ico" | "pdf" | "mp3" | "wav" | "mp4" | "mov" | "webm" | "zip"
DIR_REFERENCE  ::= PERIOD IDENTIFIER PERIOD FOLDER_KW (PERIOD IDENTIFIER PERIOD FOLDER_KW)* (PERIOD PARENT_KW)?
                 | PERIOD PARENT_KW

SINE_INSTRUCTION       ::= SINE_KW REFERENCE [RADIANS_KW] AS_KW REFERENCE
COSINE_INSTRUCTION     ::= COSINE_KW REFERENCE [RADIANS_KW] AS_KW REFERENCE
TANGENT_INSTRUCTION    ::= TANGENT_KW REFERENCE [RADIANS_KW] AS_KW REFERENCE
ARCSINE_INSTRUCTION    ::= ARCSINE_KW REFERENCE [RADIANS_KW] AS_KW REFERENCE
ARCCOSINE_INSTRUCTION  ::= ARCCOSINE_KW REFERENCE [RADIANS_KW] AS_KW REFERENCE
ARCTANGENT_INSTRUCTION ::= ARCTANGENT_KW REFERENCE [REFERENCE] [RADIANS_KW] AS_KW REFERENCE

HYPERBOLIC_SINE_INSTRUCTION      ::= HYPERBOLIC_KW SINE_KW REFERENCE AS_KW REFERENCE
HYPERBOLIC_COSINE_INSTRUCTION    ::= HYPERBOLIC_KW COSINE_KW REFERENCE AS_KW REFERENCE
HYPERBOLIC_TANGENT_INSTRUCTION   ::= HYPERBOLIC_KW TANGENT_KW REFERENCE AS_KW REFERENCE
ARC_HYPERBOLIC_SINE_INSTRUCTION  ::= ARC_KW HYPERBOLIC_KW SINE_KW REFERENCE AS_KW REFERENCE
ARC_HYPERBOLIC_COSINE_INSTRUCTION ::= ARC_KW HYPERBOLIC_KW COSINE_KW REFERENCE AS_KW REFERENCE
ARC_HYPERBOLIC_TANGENT_INSTRUCTION ::= ARC_KW HYPERBOLIC_KW TANGENT_KW REFERENCE AS_KW REFERENCE

LN_INSTRUCTION  ::= LN_KW REFERENCE AS_KW REFERENCE
LOG_INSTRUCTION ::= LOG_KW REFERENCE [BASE_KW (NUMBER | REFERENCE)] AS_KW REFERENCE

TO_DEGREES_INSTRUCTION ::= TO_KW DEGREES_KW REFERENCE AS_KW REFERENCE
TO_RADIANS_INSTRUCTION ::= TO_KW RADIANS_KW REFERENCE AS_KW REFERENCE

SUM_INSTRUCTION          ::= SUM_KW LIST_KW LIST_REF AS_KW REFERENCE
FACTORIAL_INSTRUCTION    ::= FACTORIAL_KW REFERENCE AS_KW REFERENCE
COMBINATIONS_INSTRUCTION ::= COMBINATIONS_KW REFERENCE REFERENCE AS_KW REFERENCE
PERMUTATIONS_INSTRUCTION ::= PERMUTATIONS_KW REFERENCE REFERENCE AS_KW REFERENCE
SIGN_INSTRUCTION         ::= SIGN_KW REFERENCE AS_KW REFERENCE

EXIT_LOOP_INSTRUCTION ::= EXIT_KW LOOP_KW
NEXT_ITEM_INSTRUCTION ::= NEXT_KW ITEM_KW

SPLIT_INSTRUCTION     ::= SPLIT_KW REFERENCE BY_KW (TEXT | REFERENCE) AS_KW LIST_KW LIST_REF
JOIN_INSTRUCTION      ::= JOIN_KW LIST_KW LIST_REF BY_KW (TEXT | REFERENCE) AS_KW REFERENCE
TRIM_INSTRUCTION      ::= TRIM_KW REFERENCE AS_KW REFERENCE
UPPERCASE_INSTRUCTION ::= UPPERCASE_KW REFERENCE AS_KW REFERENCE
LOWERCASE_INSTRUCTION ::= LOWERCASE_KW REFERENCE AS_KW REFERENCE

SORT_INSTRUCTION    ::= SORT_KW LIST_KW LIST_REF [DESCENDING_KW] AS_KW LIST_KW LIST_REF
REVERSE_INSTRUCTION ::= REVERSE_KW LIST_KW LIST_REF AS_KW LIST_KW LIST_REF
SLICE_INSTRUCTION   ::= SLICE_KW LIST_KW LIST_REF (NUMBER | REFERENCE) TO_KW (NUMBER | REFERENCE) AS_KW LIST_KW LIST_REF
COMBINE_INSTRUCTION ::= COMBINE_KW LIST_KW LIST_REF WITH_KW LIST_KW LIST_REF AS_KW LIST_KW LIST_REF

DICT_REF ::= IDENTIFIER (REFERENCE)?

DICTIONARY_BLOCK ::= DICTIONARY_KW IDENTIFIER (TEXT COLON VALUE)* END_KW DICTIONARY_KW

GET_DICTIONARY_INSTRUCTION    ::= GET_KW DICTIONARY_KW DICT_REF KEY_KW (TEXT | REFERENCE) AS_KW REFERENCE
PUT_DICTIONARY_INSTRUCTION    ::= PUT_KW REFERENCE IN_KW DICTIONARY_KW DICT_REF KEY_KW (TEXT | REFERENCE)
REMOVE_DICTIONARY_INSTRUCTION ::= REMOVE_KW KEY_KW (TEXT | REFERENCE) FROM_KW DICTIONARY_KW DICT_REF
COUNT_DICTIONARY_INSTRUCTION  ::= COUNT_KW DICTIONARY_KW DICT_REF AS_KW REFERENCE
REPEAT_THROUGH_DICTIONARY_INSTRUCTION ::= REPEAT_KW THROUGH_KW DICTIONARY_KW DICT_REF INSTRUCTION* END_REPEAT

TYPE_OF_INSTRUCTION    ::= TYPEOF_KW (REFERENCE | CURRENT_ITEM_KW | CURRENT_KEY_KW | CURRENT_VALUE_KW) AS_KW REFERENCE

FORMAT_NUMBER_INSTRUCTION ::= FORMAT_KW REFERENCE AS_KW REFERENCE FORMAT_NUMBER_MODIFIER+
FORMAT_NUMBER_MODIFIER    ::= DECIMALS_KW NUMBER | THOUSANDS_KW | PADDED_KW NUMBER

TEXT_BLOCK ::= TEXT_BLOCK_KW REFERENCE RAW_CONTENT* END_KW TEXT_BLOCK_KW
RAW_CONTENT ::= any character sequence until END_KW TEXT_BLOCK_KW

FETCH_INSTRUCTION ::= FETCH_KW REFERENCE [WITH_KW HEADERS_KW DICTIONARY_KW IDENTIFIER] AS_KW REFERENCE [RESPONSE_KW HEADERS_KW REFERENCE] [STATUS_KW REFERENCE]

SEND_INSTRUCTION  ::= SEND_KW REFERENCE TO_KW REFERENCE [WITH_KW HEADERS_KW DICTIONARY_KW IDENTIFIER] [STATUS_KW REFERENCE]

UPDATE_INSTRUCTION ::= UPDATE_KW REFERENCE TO_KW REFERENCE [WITH_KW HEADERS_KW DICTIONARY_KW IDENTIFIER] [STATUS_KW REFERENCE]

DELETE_URL_INSTRUCTION ::= DELETE_KW REFERENCE [WITH_KW HEADERS_KW DICTIONARY_KW IDENTIFIER] [STATUS_KW REFERENCE]

PUT_DICT_IN_LIST_INSTRUCTION ::= PUT_KW DICTIONARY_KW IDENTIFIER IN_KW LIST_KW LIST_REF
PUT_DICT_IN_DICT_INSTRUCTION ::= PUT_KW DICTIONARY_KW IDENTIFIER IN_KW DICTIONARY_KW DICT_REF KEY_KW (TEXT | REFERENCE)

FORMAT_ID ::= JSON_KW | CSV_KW | XML_KW | INI_KW

PARSE_INSTRUCTION   ::= PARSE_KW FORMAT_ID REFERENCE AS_KW (LIST_KW IDENTIFIER | DICTIONARY_KW IDENTIFIER)

INSPECT_INSTRUCTION ::= INSPECT_KW FORMAT_ID REFERENCE

INVOKE_INSTRUCTION ::= INVOKE_KW SCRIPT_KW IDENTIFIER [WITH_KW PARAM_ARG (SEPARATOR PARAM_ARG)*] [AS_KW REFERENCE (SEPARATOR REFERENCE)*]

CONDITION ::= EXPRESSION COMPARISON_OP EXPRESSION
            | NOT_KW CONDITION
            | CONDITION AND_KW CONDITION
            | CONDITION OR_KW CONDITION
            | EXPRESSION IS_IN_KW LIST_KW LIST_REF
            | EXPRESSION NOT_IN_KW LIST_KW LIST_REF
            | EXPRESSION IS_IN_KW REFERENCE
            | EXPRESSION NOT_IN_KW REFERENCE
            | EXPRESSION IS_IN_KW DICTIONARY_KW DICT_REF
            | EXPRESSION NOT_IN_KW DICTIONARY_KW DICT_REF
            | REFERENCE STARTS_WITH_KW (TEXT | REFERENCE)
            | REFERENCE ENDS_WITH_KW (TEXT | REFERENCE)

COLON ::= ":"

CONSTANT ::= PI_KW | E_KW | TAU_KW | INFINITY_KW

EXPRESSION ::= VALUE
             | REFERENCE
             | LOOP_KW
             | CURRENT_ITEM_KW
             | FAIL_REASON_KW
             | CONSTANT
             | REQUEST_BODY_KW
             | REQUEST_PATH_KW
             | REQUEST_HEADERS_KW
             | REQUEST_METHOD_KW
             | EXPRESSION MATH_OP EXPRESSION
             | EXPRESSION POWER_KW NUMBER
             | EXPRESSION ROOT_KW NUMBER
             | EXPRESSION REMAINDER_KW EXPRESSION
             | LPAREN EXPRESSION RPAREN

LPAREN ::= "("
RPAREN ::= ")"

REFERENCE ::= PERIOD IDENTIFIER (PERIOD IDENTIFIER)* [CONTAINER_TAG]
CONTAINER_REF ::= HASH IDENTIFIER (PERIOD IDENTIFIER)*

VALUE ::= TEXT | NUMBER | BOOLEAN | DATE_LITERAL | TIME_LITERAL | NONE_KW
TEXT ::= DOUBLE_QUOTE CHARACTER* DOUBLE_QUOTE
NUMBER ::= ["-"] DIGIT+ (PERIOD DIGIT+)?
BOOLEAN ::= TRUE_KW | FALSE_KW
DATE_LITERAL ::= DIGIT DIGIT DIGIT DIGIT "-" DIGIT DIGIT "-" DIGIT DIGIT
TIME_LITERAL ::= DIGIT DIGIT ":" DIGIT DIGIT ":" DIGIT DIGIT

IDENTIFIER ::= UNICODE_LETTER (UNICODE_LETTER | DIGIT | UNDERSCORE)*
UNICODE_LETTER ::= any Unicode letter category character
DIGIT ::= [0-9]
UNDERSCORE ::= "_"

SEPARATOR ::= ","
PERIOD ::= "."
HASH ::= "#"
DOUBLE_QUOTE ::= '"'

COMMENT ::= "//" CHARACTER* (end of line)

MATH_OP ::= ADD_KW | SUBTRACT_KW | MULTIPLY_KW | DIVIDE_KW
          | "+" | "-" | "*" | "/"

COMPARISON_OP ::= IS_EQUAL_TO_KW | IS_NOT_KW
                | IS_GREATER_THAN_KW | IS_LESS_THAN_KW
                | IS_GREATER_THAN_OR_EQUAL_TO_KW
                | IS_LESS_THAN_OR_EQUAL_TO_KW
                | "=" | "!=" | ">" | "<" | ">=" | "<="
```

### Invariant Token List

The following tokens must be mapped by every vocabulary binding. Symbol operators (`+`, `-`, `*`, `/`, `=`, `!=`, `>`, `<`, `>=`, `<=`) are universal across all bindings and require no mapping.

| Token | Role |
|---|---|
| `SHOW_KW` | display output |
| `ASK_KW` | prompt user input |
| `READ_KW` | read from file |
| `WRITE_KW` | write to file (overwrite) |
| `APPEND_KW` | write to file (append) |
| `SET_KW` | assign a value |
| `TO_KW` | destination marker |
| `FROM_KW` | source marker |
| `IF_KW` | conditional |
| `THEN_KW` | conditional action marker (inline form) |
| `WHILE_KW` | begin while loop |
| `REPEAT_KW` | begin count or list loop |
| `TIMES_KW` | loop count marker |
| `THROUGH_KW` | list iteration marker |
| `END_KW` | close a block |
| `STOP_KW` | halt execution |
| `START_KW` | entry point declaration |
| `AT_KW` | entry point marker |
| `RUN_KW` | execute a script |
| `DEFINE_KW` | define a vocabulary word |
| `AS_KW` | assignment/definition marker |
| `SCRIPT_KW` | script block marker |
| `OTHERWISE_KW` | false branch of if block |
| `AND_KW` | boolean conjunction |
| `OR_KW` | boolean disjunction |
| `NOT_KW` | boolean inversion |
| `IS_EQUAL_TO_KW` | equality comparison (word form) |
| `IS_NOT_KW` | inequality comparison (word form) |
| `IS_GREATER_THAN_KW` | greater than (word form) |
| `IS_LESS_THAN_KW` | less than (word form) |
| `IS_GREATER_THAN_OR_EQUAL_TO_KW` | greater or equal (word form) |
| `IS_LESS_THAN_OR_EQUAL_TO_KW` | less or equal (word form) |
| `ADD_KW` | addition (word form) |
| `SUBTRACT_KW` | subtraction (word form) |
| `MULTIPLY_KW` | multiplication (word form) |
| `DIVIDE_KW` | division (word form) |
| `TRUE_KW` | boolean true |
| `FALSE_KW` | boolean false |
| `CONVERT_KW` | type conversion |
| `NUMBER_KW` | number type target |
| `TEXT_KW` | text type target |
| `DATE_KW` | date type target / get current date |
| `TIME_KW` | time type target / get current time |
| `RETURN_KW` | return a value from a script |
| `PASS_KW` | pass to destination marker |
| `LOOP_KW` | implicit loop counter (read-only, inside repeat or while only) |
| `IMPORT_KW` | load an external file |
| `LIST_KW` | list identifier |
| `PUT_KW` | add item to list |
| `IN_KW` | list insertion / text search marker |
| `IS_IN_KW` | membership check (compound) |
| `NOT_IN_KW` | negative membership check (compound) |
| `REMOVE_KW` | remove item from list |
| `GET_KW` | retrieve by position, system value, or directory listing |
| `CURRENT_ITEM_KW` | implicit loop item (read-only, inside repeat through only) |
| `COUNT_KW` | count list items |
| `ROUND_KW` | round a number |
| `FLOOR_KW` | round down |
| `CEILING_KW` | round up |
| `POWER_KW` | exponent (word form) |
| `ROOT_KW` | root (word form) |
| `REMAINDER_KW` | remainder after division |
| `RANDOM_KW` | generate random number |
| `ABSOLUTE_KW` | absolute value |
| `MINIMUM_KW` | minimum value |
| `MAXIMUM_KW` | maximum value |
| `PERCENT_KW` | percentage |
| `OF_KW` | percentage source marker |
| `LENGTH_KW` | text length |
| `FIND_KW` | find text position |
| `EXTRACT_KW` | extract text portion |
| `BEGINNING_KW` | extract start position marker |
| `FINISHING_KW` | extract end position marker |
| `REPLACE_KW` | replace text |
| `WITH_KW` | replacement value marker |
| `ATTEMPT_KW` | begin error recovery block |
| `ALL_KW` | attempt all mode modifier |
| `FAIL_KW` | fail handler marker |
| `FAIL_REASON_KW` | implicit failure description (read-only, inside if fail only) |
| `DIFFERENCE_KW` | date/time difference |
| `BETWEEN_KW` | difference range marker |
| `DAYS_KW` | days unit |
| `HOURS_KW` | hours unit |
| `MINUTES_KW` | minutes unit |
| `FORMAT_KW` | format date/time for display |
| `USING_KW` | format pattern marker |
| `EXIST_KW` | file or directory existence check |
| `DELETE_KW` | delete a file |
| `FILES_KW` | list files in a directory |
| `FOLDER_KW` | directory descriptor in file reference chain |
| `PARENT_KW` | system root descriptor in file reference chain |
| `VERN_KW` | file extension descriptor in file reference chain |
| `SINE_KW` | sine operation |
| `COSINE_KW` | cosine operation |
| `TANGENT_KW` | tangent operation |
| `ARCSINE_KW` | arcsine operation |
| `ARCCOSINE_KW` | arccosine operation |
| `ARCTANGENT_KW` | arctangent operation (single and two-argument) |
| `HYPERBOLIC_KW` | hyperbolic modifier |
| `ARC_KW` | arc modifier for hyperbolic inverses |
| `LN_KW` | natural logarithm |
| `LOG_KW` | base 10 or arbitrary base logarithm |
| `BASE_KW` | arbitrary base marker |
| `PI_KW` | pi constant |
| `E_KW` | e constant |
| `TAU_KW` | tau constant |
| `INFINITY_KW` | infinity constant |
| `DEGREES_KW` | degrees conversion target |
| `RADIANS_KW` | radians modifier / conversion target |
| `SUM_KW` | sum of a numeric list |
| `FACTORIAL_KW` | factorial operation |
| `COMBINATIONS_KW` | combinations operation |
| `PERMUTATIONS_KW` | permutations operation |
| `SIGN_KW` | sign of a number |
| `EXIT_KW` | first word of exit loop compound |
| `NEXT_KW` | first word of next item compound |
| `ITEM_KW` | second word of next item compound (existing item role unchanged) |
| `BY_KW` | delimiter marker in split and join |
| `SPLIT_KW` | split text into list |
| `JOIN_KW` | join list into text |
| `TRIM_KW` | trim whitespace from text |
| `UPPERCASE_KW` | convert text to uppercase |
| `LOWERCASE_KW` | convert text to lowercase |
| `STARTS_WITH_KW` | starts with condition (compound) |
| `ENDS_WITH_KW` | ends with condition (compound) |
| `SORT_KW` | sort a list |
| `DESCENDING_KW` | descending sort modifier |
| `REVERSE_KW` | reverse a list |
| `SLICE_KW` | extract a portion of a list |
| `COMBINE_KW` | combine two lists |
| `DICTIONARY_KW` | dictionary identifier |
| `KEY_KW` | dictionary key marker |
| `CURRENT_KEY_KW` | implicit current key (read-only, repeat through dictionary only) |
| `CURRENT_VALUE_KW` | implicit current value (read-only, repeat through dictionary only) |
| `TAKES_KW` | script parameter declaration marker |
| `TYPEOF_KW` | type checking operation opener |
| `DECIMALS_KW` | number format — decimal places modifier |
| `THOUSANDS_KW` | number format — thousands separator modifier |
| `PADDED_KW` | number format — minimum width padding modifier |
| `TEXT_BLOCK_KW` | multi-line text block opener |
| `FETCH_KW` | HTTP GET request |
| `SEND_KW` | HTTP POST request |
| `NONE_KW` | none type literal and type name |
| `PATH_KW` | dynamic file reference signal |
| `INVOKE_KW` | execute a script parameter |
| `UPDATE_KW` | HTTP PUT request |
| `HEADERS_KW` | request/response headers marker |
| `STATUS_KW` | HTTP status code capture marker |
| `RESPONSE_KW` | response headers marker |
| `PARSE_KW` | parse structured text |
| `INSPECT_KW` | inspect structured text structure |
| `JSON_KW` | JSON format identifier (proper noun) |
| `CSV_KW` | CSV format identifier (proper noun) |
| `XML_KW` | XML format identifier (proper noun) |
| `INI_KW` | INI format identifier (proper noun) |
| `FAIL_TYPE_KW` | implicit failure category (read-only, inside if fail only) |
| `WAIT_KW` | wait execution mode — complete cycle and pause for next input |
| `CYCLE_KW` | cycle execution mode — complete cycle and immediately run again |
| `RESET_KW` | reset modifier — reinitialize file-level values each cycle |
| `KEEP_KW` | keep modifier — carry file-level values forward each cycle |
| `SERVE_KW` | web serving declaration — open port and listen for HTTP requests |
| `ROUTE_KW` | route declaration — map a URL path to a named script |
| `RESPOND_KW` | HTTP response — send a value back to the caller |
| `REQUEST_BODY_KW` | incoming request body (read-only, inside routed script only) |
| `REQUEST_PATH_KW` | incoming request URL path (read-only, inside routed script only) |
| `REQUEST_HEADERS_KW` | incoming request headers as dictionary (read-only, inside routed script only) |
| `REQUEST_METHOD_KW` | incoming request HTTP method as text (read-only, inside routed script only) |
| `FILE_KW` | file response marker in respond instruction — signals that what follows is a file reference |

### Invariant Properties

These properties are non-negotiable across all bindings:

- `.` is the sole containment hierarchy symbol. User-defined names are always prefixed with `.`
- `#` is the container tag symbol. Container names are always prefixed with `#`
- `"` delimits text literals. Text literals are not localized
- `,` is the value separator in multi-value instructions
- `//` begins a comment. Everything following on that line is ignored
- Numeric literals are always written with Western Arabic digits (0-9). Negative number literals are written with a minus sign immediately preceding the digits with no whitespace — e.g. `-15`, `-0.5`
- `(` and `)` are grouping delimiters valid in math expressions. They carry no structural meaning outside expression contexts
- Date literals use the format `YYYY-MM-DD`. Time literals use the format `HH:MI:SS`
- Comparison and math symbol forms (`+`, `-`, `=`, `>`, etc.) are universal and require no binding

---

## Part II: Vocabulary Bindings

A vocabulary binding is a complete mapping from every invariant token to a word or phrase in the target language. The mapping must be:

- **Total** — every token must have a mapping
- **Injective** — no two tokens may share the same mapped word
- **Imperative** — mapped words should be imperative mood where grammatically appropriate
- **Minimal** — prefer single words; multi-word mappings are permitted where single words do not exist

Compound operators (`IS_EQUAL_TO_KW`, `IS_IN_KW`, `NOT_IN_KW`, etc.) may be mapped to multi-word phrases. The parser treats each compound as a single atomic token.

Symbol forms (`+`, `-`, `*`, `/`, `=`, `!=`, `>`, `<`, `>=`, `<=`) are identical in all bindings and do not appear in the mapping table.

`VERN_KW` maps to the file extension `.vern` in all bindings. It is a structural descriptor, not a keyword the user types as a standalone word — it always appears as `.vern` appended to a filename in a reference chain. It requires no translation.

File extension descriptors for non-VERN file types (`txt`, `json`, `csv`, `xml`, `ini`, `html`, `md`, `log`, `yaml`, `yml`, `toml`, `sql`, `png`, `jpg`, `jpeg`, `gif`, `webp`, `svg`, `ico`, `pdf`, `mp3`, `wav`, `mp4`, `mov`, `webm`, `zip`) follow the same rule — they are structural descriptors in the reference chain, not standalone keywords, and require no translation in any binding.

---

### Binding 1: English

```
Token                              English Keyword
-------------------------------------------------
SHOW_KW                            show
ASK_KW                             ask
READ_KW                            read
WRITE_KW                           write
APPEND_KW                          append
SET_KW                             set
TO_KW                              to
FROM_KW                            from
IF_KW                              if
THEN_KW                            then
WHILE_KW                           while
REPEAT_KW                          repeat
TIMES_KW                           times
THROUGH_KW                         through
END_KW                             end
STOP_KW                            stop
START_KW                           start
AT_KW                              at
RUN_KW                             run
DEFINE_KW                          define
AS_KW                              as
SCRIPT_KW                          script
OTHERWISE_KW                       otherwise
AND_KW                             and
OR_KW                              or
NOT_KW                             not
IS_EQUAL_TO_KW                     is equal to
IS_NOT_KW                          is not
IS_GREATER_THAN_KW                 is greater than
IS_LESS_THAN_KW                    is less than
IS_GREATER_THAN_OR_EQUAL_TO_KW     is greater than or equal to
IS_LESS_THAN_OR_EQUAL_TO_KW        is less than or equal to
IS_IN_KW                           is in
NOT_IN_KW                          not in
ADD_KW                             add
SUBTRACT_KW                        subtract
MULTIPLY_KW                        multiply
DIVIDE_KW                          divide
POWER_KW                           power
ROOT_KW                            root
REMAINDER_KW                       remainder
TRUE_KW                            true
FALSE_KW                           false
CONVERT_KW                         convert
NUMBER_KW                          number
TEXT_KW                            text
DATE_KW                            date
TIME_KW                            time
RETURN_KW                          return
PASS_KW                            pass
LOOP_KW                            loop
CURRENT_ITEM_KW                    current item
IMPORT_KW                          import
LIST_KW                            list
PUT_KW                             put
IN_KW                              in
REMOVE_KW                          remove
GET_KW                             get
COUNT_KW                           count
ROUND_KW                           round
FLOOR_KW                           floor
CEILING_KW                         ceiling
RANDOM_KW                          random
ABSOLUTE_KW                        absolute
MINIMUM_KW                         minimum
MAXIMUM_KW                         maximum
PERCENT_KW                         percent
OF_KW                              of
LENGTH_KW                          length
FIND_KW                            find
EXTRACT_KW                         extract
BEGINNING_KW                       beginning
FINISHING_KW                       finishing
REPLACE_KW                         replace
WITH_KW                            with
ATTEMPT_KW                         attempt
ALL_KW                             all
FAIL_KW                            fail
FAIL_REASON_KW                     fail reason
DIFFERENCE_KW                      difference
BETWEEN_KW                         between
DAYS_KW                            days
HOURS_KW                           hours
MINUTES_KW                         minutes
FORMAT_KW                          format
USING_KW                           using
EXIST_KW                           exist
DELETE_KW                          delete
FILES_KW                           files
FOLDER_KW                          folder
PARENT_KW                          parent
SINE_KW                            sine
COSINE_KW                          cosine
TANGENT_KW                         tangent
ARCSINE_KW                         arcsine
ARCCOSINE_KW                       arccosine
ARCTANGENT_KW                      arctangent
HYPERBOLIC_KW                      hyperbolic
ARC_KW                             arc
LN_KW                              ln
LOG_KW                             log
BASE_KW                            base
PI_KW                              pi
E_KW                               e
TAU_KW                             tau
INFINITY_KW                        infinity
DEGREES_KW                         degrees
RADIANS_KW                         radians
SUM_KW                             sum
FACTORIAL_KW                       factorial
COMBINATIONS_KW                    combinations
PERMUTATIONS_KW                    permutations
SIGN_KW                            sign
EXIT_KW                            exit
NEXT_KW                            next
ITEM_KW                            item
BY_KW                              by
SPLIT_KW                           split
JOIN_KW                            join
TRIM_KW                            trim
UPPERCASE_KW                       uppercase
LOWERCASE_KW                       lowercase
STARTS_WITH_KW                     starts with
ENDS_WITH_KW                       ends with
SORT_KW                            sort
DESCENDING_KW                      descending
REVERSE_KW                         reverse
SLICE_KW                           slice
COMBINE_KW                         combine
DICTIONARY_KW                      dictionary
KEY_KW                             key
CURRENT_KEY_KW                     current key
CURRENT_VALUE_KW                   current value
TAKES_KW                           takes
TYPEOF_KW                          type of
DECIMALS_KW                        decimals
THOUSANDS_KW                       thousands
PADDED_KW                          padded
TEXT_BLOCK_KW                      text
FETCH_KW                           fetch
SEND_KW                            send
NONE_KW                            none
PATH_KW                            path
INVOKE_KW                          invoke
UPDATE_KW                          update
HEADERS_KW                         headers
STATUS_KW                          status
RESPONSE_KW                        response
PARSE_KW                           parse
INSPECT_KW                         inspect
JSON_KW                            json
CSV_KW                             csv
XML_KW                             xml
INI_KW                             ini
FAIL_TYPE_KW                       fail type
WAIT_KW                            wait
CYCLE_KW                           cycle
RESET_KW                           reset
KEEP_KW                            keep
SERVE_KW                           serve
ROUTE_KW                           route
RESPOND_KW                         respond
REQUEST_BODY_KW                    request body
REQUEST_PATH_KW                    request path
REQUEST_HEADERS_KW                 request headers
REQUEST_METHOD_KW                  request method
FILE_KW                            file
LAUNCH_KW                          launch
SECONDS_KW                         seconds
MILLISECONDS_KW                    milliseconds
```

---

### Binding 2: Swahili

Swahili is a Bantu language spoken by over 200 million people across East and Central Africa. It uses Latin script, left-to-right, with agglutinative morphology. Imperative forms are typically bare verb stems.

```
Token                              Swahili Keyword
--------------------------------------------------
SHOW_KW                            onyesha
ASK_KW                             uliza
READ_KW                            soma
WRITE_KW                           andika
APPEND_KW                          ongeza
SET_KW                             weka
TO_KW                              kwa
FROM_KW                            kutoka
IF_KW                              ikiwa
THEN_KW                            basi
WHILE_KW                           wakati
REPEAT_KW                          rudia
TIMES_KW                           mara
THROUGH_KW                         kupitia
END_KW                             mwisho
STOP_KW                            simama
START_KW                           anza
AT_KW                              katika
RUN_KW                             endesha
DEFINE_KW                          fafanua
AS_KW                              kama
SCRIPT_KW                          hati
OTHERWISE_KW                       vinginevyo
AND_KW                             na
OR_KW                              au
NOT_KW                             si
IS_EQUAL_TO_KW                     ni sawa na
IS_NOT_KW                          si sawa na
IS_GREATER_THAN_KW                 ni kubwa kuliko
IS_LESS_THAN_KW                    ni ndogo kuliko
IS_GREATER_THAN_OR_EQUAL_TO_KW     ni kubwa au sawa na
IS_LESS_THAN_OR_EQUAL_TO_KW        ni ndogo au sawa na
IS_IN_KW                           ipo katika
NOT_IN_KW                          haipo katika
ADD_KW                             jumlisha
SUBTRACT_KW                        toa
MULTIPLY_KW                        zidisha
DIVIDE_KW                          gawanya
POWER_KW                           nguvu
ROOT_KW                            mzizi
REMAINDER_KW                       mabaki
TRUE_KW                            kweli
FALSE_KW                           uongo
CONVERT_KW                         badilisha
NUMBER_KW                          nambari
TEXT_KW                            maandishi
DATE_KW                            tarehe
TIME_KW                            muda
RETURN_KW                          rudisha
PASS_KW                            peleka
LOOP_KW                            mzunguko
CURRENT_ITEM_KW                    kipande cha sasa
IMPORT_KW                          ingiza
LIST_KW                            orodha
PUT_KW                             weka ndani
IN_KW                              ndani
REMOVE_KW                          ondoa
GET_KW                             pata
COUNT_KW                           hesabu
ROUND_KW                           karibisho
FLOOR_KW                           chini
CEILING_KW                         juu
RANDOM_KW                          nasibu
ABSOLUTE_KW                        thamani halisi
MINIMUM_KW                         ndogo zaidi
MAXIMUM_KW                         kubwa zaidi
PERCENT_KW                         asilimia
OF_KW                              ya
LENGTH_KW                          urefu
FIND_KW                            tafuta
EXTRACT_KW                         toa sehemu
BEGINNING_KW                       mwanzo
FINISHING_KW                       mwisho wa
REPLACE_KW                         geuza
WITH_KW                            pamoja
ATTEMPT_KW                         jaribu
ALL_KW                             yote
FAIL_KW                            kushindwa
FAIL_REASON_KW                     sababu ya kushindwa
DIFFERENCE_KW                      tofauti
BETWEEN_KW                         kati ya
DAYS_KW                            siku
HOURS_KW                           masaa
MINUTES_KW                         dakika
FORMAT_KW                          umbizo
USING_KW                           kwa kutumia
EXIST_KW                           ipo
DELETE_KW                          futa
FILES_KW                           faili
FOLDER_KW                          folda
PARENT_KW                          mzizi wa mfumo
SINE_KW                            sinusi
COSINE_KW                          kosinusi
TANGENT_KW                         tanjenti
ARCSINE_KW                         arkisinusi
ARCCOSINE_KW                       arkikosinusi
ARCTANGENT_KW                      arkitanjenti
HYPERBOLIC_KW                      hiperboliki
ARC_KW                             arki
LN_KW                              logariti asili
LOG_KW                             logariti
BASE_KW                            msingi
PI_KW                              pai
E_KW                               e
TAU_KW                             tau
INFINITY_KW                        usio na kikomo
DEGREES_KW                         digrii
RADIANS_KW                         radiani
SUM_KW                             jumla
FACTORIAL_KW                       faktoria
COMBINATIONS_KW                    mchanganyiko
PERMUTATIONS_KW                    mpangilio
SIGN_KW                            ishara
EXIT_KW                            toka
NEXT_KW                            ifuatayo
ITEM_KW                            kipande
BY_KW                              kwa kipande
SPLIT_KW                           gawanya maandishi
JOIN_KW                            unganisha
TRIM_KW                            kata nafasi
UPPERCASE_KW                       herufi kubwa
LOWERCASE_KW                       herufi ndogo
STARTS_WITH_KW                     inaanza na
ENDS_WITH_KW                       inaishia na
SORT_KW                            panga
DESCENDING_KW                      kushuka
REVERSE_KW                         geuza mpangilio
SLICE_KW                           kata sehemu
COMBINE_KW                         unganisha orodha
DICTIONARY_KW                      kamusi
KEY_KW                             ufunguo
CURRENT_KEY_KW                     ufunguo wa sasa
CURRENT_VALUE_KW                   thamani ya sasa
TAKES_KW                           inachukua
TYPEOF_KW                          aina ya
DECIMALS_KW                        desimali
THOUSANDS_KW                       maelfu
PADDED_KW                          pamba
TEXT_BLOCK_KW                      maandishi
FETCH_KW                           pakua
SEND_KW                            tuma
NONE_KW                            tupu
PATH_KW                            njia
INVOKE_KW                          tekeleza
UPDATE_KW                          sasisha
HEADERS_KW                         vichwa
STATUS_KW                          hali
RESPONSE_KW                        jibu
PARSE_KW                           changanua
INSPECT_KW                         kagua
JSON_KW                            json
CSV_KW                             csv
XML_KW                             xml
INI_KW                             ini
FAIL_TYPE_KW                       aina ya kushindwa
WAIT_KW                            subiri
CYCLE_KW                           zungusha
RESET_KW                           anza upya
KEEP_KW                            hifadhi
SERVE_KW                           hudumia
ROUTE_KW                           elekeza
RESPOND_KW                         jibu
REQUEST_BODY_KW                    mwili wa ombi
REQUEST_PATH_KW                    njia ya ombi
REQUEST_HEADERS_KW                 vichwa vya ombi
REQUEST_METHOD_KW                  njia ya HTTP
FILE_KW                            faili
LAUNCH_KW                          anzisha
SECONDS_KW                         sekunde
MILLISECONDS_KW                    millisekunde
```

---

### Binding 3: Japanese

Japanese is a Japonic language spoken by approximately 125 million people. It uses a combination of three scripts — hiragana, katakana, and kanji — written left-to-right in modern usage. Japanese word order is SOV (subject-object-verb), but VERN's keyword-driven imperative structure maps naturally to Japanese imperative verb forms.

```
Token                              Japanese Keyword       Romaji
---------------------------------------------------------------
SHOW_KW                            表示する               hyōji suru
ASK_KW                             入力する               nyūryoku suru
READ_KW                            読む                   yomu
WRITE_KW                           書く                   kaku
APPEND_KW                          追加する               tsuika suru
SET_KW                             設定する               settei suru
TO_KW                              に                     ni
FROM_KW                            から                   kara
IF_KW                              もし                   moshi
THEN_KW                            ならば                 naraba
WHILE_KW                           間                     あいだ (aida)
REPEAT_KW                          繰り返す               kurikaesu
TIMES_KW                           回                     kai
THROUGH_KW                         通して                 tōshite
END_KW                             終わり                 owari
STOP_KW                            止める                 tomeru
START_KW                           開始する               kaishi suru
AT_KW                              で                     de
RUN_KW                             実行する               jikkō suru
DEFINE_KW                          定義する               teigi suru
AS_KW                              として                 toshite
SCRIPT_KW                          スクリプト             sukuriputo
OTHERWISE_KW                       そうでなければ         sō de nakereba
AND_KW                             かつ                   katsu
OR_KW                              または                 matawa
NOT_KW                             でない                 de nai
IS_EQUAL_TO_KW                     と等しい               to hitoshii
IS_NOT_KW                          と等しくない           to hitoshikunai
IS_GREATER_THAN_KW                 より大きい             yori ōkii
IS_LESS_THAN_KW                    より小さい             yori chīsai
IS_GREATER_THAN_OR_EQUAL_TO_KW     以上                   ijō
IS_LESS_THAN_OR_EQUAL_TO_KW        以下                   ika
IS_IN_KW                           に含まれる             ni fukumareru
NOT_IN_KW                          に含まれない           ni fukumarenai
ADD_KW                             足す                   tasu
SUBTRACT_KW                        引く                   hiku
MULTIPLY_KW                        掛ける                 kakeru
DIVIDE_KW                          割る                   waru
POWER_KW                           乗                     jō
ROOT_KW                            根                     kon
REMAINDER_KW                       余り                   amari
TRUE_KW                            真                     shin
FALSE_KW                           偽                     gi
CONVERT_KW                         変換する               henkan suru
NUMBER_KW                          数字                   sūji
TEXT_KW                            テキスト               tekisuto
DATE_KW                            日付                   hizuke
TIME_KW                            時刻                   jikoku
RETURN_KW                          返す                   kaesu
PASS_KW                            渡す                   watasu
LOOP_KW                            ループ                 rūpu
CURRENT_ITEM_KW                    現在の項目             genzai no kōmoku
IMPORT_KW                          読み込む               yomikomi
LIST_KW                            リスト                 risuto
PUT_KW                             入れる                 ireru
IN_KW                              の中に                 no naka ni
REMOVE_KW                          削除する               sakujo suru
GET_KW                             取得する               shutoku suru
COUNT_KW                           数える                 kazoeru
ROUND_KW                           丸める                 marumeru
FLOOR_KW                           切り捨て               kirisute
CEILING_KW                         切り上げ               kiriage
RANDOM_KW                          乱数                   ransū
ABSOLUTE_KW                        絶対値                 zettaichi
MINIMUM_KW                         最小                   saisho
MAXIMUM_KW                         最大                   saidai
PERCENT_KW                         パーセント             pāsento
OF_KW                              の                     no
LENGTH_KW                          長さ                   nagasa
FIND_KW                            探す                   sagasu
EXTRACT_KW                         抽出する               chūshutsu suru
BEGINNING_KW                       始め                   hajime
FINISHING_KW                       終点                   shūten
REPLACE_KW                         置き換える             okikaeru
WITH_KW                            と                     to
ATTEMPT_KW                         試みる                 kokoromiru
ALL_KW                             すべて                 subete
FAIL_KW                            失敗                   shippai
FAIL_REASON_KW                     失敗の理由             shippai no riyū
DIFFERENCE_KW                      差                     sa
BETWEEN_KW                         の間                   no aida
DAYS_KW                            日                     nichi
HOURS_KW                           時間                   jikan
MINUTES_KW                         分                     fun
FORMAT_KW                          書式設定               shoshiki settei
USING_KW                           を使って               wo tsukatte
EXIST_KW                           存在する               sonzai suru
DELETE_KW                          消去する               shōkyo suru
FILES_KW                           ファイル               fairu
FOLDER_KW                          フォルダ               foruda
PARENT_KW                          ルート                 rūto
SINE_KW                            サイン                 sain
COSINE_KW                          コサイン               kosain
TANGENT_KW                         タンジェント           tanjento
ARCSINE_KW                         逆サイン               gyaku sain
ARCCOSINE_KW                       逆コサイン             gyaku kosain
ARCTANGENT_KW                      逆タンジェント         gyaku tanjento
HYPERBOLIC_KW                      双曲線                 sōkyokusen
ARC_KW                             逆双曲線               gyaku sōkyokusen
LN_KW                              自然対数               shizen taisū
LOG_KW                             対数                   taisū
BASE_KW                            底                     tei
PI_KW                              円周率                 enshūritsu
E_KW                               e                      e
TAU_KW                             タウ                   tau
INFINITY_KW                        無限大                 mugendai
DEGREES_KW                         度                     do
RADIANS_KW                         ラジアン               rajian
SUM_KW                             合計                   gōkei
FACTORIAL_KW                       階乗                   kaijō
COMBINATIONS_KW                    組合せ                 kumiawase
PERMUTATIONS_KW                    順列                   junretsu
SIGN_KW                            符号                   fugō
EXIT_KW                            抜ける                 nukeru
NEXT_KW                            次の                   tsugi no
ITEM_KW                            項目                   kōmoku
BY_KW                              区切り                 kukiri
SPLIT_KW                           分割する               bunkatsu suru
JOIN_KW                            結合する               ketsugō suru
TRIM_KW                            空白除去               kūhaku jokyo
UPPERCASE_KW                       大文字にする           ōmoji ni suru
LOWERCASE_KW                       小文字にする           komoji ni suru
STARTS_WITH_KW                     で始まる               de hajimaru
ENDS_WITH_KW                       で終わる               de owaru
SORT_KW                            並べ替える             narabaekaeru
DESCENDING_KW                      降順                   kōjun
REVERSE_KW                         逆順にする             gyakujun ni suru
SLICE_KW                           切り出す               kiridasu
COMBINE_KW                         連結する               renketsu suru
DICTIONARY_KW                      辞書                   jisho
KEY_KW                             キー                   kī
CURRENT_KEY_KW                     現在のキー             genzai no kī
CURRENT_VALUE_KW                   現在の値               genzai no atai
TAKES_KW                           受け取る               uketoru
TYPEOF_KW                          型を確認する           kata wo kakunin suru
DECIMALS_KW                        小数点以下             shōsūten ika
THOUSANDS_KW                       千の位                 sen no kurai
PADDED_KW                          埋める                 umeru
TEXT_BLOCK_KW                      テキストブロック       tekisuto burokku
FETCH_KW                           取得する               shutoku suru
SEND_KW                            送信する               sōshin suru
NONE_KW                            なし                   nashi
PATH_KW                            パス                   pasu
INVOKE_KW                          呼び出す               yobidasu
UPDATE_KW                          更新する               kōshin suru
HEADERS_KW                         ヘッダー               heddā
STATUS_KW                          状態                   jōtai
RESPONSE_KW                        レスポンス             resupонsu
PARSE_KW                           解析する               kaiseki suru
INSPECT_KW                         検査する               kensa suru
JSON_KW                            json
CSV_KW                             csv
XML_KW                             xml
INI_KW                             ini
FAIL_TYPE_KW                       失敗の種類             shippai no shurui
WAIT_KW                            待機する               taiki suru
CYCLE_KW                           循環する               junkan suru
RESET_KW                           初期化する             shokika suru
KEEP_KW                            保持する               hoji suru
SERVE_KW                           提供する               teikyō suru
ROUTE_KW                           経路設定する           keiro settei suru
RESPOND_KW                         応答する               ōtō suru
REQUEST_BODY_KW                    リクエスト本文         rikuesuto honbun
REQUEST_PATH_KW                    リクエストパス         rikuesuto pasu
REQUEST_HEADERS_KW                 リクエストヘッダー     rikuesuto heddā
REQUEST_METHOD_KW                  リクエスト方法         rikuesuto hōhō
FILE_KW                            ファイル               fairu
LAUNCH_KW                          起動する               kidō suru
SECONDS_KW                         秒                     byō
MILLISECONDS_KW                    ミリ秒                 miri-byō
```

---

### Binding 4: Arabic

Arabic is a Semitic language spoken by over 300 million people across North Africa and the Middle East. It uses Arabic script, written right-to-left. Arabic has a rich root-based morphology — most words derive from three-letter roots. Imperative forms are well-defined and unambiguous in Arabic.

Note on directionality: VERN's one-instruction-per-line constraint accommodates RTL script naturally. The parser reads tokens positionally regardless of script direction. An Arabic VERN file is written right-to-left as is natural for Arabic; the token sequence maps to the same invariant grammar positions.

```
Token                              Arabic Keyword         Transliteration
------------------------------------------------------------------------
SHOW_KW                            اعرض                   aʿriḍ
ASK_KW                             اسأل                   isʾal
READ_KW                            اقرأ                   iqraʾ
WRITE_KW                           اكتب                   uktub
APPEND_KW                          ألحق                   alḥiq
SET_KW                             اضبط                   iḍbaṭ
TO_KW                              إلى                    ilā
FROM_KW                            من                     min
IF_KW                              إذا                    idhā
THEN_KW                            فإن                    fa-inna
WHILE_KW                           بينما                  baynamā
REPEAT_KW                          كرر                    karrir
TIMES_KW                           مرات                   marrāt
THROUGH_KW                         عبر                    ʿabr
END_KW                             نهاية                  nihāya
STOP_KW                            أوقف                   awqif
START_KW                           ابدأ                   ibdaʾ
AT_KW                              عند                    ʿinda
RUN_KW                             شغّل                   shaggil
DEFINE_KW                          عرّف                   ʿarrif
AS_KW                              بوصفه                  bi-waṣfihi
SCRIPT_KW                          سكريبت                 skrībt
OTHERWISE_KW                       وإلا                   wa-illā
AND_KW                             و                      wa
OR_KW                              أو                     aw
NOT_KW                             ليس                    laysa
IS_EQUAL_TO_KW                     يساوي                  yusāwī
IS_NOT_KW                          لا يساوي               lā yusāwī
IS_GREATER_THAN_KW                 أكبر من                akbar min
IS_LESS_THAN_KW                    أصغر من                aṣghar min
IS_GREATER_THAN_OR_EQUAL_TO_KW     أكبر من أو يساوي       akbar min aw yusāwī
IS_LESS_THAN_OR_EQUAL_TO_KW        أصغر من أو يساوي       aṣghar min aw yusāwī
IS_IN_KW                           موجود في               mawjūd fī
NOT_IN_KW                          غير موجود في           ghayr mawjūd fī
ADD_KW                             أضف                    aḍif
SUBTRACT_KW                        اطرح                   iṭraḥ
MULTIPLY_KW                        اضرب                   iḍrib
DIVIDE_KW                          اقسم                   iqsim
POWER_KW                           قوة                    quwwa
ROOT_KW                            جذر                    jadhr
REMAINDER_KW                       باقي                   bāqī
TRUE_KW                            صحيح                   ṣaḥīḥ
FALSE_KW                           خطأ                    khaṭaʾ
CONVERT_KW                         حوّل                   ḥawwil
NUMBER_KW                          رقم                    raqm
TEXT_KW                            نص                     naṣṣ
DATE_KW                            تاريخ                  tārīkh
TIME_KW                            وقت                    waqt
RETURN_KW                          أرجع                   arjiʿ
PASS_KW                            مرر                    marrir
LOOP_KW                            دورة                   dawra
CURRENT_ITEM_KW                    العنصر الحالي          al-ʿunṣur al-ḥālī
IMPORT_KW                          استورد                 istawrid
LIST_KW                            قائمة                  qāʾima
PUT_KW                             ضع                     ḍaʿ
IN_KW                              في                     fī
REMOVE_KW                          احذف                   iḥdhif
GET_KW                             احصل على               iḥṣul ʿalā
COUNT_KW                           عدّ                    ʿudd
ROUND_KW                           قرّب                   qarrib
FLOOR_KW                           أنزل                   anzil
CEILING_KW                         أصعد                   aṣʿid
RANDOM_KW                          عشوائي                 ʿashwāʾī
ABSOLUTE_KW                        القيمة المطلقة         al-qīma al-muṭlaqa
MINIMUM_KW                         الأدنى                 al-adnā
MAXIMUM_KW                         الأقصى                 al-aqṣā
PERCENT_KW                         نسبة مئوية             nisba miʾawiyya
OF_KW                              لـ                     li
LENGTH_KW                          طول                    ṭūl
FIND_KW                            ابحث                   ibḥath
EXTRACT_KW                         استخرج                 istakhrij
BEGINNING_KW                       بداية                  bidāya
FINISHING_KW                       اكتمال                 iktimāl
REPLACE_KW                         استبدل                 istabdil
WITH_KW                            بـ                     bi-
ATTEMPT_KW                         حاول                   ḥāwil
ALL_KW                             الكل                   al-kull
FAIL_KW                            فشل                    fashal
FAIL_REASON_KW                     سبب الفشل              sabab al-fashal
DIFFERENCE_KW                      الفرق                  al-farq
BETWEEN_KW                         بين                    bayna
DAYS_KW                            أيام                   ayyām
HOURS_KW                           ساعات                  sāʿāt
MINUTES_KW                         دقائق                  daqāʾiq
FORMAT_KW                          نسّق                   nassiq
USING_KW                           باستخدام               bi-istikhdam
EXIST_KW                           متاح                   mutāḥ
DELETE_KW                          امسح                   imḥi
FILES_KW                           ملفات                  malaffāt
FOLDER_KW                          مجلد                   mijlad
PARENT_KW                          الجذر                  al-jadhr
SINE_KW                            جيب                    jayb
COSINE_KW                          جيب التمام             jayb al-tamām
TANGENT_KW                         ظل                     ẓill
ARCSINE_KW                         قوس الجيب              qaws al-jayb
ARCCOSINE_KW                       قوس جيب التمام         qaws jayb al-tamām
ARCTANGENT_KW                      قوس الظل               qaws al-ẓill
HYPERBOLIC_KW                      زائدي                  zāʾidī
ARC_KW                             قوس                    qaws
LN_KW                              لوغاريتم طبيعي         lūghārītm ṭabīʿī
LOG_KW                             لوغاريتم               lūghārītm
BASE_KW                            أساس                   asās
PI_KW                              باي                    bāy
E_KW                               e                      e
TAU_KW                             تاو                    tāw
INFINITY_KW                        لانهاية                lā nihāya
DEGREES_KW                         درجات                  darajāt
RADIANS_KW                         راديان                 rādiyān
SUM_KW                             مجموع                  majmūʿ
FACTORIAL_KW                       مضروب                  maḍrūb
COMBINATIONS_KW                    توافيق                 tawāfīq
PERMUTATIONS_KW                    تباديل                 tabādīl
SIGN_KW                            إشارة                  ishāra
EXIT_KW                            اخرج                   ukhruj
NEXT_KW                            التالي                 al-tālī
ITEM_KW                            عنصر                   ʿunṣur
BY_KW                              بفاصل                  bi-fāṣil
SPLIT_KW                           قسّم                   qassim
JOIN_KW                            ادمج                   idmij
TRIM_KW                            أزل المسافات           azil al-masāfāt
UPPERCASE_KW                       حروف كبيرة             ḥurūf kabīra
LOWERCASE_KW                       حروف صغيرة             ḥurūf ṣaghīra
STARTS_WITH_KW                     يبدأ بـ                yabdaʾ bi-
ENDS_WITH_KW                       ينتهي بـ               yantahī bi-
SORT_KW                            رتّب                   rattib
DESCENDING_KW                      تنازلي                 tanāzulī
REVERSE_KW                         اعكس                   iʿkis
SLICE_KW                           استخرج جزء             istakhrij juzʾ
COMBINE_KW                         ادمج قائمة             idmij qāʾima
DICTIONARY_KW                      قاموس                  qāmūs
KEY_KW                             مفتاح                  miftāḥ
CURRENT_KEY_KW                     المفتاح الحالي         al-miftāḥ al-ḥālī
CURRENT_VALUE_KW                   القيمة الحالية         al-qīma al-ḥāliyya
TAKES_KW                           يأخذ                   yaʾkhudh
TYPEOF_KW                          نوع                    nawʿ
DECIMALS_KW                        عشريات                 ʿashariyyāt
THOUSANDS_KW                       آلاف                   ālāf
PADDED_KW                          محشو                   maḥshū
TEXT_BLOCK_KW                      نص مطوّل               naṣṣ muṭawwal
FETCH_KW                           جلب                    jalab
SEND_KW                            أرسل                   arsil
NONE_KW                            لا شيء                 lā shayʾ
PATH_KW                            مسار                   masār
INVOKE_KW                          استدعِ                 istadʿi
UPDATE_KW                          حدّث                   ḥaddith
HEADERS_KW                         ترويسات                tarwīsāt
STATUS_KW                          حالة                   ḥāla
RESPONSE_KW                        استجابة                istijāba
PARSE_KW                           حلّل                   ḥallil
INSPECT_KW                         افحص                   ifḥaṣ
JSON_KW                            json
CSV_KW                             csv
XML_KW                             xml
INI_KW                             ini
FAIL_TYPE_KW                       نوع الفشل              nawʿ al-fashal
WAIT_KW                            انتظر                  intaẓir
CYCLE_KW                           دوّر                   dawwir
RESET_KW                           أعد الضبط              aʿid al-ḍabṭ
KEEP_KW                            احتفظ                  iḥtafiẓ
SERVE_KW                           قدّم                   qaddim
ROUTE_KW                           وجّه                   wajjih
RESPOND_KW                         استجب                  istajibb
REQUEST_BODY_KW                    جسم الطلب              jism al-ṭalab
REQUEST_PATH_KW                    مسار الطلب             masār al-ṭalab
REQUEST_HEADERS_KW                 ترويسات الطلب          tarwīsāt al-ṭalab
REQUEST_METHOD_KW                  طريقة الطلب            ṭarīqat al-ṭalab
FILE_KW                            ملف                    malaf
LAUNCH_KW                          شغّل                   shaggil
SECONDS_KW                         ثوانٍ                  thawānin
MILLISECONDS_KW                    ميلي ثانية             milli thāniya
```

---

## Part III: The Binding Contract

Any new vocabulary binding for VERN must satisfy the following requirements to be considered a valid VERN binding:

### Required

1. **Complete mapping** — every token in the invariant token list must have exactly one mapped keyword or phrase in the target language

2. **No collisions** — no two tokens may share the same mapped keyword. If a target language uses the same word for two different concepts, one must be disambiguated

3. **Imperative mood** — keywords should use imperative verb forms where the target language has them

4. **Unicode compliance** — all keywords must be valid Unicode

5. **Symbol preservation** — the symbol forms (`+`, `-`, `*`, `/`, `=`, `!=`, `>`, `<`, `>=`, `<=`, `.`, `#`, `"`, `,`, `//`, `(`, `)`) are identical in all bindings and are not localized

6. **Semantic equivalence** — a program written in any binding must execute identically to the same program written in any other binding. The binding changes the words, not the behavior

### Recommended

7. **Cultural mapping via `define`** — bindings are encouraged to include a standard library of `define` extensions mapping culturally native concepts to VERN operations

8. **Bidirectional support** — the binding table should support both directions: human language → invariant token (for parsing) and invariant token → human language (for error messages and output)

---

## Part IV: What This Architecture Is Not

To establish clear boundaries for the prior art claim:

**This is not internationalization (i18n)** — i18n translates user interface elements while keeping code in English. VERN localizes the executable keywords themselves.

**This is not localization (l10n)** — l10n adapts regional formats (dates, currencies, number separators). VERN's binding system operates at the level of executable syntax, not formatting.

**This is not a domain-specific language (DSL)** — DSLs provide specialized vocabulary within a single language (usually English). VERN provides a general-purpose grammar that any language can instantiate.

**This is not a transliteration system** — transliteration maps one script to another phonetically. VERN bindings map computational concepts to native language equivalents semantically.

**This is not machine translation** — machine translation converts text from one language to another. VERN programs in different bindings are not translations of each other; they are independent expressions of the same invariant grammar.

The specific claim is: **a general-purpose imperative programming grammar in which the executable vocabulary is the localization target, implemented through a total, injective keyword mapping that preserves execution semantics across all bindings.**

---

*End of Document*
*The VERN Project — 2026*
