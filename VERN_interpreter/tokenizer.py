#!/usr/bin/env python3
"""
VERN Language Tokenizer — English binding, v0.6 spec.

Usage:
    python tokenizer.py <file.vern>

Produces one token per line to stdout: line_number  TOKEN_TYPE  value
"""

import re
import sys
from dataclasses import dataclass
from typing import List, Optional, Tuple


# ── Token ──────────────────────────────────────────────────────────────────────

@dataclass
class Token:
    type: str
    value: str
    line: int

    def __repr__(self) -> str:
        return f"Token({self.type:<35} {self.value!r:<30} line={self.line})"


class TokenizeError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"Line {line}: {message}")
        self.line = line


# ── Compound keywords ──────────────────────────────────────────────────────────
# Ordered longest-first so greedy matching always picks the right one.
# Each entry: (lowercase phrase, TOKEN_TYPE)

COMPOUND_KEYWORDS: List[Tuple[str, str]] = [
    # Comparison operators — the spec explicitly calls these atomic compounds
    ("is greater than or equal to", "IS_GREATER_THAN_OR_EQUAL_TO"),
    ("is less than or equal to",    "IS_LESS_THAN_OR_EQUAL_TO"),
    ("is greater than",             "IS_GREATER_THAN"),
    ("is less than",                "IS_LESS_THAN"),
    ("is equal to",                 "IS_EQUAL_TO"),
    ("is not",                      "IS_NOT"),
    ("is in",                       "IS_IN"),
    ("not in",                      "NOT_IN"),

    # Hyperbolic trig — arc must come before hyperbolic
    ("arc hyperbolic sine",         "ARC_HYPERBOLIC_SINE"),
    ("arc hyperbolic cosine",       "ARC_HYPERBOLIC_COSINE"),
    ("arc hyperbolic tangent",      "ARC_HYPERBOLIC_TANGENT"),
    ("hyperbolic sine",             "HYPERBOLIC_SINE"),
    ("hyperbolic cosine",           "HYPERBOLIC_COSINE"),
    ("hyperbolic tangent",          "HYPERBOLIC_TANGENT"),

    # Implicit read-only keywords
    ("current item",                "CURRENT_ITEM"),
    ("current key",                 "CURRENT_KEY"),
    ("current value",               "CURRENT_VALUE"),
    ("fail reason",                 "FAIL_REASON"),

    # Loop control compounds
    ("exit loop",                   "EXIT_LOOP"),
    ("next item",                   "NEXT_ITEM"),

    # String condition compounds
    ("starts with",                 "STARTS_WITH"),
    ("ends with",                   "ENDS_WITH"),

    # Block keywords — `end` is only valid as part of these
    ("end script",                  "END_SCRIPT"),
    ("end list",                    "END_LIST"),
    ("end dictionary",              "END_DICTIONARY"),
    ("end repeat",                  "END_REPEAT"),
    ("end while",                   "END_WHILE"),
    ("end if",                      "END_IF"),
    ("end attempt",                 "END_ATTEMPT"),
    ("end fail",                    "END_FAIL"),
    ("end text",                    "END_TEXT"),

    # Error recovery keywords
    ("if fail",                     "IF_FAIL"),
    ("attempt all",                 "ATTEMPT_ALL"),

    # Typed failure info
    ("fail type",                   "FAIL_TYPE"),

    # Response headers (networking)
    ("response headers",            "RESPONSE_HEADERS"),

    # Entry point
    ("start at",                    "START_AT"),

    # Iteration
    ("repeat through",              "REPEAT_THROUGH"),

    # Type and length queries
    ("type of",                     "TYPE_OF"),
    ("length of",                   "LENGTH_OF"),

    # Angle conversion instructions (line-opening position only)
    ("to degrees",                  "TO_DEGREES"),
    ("to radians",                  "TO_RADIANS"),

    # Date/time arithmetic separator
    ("difference between",          "DIFFERENCE_BETWEEN"),

    # Script return target
    ("pass to",                     "PASS_TO"),
]

# ── Single reserved keywords ───────────────────────────────────────────────────
# Maps lowercase word → TOKEN_TYPE (uppercase form of the word).
# Components of compound operators that have no standalone validity are included
# so the tokenizer emits a keyword rather than an identifier; the parser
# enforces that they only appear in their compound contexts.

