# VERN Invariant Grammar Specification v0.2
## Universal Imperative Grammar with Vocabulary Bindings

**Document Version:** 2.0
**Date:** 2026-06-02
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
8. **Two reserved symbols only** — `.` for containment hierarchy, `#` for container tags

### Abstract Syntax

The following notation uses invariant token names in ALL CAPS. These are not English words — they are abstract labels for grammar positions. Each is replaced by a vocabulary binding's equivalent word or phrase.

```
PROGRAM ::= (IMPORT | FILE_VALUE | LIST | CONTAINER | SCRIPT | COMMENT)* [ENTRY_POINT] [STOP]

IMPORT ::= IMPORT_KW REFERENCE

FILE_VALUE ::= SET_KW REFERENCE TO_KW EXPRESSION
             | DEFINE_KW TEXT AS_KW RUN_KW REFERENCE

LIST ::= LIST_KW IDENTIFIER (REFERENCE)?
         VALUE*
         END_KW LIST_KW

CONTAINER ::= HASH IDENTIFIER
              (SET_KW REFERENCE TO_KW VALUE)*

SCRIPT ::= SCRIPT_HEADER [CONTAINER_TAG] INSTRUCTION* END_SCRIPT
SCRIPT_HEADER ::= SCRIPT_KW REFERENCE
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

SHOW_INSTRUCTION   ::= SHOW_KW (REFERENCE | VALUE) (SEPARATOR (REFERENCE | VALUE))*
ASK_INSTRUCTION    ::= ASK_KW REFERENCE
READ_INSTRUCTION   ::= READ_KW REFERENCE (SEPARATOR REFERENCE)* FROM_KW REFERENCE
WRITE_INSTRUCTION  ::= WRITE_KW REFERENCE (SEPARATOR REFERENCE)* TO_KW REFERENCE
APPEND_INSTRUCTION ::= APPEND_KW REFERENCE (SEPARATOR REFERENCE)* TO_KW REFERENCE
SET_INSTRUCTION    ::= SET_KW REFERENCE TO_KW EXPRESSION
IF_INSTRUCTION     ::= IF_KW CONDITION THEN_KW INSTRUCTION
IF_BLOCK_INSTRUCTION ::= IF_KW CONDITION INSTRUCTION* END_IF
END_IF             ::= END_KW IF_KW
RUN_INSTRUCTION    ::= RUN_KW REFERENCE [CONTAINER_TAG]
STOP_INSTRUCTION   ::= STOP_KW

CONVERT_INSTRUCTION ::= CONVERT_KW (REFERENCE | LOOP_KW | CURRENT_ITEM_KW) TO_KW TYPE_KW AS_KW REFERENCE
TYPE_KW ::= NUMBER_KW | TEXT_KW

RETURN_INSTRUCTION ::= RETURN_KW REFERENCE PASS_KW TO_KW REFERENCE

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

ATTEMPT_INSTRUCTION ::= ATTEMPT_KW [ALL_KW] INSTRUCTION* IF_FAIL INSTRUCTION* END_FAIL END_ATTEMPT
IF_FAIL     ::= IF_KW FAIL_KW
END_FAIL    ::= END_KW FAIL_KW
END_ATTEMPT ::= END_KW ATTEMPT_KW

CONDITION ::= EXPRESSION COMPARISON_OP EXPRESSION
            | NOT_KW CONDITION
            | CONDITION AND_KW CONDITION
            | CONDITION OR_KW CONDITION
            | EXPRESSION IS_IN_KW LIST_KW LIST_REF
            | EXPRESSION NOT_IN_KW LIST_KW LIST_REF
            | EXPRESSION IS_IN_KW REFERENCE
            | EXPRESSION NOT_IN_KW REFERENCE

EXPRESSION ::= VALUE
             | REFERENCE
             | LOOP_KW
             | CURRENT_ITEM_KW
             | FAIL_REASON_KW
             | EXPRESSION MATH_OP EXPRESSION
             | EXPRESSION POWER_KW NUMBER
             | EXPRESSION ROOT_KW NUMBER
             | EXPRESSION REMAINDER_KW EXPRESSION

REFERENCE ::= PERIOD IDENTIFIER (PERIOD IDENTIFIER)* [CONTAINER_TAG]
CONTAINER_REF ::= HASH IDENTIFIER (PERIOD IDENTIFIER)*

VALUE ::= TEXT | NUMBER | BOOLEAN | DATE_LITERAL | TIME_LITERAL
TEXT ::= DOUBLE_QUOTE CHARACTER* DOUBLE_QUOTE
NUMBER ::= DIGIT+ (PERIOD DIGIT+)?
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
| `REPEAT_KW` | begin loop |
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
| `RETURN_KW` | return a value from a script |
| `PASS_KW` | pass to destination marker |
| `LOOP_KW` | implicit loop counter (read-only, inside repeat only) |
| `IMPORT_KW` | load an external file |
| `LIST_KW` | list identifier |
| `PUT_KW` | add item to list |
| `IN_KW` | list insertion / text search marker |
| `IS_IN_KW` | membership check (compound) |
| `NOT_IN_KW` | negative membership check (compound) |
| `REMOVE_KW` | remove item from list |
| `THROUGH_KW` | list iteration marker |
| `GET_KW` | retrieve by position or system value |
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
| `DATE_KW` | date type / get current date |
| `TIME_KW` | time type / get current time |
| `DIFFERENCE_KW` | date/time difference |
| `BETWEEN_KW` | difference range marker |
| `DAYS_KW` | days unit |
| `HOURS_KW` | hours unit |
| `MINUTES_KW` | minutes unit |
| `FORMAT_KW` | format date/time for display |
| `USING_KW` | format pattern marker |

### Invariant Properties

These properties are non-negotiable across all bindings:

- `.` is the sole containment hierarchy symbol. User-defined names are always prefixed with `.`
- `#` is the container tag symbol. Container names are always prefixed with `#`
- `"` delimits text literals. Text literals are not localized
- `,` is the value separator in multi-value instructions
- `//` begins a comment. Everything following on that line is ignored
- Numeric literals are always written with Western Arabic digits (0-9)
- Date literals use the format `YYYY-MM-DD`. Time literals use the format `HH:MM:SS`
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
DATE_KW                            date
TIME_KW                            time
DIFFERENCE_KW                      difference
BETWEEN_KW                         between
DAYS_KW                            days
HOURS_KW                           hours
MINUTES_KW                         minutes
FORMAT_KW                          format
USING_KW                           using
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
DATE_KW                            tarehe
TIME_KW                            wakati
DIFFERENCE_KW                      tofauti
BETWEEN_KW                         kati ya
DAYS_KW                            siku
HOURS_KW                           masaa
MINUTES_KW                         dakika
FORMAT_KW                          umbizo
USING_KW                           kwa kutumia
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
DATE_KW                            日付                   hizuke
TIME_KW                            時刻                   jikoku
DIFFERENCE_KW                      差                     sa
BETWEEN_KW                         の間                   no aida
DAYS_KW                            日                     nichi
HOURS_KW                           時間                   jikan
MINUTES_KW                         分                     fun
FORMAT_KW                          書式設定               shoshiki settei
USING_KW                           を使って               wo tsukatte
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
DATE_KW                            تاريخ                  tārīkh
TIME_KW                            وقت                    waqt
DIFFERENCE_KW                      الفرق                  al-farq
BETWEEN_KW                         بين                    bayna
DAYS_KW                            أيام                   ayyām
HOURS_KW                           ساعات                  sāʿāt
MINUTES_KW                         دقائق                  daqāʾiq
FORMAT_KW                          نسّق                   nassiq
USING_KW                           باستخدام               bi-istikhdam
```

---

## Part III: The Binding Contract

Any new vocabulary binding for VERN must satisfy the following requirements to be considered a valid VERN binding:

### Required

1. **Complete mapping** — every token in the invariant token list must have exactly one mapped keyword or phrase in the target language

2. **No collisions** — no two tokens may share the same mapped keyword. If a target language uses the same word for two different concepts, one must be disambiguated

3. **Imperative mood** — keywords should use imperative verb forms where the target language has them

4. **Unicode compliance** — all keywords must be valid Unicode

5. **Symbol preservation** — the symbol forms (`+`, `-`, `*`, `/`, `=`, `!=`, `>`, `<`, `>=`, `<=`, `.`, `#`, `"`, `,`, `//`) are identical in all bindings and are not localized

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