SINGLE_KEYWORDS: dict = {w: w.upper() for w in [
    "set", "to", "show", "ask", "read", "write", "append", "from",
    "if", "then", "repeat", "times", "stop", "start", "at",
    "run", "define", "as", "script", "and", "or", "not",
    "true", "false",
    "add", "subtract", "multiply", "divide",
    "convert", "number", "text",
    "return", "pass", "loop",
    "import",
    "list", "put", "in", "remove", "through", "get",
    "current", "item", "count",
    "round", "floor", "ceiling",
    "power", "root", "remainder", "random", "absolute",
    "minimum", "maximum", "percent", "of",
    "find", "extract", "replace", "with", "beginning", "finishing",
    "attempt", "fail", "reason",
    "date", "time",
    "difference", "between", "days", "hours", "minutes",
    "format", "using",
    "while", "otherwise",
    "exist", "delete", "files", "folder", "parent",
    "sine", "cosine", "tangent", "arcsine", "arccosine", "arctangent",
    "hyperbolic", "arc",
    "ln", "log", "base",
    "pi", "e", "tau", "infinity",
    "degrees", "radians",
    "sum", "factorial", "combinations", "permutations", "sign",
    "exit", "next",
    "by", "split", "join", "trim", "uppercase", "lowercase",
    "starts", "ends",
    "ascending", "descending",
    "sort", "reverse", "slice", "combine",
    "dictionary", "key", "value",
    "takes",
    "type",
    "fetch", "send",
    "decimals", "thousands", "padded",
    "end",
    # Phase 1 additions
    "none",
    "invoke",
    # Phase 2 additions
    "path",
    "update",
    "headers", "status", "response",
    "parse", "inspect",
    "json", "csv", "xml", "ini",
    # Phase 3 additions (v0.7.5)
    "wait", "cycle", "reset", "keep",
    "serve", "route", "respond", "request", "launch",
    "seconds", "milliseconds",
    # Implicit components of compound comparison operators — reserved but
    # only valid inside their compounds; listed here so they tokenize
    # as keywords rather than identifiers.
    "is", "equal", "greater", "less", "than",
]}

# ── Regex patterns ─────────────────────────────────────────────────────────────

_RE_WS       = re.compile(r'\s+')
# Reference chain: .name or .name.other.vern etc.
# Each segment: letter then letters/digits/underscores (underscore-leading invalid).
_RE_REF      = re.compile(r'\.[a-zA-Z][a-zA-Z0-9_]*(?:\.[a-zA-Z][a-zA-Z0-9_]*)*')
# Container tag: #name  (same identifier rules)
_RE_CTAG     = re.compile(r'#[a-zA-Z][a-zA-Z0-9_]*')
# Date: YYYY-MM-DD  (requires a non-digit after to avoid matching longer seqs)
_RE_DATE     = re.compile(r'\d{4}-\d{2}-\d{2}(?!\d)')
# Time: HH:MI:SS
_RE_TIME     = re.compile(r'\d{2}:\d{2}:\d{2}(?!\d)')
# Number: integer or decimal
_RE_NUM      = re.compile(r'\d+(?:\.\d+)?')
# A bare word: letter then letters/digits/underscores (underscore-leading invalid).
_RE_WORD     = re.compile(r'[a-zA-Z][a-zA-Z0-9_]*')

# Symbol tokens — longer symbols tried before shorter
_SYMBOLS: List[Tuple[str, str]] = [
    (">=", "GTE"),
    ("<=", "LTE"),
    ("!=", "NEQ"),
    (">",  "GT"),
    ("<",  "LT"),
    ("=",  "EQ"),
    ("+",  "PLUS"),
    ("-",  "MINUS"),
    ("*",  "STAR"),
    ("/",  "SLASH"),
    (",",  "COMMA"),
    (":",  "COLON"),
]


# ── Comment stripping ──────────────────────────────────────────────────────────

def _strip_comment(line: str) -> str:
    """Return the portion of line before any // that is not inside a string."""
    in_string = False
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == '"':
            in_string = not in_string
        elif not in_string and ch == '/' and i + 1 < len(line) and line[i + 1] == '/':
            return line[:i]
        i += 1
    return line


# ── Compound keyword matcher ───────────────────────────────────────────────────

def _match_compound(text: str, pos: int) -> Optional[Tuple[str, str]]:
    """
    Try each compound keyword phrase against text[pos:] (case-insensitive).
    Returns (TOKEN_TYPE, matched_text) for the first match whose end is at a
    word boundary (next char is not alphanumeric), or None.
    """
    lower = text.lower()
    for phrase, tok_type in COMPOUND_KEYWORDS:
        end = pos + len(phrase)
        if lower[pos:end] == phrase:
            # Word boundary: end of string, or next char is not alnum/underscore
            if end >= len(text) or not (text[end].isalnum()):
                return tok_type, text[pos:end]
    return None


# ── Line tokenizer ─────────────────────────────────────────────────────────────

def _tokenize_line(text: str, line_no: int) -> List[Token]:
    """Tokenize one pre-stripped, comment-free line of VERN source."""
    tokens: List[Token] = []
    pos = 0
    n = len(text)

    while pos < n:
        # ── whitespace
        m = _RE_WS.match(text, pos)
        if m:
            pos = m.end()
            continue

        if pos >= n:
            break

        ch = text[pos]

        # ── text literal  "..."
        if ch == '"':
            end = pos + 1
            while end < n and text[end] != '"':
                end += 1
            if end >= n:
                raise TokenizeError("unterminated text literal", line_no)
            tokens.append(Token("TEXT_LITERAL", text[pos + 1:end], line_no))
            pos = end + 1
            continue

        # ── reference chain  .name or .name.other.vern
        if ch == '.' and pos + 1 < n and text[pos + 1].isalpha():
            m = _RE_REF.match(text, pos)
            if m:
                tokens.append(Token("REFERENCE", m.group(), line_no))
                pos = m.end()
                continue

        # ── container tag  #name
        if ch == '#':
            m = _RE_CTAG.match(text, pos)
            if m:
                tokens.append(Token("CONTAINER_TAG", m.group(), line_no))
                pos = m.end()
                continue
            raise TokenizeError(
                f"invalid container tag at '{text[pos:pos + 10].rstrip()}'",
                line_no,
            )

        # ── numeric literals — date and time tried before plain number
        if ch.isdigit():
            m = _RE_DATE.match(text, pos)
            if m:
                tokens.append(Token("DATE_LITERAL", m.group(), line_no))
                pos = m.end()
                continue

            m = _RE_TIME.match(text, pos)
            if m:
                tokens.append(Token("TIME_LITERAL", m.group(), line_no))
                pos = m.end()
                continue

            m = _RE_NUM.match(text, pos)
            if m:
                tokens.append(Token("NUMBER_LITERAL", m.group(), line_no))
                pos = m.end()
                continue

        # ── symbol operators
        matched_sym = False
        for sym, tok_type in _SYMBOLS:
            if text.startswith(sym, pos):
                tokens.append(Token(tok_type, sym, line_no))
                pos += len(sym)
                matched_sym = True
                break
        if matched_sym:
            continue

        # ── keywords (compound first for greedy match) and bare identifiers
        if ch.isalpha():
            result = _match_compound(text, pos)
            if result:
                tok_type, matched = result
                tokens.append(Token(tok_type, matched, line_no))
                pos += len(matched)
                continue

            m = _RE_WORD.match(text, pos)
            if m:
                word = m.group()
                lower_word = word.lower()
                if lower_word in SINGLE_KEYWORDS:
                    tokens.append(Token(SINGLE_KEYWORDS[lower_word], lower_word, line_no))
                else:
                    tokens.append(Token("IDENTIFIER", word, line_no))
                pos = m.end()
                continue

        raise TokenizeError(
            f"unexpected character {ch!r} at column {pos + 1}",
            line_no,
        )

    return tokens


# ── Full-source tokenizer ──────────────────────────────────────────────────────

def tokenize(source: str) -> List[Token]:
    """
    Tokenize a complete VERN source string.

    Handles:
    - Comment stripping (// not inside strings)
    - Text blocks (lines inside text...end text are emitted as TEXT_LINE tokens)
    - All reserved words, compound keywords, literals, and identifiers
    """
    all_tokens: List[Token] = []
    in_text_block = False

    for line_no, raw_line in enumerate(source.splitlines(), start=1):

        if in_text_block:
            # Inside a text block every line is raw content — check only for
            # the closing marker (case-insensitive, leading whitespace stripped)
            stripped = raw_line.strip()
            if stripped.lower() == "end text":
                all_tokens.append(Token("END_TEXT", "end text", line_no))
                in_text_block = False
            else:
                # Preserve content but strip cosmetic leading whitespace
                all_tokens.append(Token("TEXT_LINE", raw_line.lstrip(), line_no))
            continue

        # Strip comment and surrounding whitespace
        line = _strip_comment(raw_line).strip()
        if not line:
            continue

        line_tokens = _tokenize_line(line, line_no)
        if not line_tokens:
            continue

        # Detect opening of a text block: first token TEXT, second REFERENCE
        # e.g.  text .welcome
        if (len(line_tokens) >= 2
                and line_tokens[0].type == "TEXT"
                and line_tokens[1].type == "REFERENCE"):
            in_text_block = True

        all_tokens.extend(line_tokens)

    return all_tokens


# ── File helper ────────────────────────────────────────────────────────────────

def tokenize_file(path: str) -> List[Token]:
    """Read a .vern file and return its token stream."""
    with open(path, encoding="utf-8") as fh:
        return tokenize(fh.read())


# ── CLI entry point ────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python tokenizer.py <file.vern>", file=sys.stderr)
        sys.exit(1)

    path = sys.argv[1]
    try:
        tokens = tokenize_file(path)
    except TokenizeError as exc:
        print(f"Tokenize error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)

    for tok in tokens:
        print(f"  {tok.line:4d}  {tok.type:<35}  {tok.value!r}")


if __name__ == "__main__":
    main()
