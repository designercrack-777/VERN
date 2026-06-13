#!/usr/bin/env python3
"""
VERN Parser — v0.6 spec.
Consumes a token stream from tokenizer.py and produces an AST.

Run:
    python parser.py <file.vern>
"""

import sys, os, pprint
sys.path.insert(0, os.path.dirname(__file__))
from tokenizer import Token, tokenize, tokenize_file, TokenizeError
from ast_nodes import *


class ParseError(Exception):
    def __init__(self, message: str, line: int):
        super().__init__(f"Line {line}: {message}")
        self.line = line


# ── Comparison operator token types ───────────────────────────────────────────
_CMP_OPS = {
    "IS_EQUAL_TO", "IS_NOT", "IS_GREATER_THAN", "IS_LESS_THAN",
    "IS_GREATER_THAN_OR_EQUAL_TO", "IS_LESS_THAN_OR_EQUAL_TO",
    "EQ", "NEQ", "GT", "LT", "GTE", "LTE",
}

# Binary math operator token types → symbol string
_MATH_OPS = {
    "PLUS": "+", "MINUS": "-", "STAR": "*", "SLASH": "/",
    "ADD": "+", "SUBTRACT": "-", "MULTIPLY": "*", "DIVIDE": "/",
    "POWER": "power", "ROOT": "root", "REMAINDER": "remainder",
}

# Math constant token types
_CONSTANTS = {"PI", "E", "TAU", "INFINITY"}

# Trig functions (single-argument)
_TRIG_SINGLE = {
    "SINE": "sine", "COSINE": "cosine", "TANGENT": "tangent",
    "ARCSINE": "arcsine", "ARCCOSINE": "arccosine", "ARCTANGENT": "arctangent",
    "HYPERBOLIC_SINE": "hyperbolic sine",
    "HYPERBOLIC_COSINE": "hyperbolic cosine",
    "HYPERBOLIC_TANGENT": "hyperbolic tangent",
    "ARC_HYPERBOLIC_SINE": "arc hyperbolic sine",
    "ARC_HYPERBOLIC_COSINE": "arc hyperbolic cosine",
    "ARC_HYPERBOLIC_TANGENT": "arc hyperbolic tangent",
}


class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
        self._in_script = False   # detect nested script defs

    # ── Cursor helpers ─────────────────────────────────────────────────────────

    def _peek(self, offset: int = 0) -> Optional[Token]:
        i = self.pos + offset
        return self.tokens[i] if i < len(self.tokens) else None

    def _advance(self) -> Token:
        t = self.tokens[self.pos]
        self.pos += 1
        return t

    def _check(self, *types: str) -> bool:
        t = self._peek()
        return t is not None and t.type in types

    def _match(self, *types: str) -> Optional[Token]:
        if self._check(*types):
            return self._advance()
        return None

    def _expect(self, *types: str) -> Token:
        t = self._peek()
        if t is None:
            raise ParseError(f"The program ended unexpectedly. {' or '.join(types)} was expected next.", -1)
        if t.type not in types:
            raise ParseError(
                f"'{t.value}' cannot appear here. {' or '.join(types)} was expected.",
                t.line,
            )
        return self._advance()

    def _line(self) -> int:
        t = self._peek()
        return t.line if t else -1

    def _same_line(self, line_no: int) -> bool:
        t = self._peek()
        return t is not None and t.line == line_no

    # ── Expression parsing ─────────────────────────────────────────────────────

    def _parse_atom(self) -> Any:
        """Parse a single value atom."""
        t = self._peek()
        if t is None:
            raise ParseError("The program ended unexpectedly. A value reference was expected here.", -1)
        line = t.line

        if t.type == "REFERENCE":
            self._advance()
            # check for inline container tag on same line
            tag = None
            ct = self._peek()
            if ct and ct.type == "CONTAINER_TAG" and ct.line == line:
                self._advance()
                tag = ct.value
            return ValueRef(ref=t.value, container=tag, line=line)

        if t.type == "TEXT_LITERAL":
            self._advance()
            return TextLit(value=t.value, line=line)

        if t.type == "NUMBER_LITERAL":
            self._advance()
            return NumberLit(value=t.value, line=line)

        if t.type == "DATE_LITERAL":
            self._advance()
            return DateLit(value=t.value, line=line)

        if t.type == "TIME_LITERAL":
            self._advance()
            return TimeLit(value=t.value, line=line)

        if t.type == "TRUE":
            self._advance()
            return BoolLit(value=True, line=line)

        if t.type == "FALSE":
            self._advance()
            return BoolLit(value=False, line=line)

        if t.type in _CONSTANTS:
            self._advance()
            return Constant(name=t.value, line=line)

        if t.type == "LOOP":
            self._advance()
            return LoopVar(line=line)

        if t.type == "CURRENT_ITEM":
            self._advance()
            return CurrentItem(line=line)

        if t.type == "CURRENT_KEY":
            self._advance()
            return CurrentKey(line=line)

        if t.type == "CURRENT_VALUE":
            self._advance()
            return CurrentValue(line=line)

        if t.type == "FAIL_REASON":
            self._advance()
            return FailReason(line=line)

        if t.type == "FAIL_TYPE":
            self._advance()
            return FailType(line=line)

        if t.type == "NONE":
            self._advance()
            return NoneLit(line=line)

        if t.type == "REQUEST":
            self._advance()
            attr_t = self._peek()
            if attr_t is None or attr_t.line != line:
                raise ParseError(
                    "'request' must be followed by 'body', 'path', 'headers', or 'method' on the same line.",
                    line)
            if attr_t.type == "PATH":
                self._advance()
                return RequestRef(attribute='path', line=line)
            elif attr_t.type == "HEADERS":
                self._advance()
                return RequestRef(attribute='headers', line=line)
            elif attr_t.type == "IDENTIFIER" and attr_t.value.lower() == "body":
                self._advance()
                return RequestRef(attribute='body', line=line)
            elif attr_t.type == "IDENTIFIER" and attr_t.value.lower() == "method":
                self._advance()
                return RequestRef(attribute='method', line=line)
            else:
                raise ParseError(
                    f"'{attr_t.value}' is not a valid request attribute. "
                    f"Use 'request body', 'request path', 'request headers', or 'request method'.", line)

        if t.type == "LPAREN":
            paren_line = t.line
            self._advance()
            if self._check("RPAREN"):
                raise ParseError(
                    "Empty parentheses '()' are not valid. An expression is required inside.",
                    paren_line)
            inner = self._parse_expr(line_no=paren_line)
            rp = self._peek()
            if rp is None or rp.type != "RPAREN":
                raise ParseError(
                    "An opening parenthesis '(' was not matched with a closing ')'. "
                    "Add the missing closing parenthesis.",
                    paren_line)
            self._advance()
            return inner

        if t.type == "RPAREN":
            raise ParseError(
                "An unexpected closing parenthesis ')' was found. "
                "Check that all opening parentheses are matched.",
                t.line)

        raise ParseError(f"'{t.value}' cannot be used as a value here.", line)

    def _parse_expr(self, line_no: Optional[int] = None) -> Any:
        """
        Parse an expression: atom [binop atom ...] (left-associative).
        Stops when no binary operator follows, or the next token is on a
        different line than `line_no` (when supplied).
        """
        left = self._parse_atom()
        start_line = line_no if line_no is not None else left.line

        while True:
            t = self._peek()
            if t is None:
                break
            if t.line != start_line:
                break
            if t.type not in _MATH_OPS:
                break
            op_tok = self._advance()
            op = _MATH_OPS[op_tok.type]
            right = self._parse_atom()
            left = BinOp(left=left, op=op, right=right, line=op_tok.line)

        return left

    # ── Condition parsing ──────────────────────────────────────────────────────

    def _parse_condition(self, line_no: int) -> Any:
        """Parse a condition expression (may contain and/or), all on line_no."""
        cond = self._parse_simple_cond(line_no)

        while self._same_line(line_no):
            t = self._peek()
            if t is None:
                break
            if t.type == "AND":
                self._advance()
                right = self._parse_simple_cond(line_no)
                cond = AndCond(left=cond, right=right, line=t.line)
            elif t.type == "OR":
                self._advance()
                right = self._parse_simple_cond(line_no)
                cond = OrCond(left=cond, right=right, line=t.line)
            else:
                break

        return cond

    def _parse_simple_cond(self, line_no: int) -> Any:
        """Parse one comparison/membership/exist/starts_with/ends_with/not cond."""
        t = self._peek()
        if t is None:
            raise ParseError("The program ended unexpectedly. A condition was expected here.", -1)
        line = t.line

        # not <cond>
        if t.type == "NOT":
            self._advance()
            inner = self._parse_simple_cond(line_no)
            return NotCond(cond=inner, line=line)

        # Dynamic file exist check: path .value exist
        if t.type == "PATH":
            self._advance()
            ref = self._parse_value_ref()
            t2 = self._peek()
            if t2 and t2.type == "EXIST" and t2.line == line_no:
                self._advance()
                return PathExistCheck(ref=ref, line=line)
            raise ParseError("'path' in an 'if' statement must be followed by 'exist'. Write: 'if path .filename exist'.", line)

        # not in used as prefix check — already handled by tokenizer as NOT_IN
        # so we won't see bare NOT here for membership

        # Parse LHS atom/expr
        left = self._parse_atom()

        t = self._peek()
        if t is None or t.line != line_no:
            # standalone bool or ref
            return left

        # is in / not in / is_equal_to / is_not / comparisons
        if t.type in _CMP_OPS:
            op_tok = self._advance()
            right = self._parse_atom()
            return Comparison(left=left, op=op_tok.type, right=right, line=line)

        if t.type == "IS_IN":
            self._advance()
            return self._parse_membership(left, negated=False, line=line)

        if t.type == "NOT_IN":
            self._advance()
            return self._parse_membership(left, negated=True, line=line)

        if t.type == "STARTS_WITH":
            self._advance()
            pattern = self._parse_atom()
            return StartsWithCond(ref=left, pattern=pattern, line=line)

        if t.type == "ENDS_WITH":
            self._advance()
            pattern = self._parse_atom()
            return EndsWithCond(ref=left, pattern=pattern, line=line)

        if t.type == "EXIST":
            self._advance()
            return ExistCheck(ref=left, line=line)

        # Bare bool/ref used as condition
        return left

    def _parse_membership(self, value: Any, negated: bool, line: int) -> MemberCheck:
        """After 'is in' or 'not in', parse collection specifier."""
        t = self._peek()
        if t is None:
            raise ParseError("'is in' and 'not in' must be followed by 'list', 'dictionary', or a value reference.", line)

        if t.type == "LIST":
            self._advance()
            name = self._expect("IDENTIFIER").value
            file_ref = self._parse_optional_file_ref(t.line)
            return MemberCheck(value=value, negated=negated,
                               collection_kind="list", collection=name,
                               file_ref=file_ref, line=line)

        if t.type == "DICTIONARY":
            self._advance()
            name = self._expect("IDENTIFIER").value
            return MemberCheck(value=value, negated=negated,
                               collection_kind="dictionary", collection=name,
                               file_ref=None, line=line)

        if t.type == "REFERENCE":
            ref = self._parse_value_ref()
            return MemberCheck(value=value, negated=negated,
                               collection_kind="text", collection=ref,
                               file_ref=None, line=line)

        raise ParseError(f"'{t.value}' cannot follow a membership check. Use 'list', 'dictionary', or a value reference.", line)

    def _parse_value_ref(self) -> ValueRef:
        """Parse a REFERENCE token — no inline container tag.

        Container tags on run/script instructions are consumed by those
        instruction parsers. Only _parse_atom consumes inline tags in
        expression (show/set) contexts.
        """
        t = self._expect("REFERENCE")
        return ValueRef(ref=t.value, container=None, line=t.line)

    def _parse_optional_file_ref(self, base_line: int) -> Optional[ValueRef]:
        """If the next token is a REFERENCE on the same line, return it."""
        t = self._peek()
        if t and t.type == "REFERENCE" and t.line == base_line:
            # Only consume it if it looks like a cross-file ref (.name.vern)
            if ".vern" in t.value:
                return self._parse_value_ref()
        return None

    # ── Comma-separated value list ─────────────────────────────────────────────

    def _parse_value_list(self, line_no: int) -> List[Any]:
        """Parse one or more comma-separated expressions on line_no."""
        items = [self._parse_expr(line_no)]
        while self._same_line(line_no) and self._check("COMMA"):
            self._advance()
            items.append(self._parse_expr(line_no))
        return items

    # ── Instruction dispatcher ─────────────────────────────────────────────────

    def _parse_instruction(self, allow_file_level: bool = False) -> Any:
        """Parse one instruction and return its AST node."""
        t = self._peek()
        if t is None:
            raise ParseError("The program ended unexpectedly. An instruction was expected here.", -1)
        line = t.line
        tt = t.type

        # ── Script definition (file-level only) ────────────────────────────────
        if tt == "SCRIPT":
            if self._in_script and not allow_file_level:
                raise ParseError("Scripts cannot be defined inside other scripts. Move this script definition to the file level.", line)
            return self._parse_script_def()

        # ── Container definition (file-level only) ─────────────────────────────
        if tt == "CONTAINER_TAG" and allow_file_level:
            return self._parse_container_def()

        # ── List declaration (file-level) ──────────────────────────────────────
        if tt == "LIST" and allow_file_level:
            return self._parse_list_decl()

        # ── Dictionary declaration (file-level) ────────────────────────────────
        if tt == "DICTIONARY" and allow_file_level:
            # peek: if next is IDENTIFIER (not a reference), it's a declaration
            n = self._peek(1)
            if n and n.type == "IDENTIFIER":
                return self._parse_dict_decl()

        # ── Text block (file-level) ────────────────────────────────────────────
        if tt == "TEXT" and allow_file_level:
            n = self._peek(1)
            if n and n.type == "REFERENCE" and n.line == line:
                return self._parse_text_block()

        # ── Common instructions ────────────────────────────────────────────────
        dispatch = {
            "SET":                self._parse_set,
            "SHOW":               self._parse_show,
            "ASK":                self._parse_ask,
            "READ":               self._parse_read,
            "WRITE":              self._parse_write,
            "APPEND":             self._parse_append,
            "RUN":                self._parse_run,
            "RETURN":             self._parse_return,
            "CONVERT":            self._parse_convert,
            "TYPE_OF":            self._parse_type_of,
            "IF":                 self._parse_if,
            "IF_FAIL":            None,   # handled inside attempt
            "WHILE":              self._parse_while,
            "REPEAT":             self._parse_repeat,
            "REPEAT_THROUGH":     self._parse_repeat_through,
            "ATTEMPT":            self._parse_attempt,
            "ATTEMPT_ALL":        self._parse_attempt,
            "EXIT_LOOP":          lambda: ExitLoopInstr(line=self._advance().line),
            "NEXT_ITEM":          lambda: NextItemInstr(line=self._advance().line),
            "IMPORT":             self._parse_import,
            "STOP":               self._parse_stop,
            "START_AT":           self._parse_start_at,
            "DEFINE":             self._parse_define,
            "PUT":                self._parse_put,
            "REMOVE":             self._parse_remove,
            "GET":                self._parse_get,
            "COUNT":              self._parse_count,
            "SORT":               self._parse_sort,
            "REVERSE":            self._parse_reverse,
            "SLICE":              self._parse_slice,
            "COMBINE":            self._parse_combine,
            "ROUND":              self._parse_round,
            "FLOOR":              self._parse_floor,
            "CEILING":            self._parse_ceiling,
            "RANDOM":             self._parse_random,
            "ABSOLUTE":           self._parse_absolute,
            "MINIMUM":            lambda: self._parse_minmax("minimum"),
            "MAXIMUM":            lambda: self._parse_minmax("maximum"),
            "PERCENT":            self._parse_percent,
            "SUM":                self._parse_sum,
            "FACTORIAL":          self._parse_factorial,
            "COMBINATIONS":       self._parse_combinations,
            "PERMUTATIONS":       self._parse_permutations,
            "SIGN":               self._parse_sign,
            "SINE":               lambda: self._parse_trig("sine"),
            "COSINE":             lambda: self._parse_trig("cosine"),
            "TANGENT":            lambda: self._parse_trig("tangent"),
            "ARCSINE":            lambda: self._parse_trig("arcsine"),
            "ARCCOSINE":          lambda: self._parse_trig("arccosine"),
            "ARCTANGENT":         lambda: self._parse_trig("arctangent"),
            "HYPERBOLIC_SINE":    lambda: self._parse_trig("hyperbolic sine"),
            "HYPERBOLIC_COSINE":  lambda: self._parse_trig("hyperbolic cosine"),
            "HYPERBOLIC_TANGENT": lambda: self._parse_trig("hyperbolic tangent"),
            "ARC_HYPERBOLIC_SINE":    lambda: self._parse_trig("arc hyperbolic sine"),
            "ARC_HYPERBOLIC_COSINE":  lambda: self._parse_trig("arc hyperbolic cosine"),
            "ARC_HYPERBOLIC_TANGENT": lambda: self._parse_trig("arc hyperbolic tangent"),
            "LN":                 self._parse_ln,
            "LOG":                self._parse_log,
            "TO_DEGREES":         lambda: self._parse_angle_conv("degrees"),
            "TO_RADIANS":         lambda: self._parse_angle_conv("radians"),
            "LENGTH_OF":          self._parse_length_of,
            "FIND":               self._parse_find,
            "EXTRACT":            self._parse_extract,
            "REPLACE":            self._parse_replace,
            "SPLIT":              self._parse_split,
            "JOIN":               self._parse_join,
            "TRIM":               self._parse_trim,
            "UPPERCASE":          self._parse_uppercase,
            "LOWERCASE":          self._parse_lowercase,
            "FORMAT":             self._parse_format,
            "DIFFERENCE_BETWEEN": self._parse_difference_between,
            "DELETE":             self._parse_delete,
            "FETCH":              self._parse_fetch,
            "SEND":               self._parse_send,
            "UPDATE":             self._parse_update,
            "PARSE":              self._parse_parse,
            "INSPECT":            self._parse_inspect,
            "INVOKE":             self._parse_invoke,
            "WAIT":               self._parse_wait,
            "CYCLE":              self._parse_execution_mode,
            "SERVE":              self._parse_serve,
            "ROUTE":              self._parse_route,
            "RESPOND":            self._parse_respond,
            "LAUNCH":             self._parse_launch,
        }

        handler = dispatch.get(tt)
        if handler is None:
            raise ParseError(f"'{t.value}' is not a recognised instruction. Check the spelling or remove this line.", line)
        return handler()

    # ── File-level parse ───────────────────────────────────────────────────────

    def _parse_body(self, terminators: tuple) -> List[Any]:
        """
        Parse a sequence of instructions until one of the terminator token
        types appears (without consuming it), or end of input.

        When inside a script block (_in_script is True), END_SCRIPT is always
        treated as a body terminator regardless of the terminator set passed in.
        This ensures that inline if / then instructions inside a script never
        cause the closing end script to be consumed by an inner block parser
        whose terminator set does not include END_SCRIPT.  The token is left
        unconsumed so the enclosing _parse_script_def can expect and consume it.
        """
        body = []
        while True:
            t = self._peek()
            if t is None:
                break
            if t.type in terminators:
                break
            # Hard sentinel: when inside a script, END_SCRIPT must always stop
            # any nested body parse so the outer script body and _expect can
            # consume it at the right level.
            if self._in_script and t.type == "END_SCRIPT" and "END_SCRIPT" not in terminators:
                break
            body.append(self._parse_instruction())
        return body

    def parse_program(self) -> Program:
        """Parse a complete VERN program."""
        body = []
        while self._peek():
            t = self._peek()
            if t is None:
                break
            # File-level constructs
            body.append(self._parse_instruction(allow_file_level=True))
        return Program(body=body)

    # ── Script definition ──────────────────────────────────────────────────────

    def _parse_param(self) -> Any:
        """Parse one parameter in a takes clause.

        Accepts:
          - list name         → ("list", name)
          - dictionary name   → ("dict", name)
          - script name       → ("script", name)
          - .ref              → ValueRef (existing form)
        """
        t = self._peek()
        if t is None:
            raise ParseError("'takes' must be followed by one or more parameter names.", -1)
        if t.type == "LIST":
            self._advance()
            name = self._expect("IDENTIFIER").value
            return ("list", name)
        if t.type == "DICTIONARY":
            self._advance()
            name = self._expect("IDENTIFIER").value
            return ("dict", name)
        if t.type == "SCRIPT":
            self._advance()
            name = self._expect("IDENTIFIER").value
            return ("script", name)
        return self._parse_value_ref()

    def _parse_run_arg(self, line: int) -> Any:
        """Parse one argument in a run with clause.

        Accepts:
          - list name         → ("list", name)
          - dictionary name   → ("dict", name)
          - script .ref       → ("script", ValueRef)
          - any atom          → existing form
        """
        t = self._peek()
        if t is None:
            raise ParseError("'with' must be followed by one or more values to pass to the script.", -1)
        if t.type == "LIST":
            self._advance()
            name = self._expect("IDENTIFIER").value
            return ("list", name)
        if t.type == "DICTIONARY":
            self._advance()
            name = self._expect("IDENTIFIER").value
            return ("dict", name)
        if t.type == "SCRIPT":
            self._advance()
            ref = self._parse_value_ref()
            return ("script", ref)
        return self._parse_atom()

    def _parse_script_def(self) -> ScriptDef:
        line = self._peek().line
        self._expect("SCRIPT")
        name = self._parse_value_ref()

        params = []
        container = None

        # optional takes .p1, .p2  (or list/dict/script typed params)
        if self._same_line(line) and self._check("TAKES"):
            self._advance()
            params.append(self._parse_param())
            while self._same_line(line) and self._check("COMMA"):
                self._advance()
                params.append(self._parse_param())

        # optional container tag on same line
        if self._same_line(line) and self._check("CONTAINER_TAG"):
            container = self._advance().value

        old = self._in_script
        self._in_script = True
        body = self._parse_body(("END_SCRIPT",))
        self._in_script = old
        self._expect("END_SCRIPT")
        return ScriptDef(name=name, params=params, container=container,
                         body=body, line=line)

    # ── Container definition ───────────────────────────────────────────────────

    def _parse_container_def(self) -> ContainerDef:
        t = self._expect("CONTAINER_TAG")
        line = t.line
        tag = t.value
        # body: only SET instructions until next container, script, list, dict,
        # text block, stop, start_at, import, or end of input
        stop_at = {"CONTAINER_TAG", "SCRIPT", "LIST", "DICTIONARY",
                   "TEXT", "STOP", "START_AT", "IMPORT", "END_SCRIPT"}
        body = []
        while True:
            nt = self._peek()
            if nt is None or nt.type in stop_at:
                break
            node = self._parse_instruction()
            if not isinstance(node, SetInstr):
                raise ParseError(
                    "Containers may only contain 'set' instructions. Remove or move any other instruction.",
                    node.line,
                )
            body.append(node)
        return ContainerDef(tag=tag, body=body, line=line)

    # ── List declaration ───────────────────────────────────────────────────────

    def _parse_list_decl(self) -> ListDecl:
        line = self._peek().line
        self._expect("LIST")
        name = self._expect("IDENTIFIER").value

        # Optional cross-file ref
        file_ref = None
        if self._same_line(line) and self._check("REFERENCE"):
            t = self._peek()
            if t and ".vern" in t.value:
                file_ref = self._parse_value_ref()

        items = []
        while True:
            t = self._peek()
            if t is None or t.type == "END_LIST":
                break
            # Each item is on its own line; could be a literal or IDENTIFIER (dict ref)
            item_line = t.line
            if t.type == "IDENTIFIER":
                items.append(self._advance().value)
            elif t.type in ("TEXT_LITERAL", "NUMBER_LITERAL", "DATE_LITERAL",
                            "TIME_LITERAL", "TRUE", "FALSE", "NONE"):
                items.append(self._parse_atom())
            else:
                raise ParseError(
                    f"'{t.value}' is not a valid list item. List items must be text values in quotes, whole numbers, or names of declared dictionaries.",
                    item_line,
                )

        self._expect("END_LIST")
        return ListDecl(name=name, items=items, file_ref=file_ref, line=line)

    # ── Dictionary declaration ─────────────────────────────────────────────────

    def _parse_dict_decl(self) -> DictDecl:
        line = self._peek().line
        self._expect("DICTIONARY")
        name = self._expect("IDENTIFIER").value
        pairs = []
        while True:
            t = self._peek()
            if t is None or t.type == "END_DICTIONARY":
                break
            key = self._parse_atom()
            self._expect("COLON")
            # value can be a literal or an IDENTIFIER (dict reference)
            vt = self._peek()
            if vt and vt.type == "IDENTIFIER":
                value = self._advance().value
            else:
                value = self._parse_atom()
            pairs.append((key, value))
        self._expect("END_DICTIONARY")
        return DictDecl(name=name, pairs=pairs, line=line)

    # ── Text block declaration ─────────────────────────────────────────────────

    def _parse_text_block(self) -> TextBlockDecl:
        line = self._peek().line
        self._advance()   # TEXT keyword
        name = self._parse_value_ref()
        content = []
        while True:
            t = self._peek()
            if t is None or t.type == "END_TEXT":
                break
            if t.type == "TEXT_LINE":
                content.append(self._advance().value)
            else:
                break
        self._expect("END_TEXT")
        return TextBlockDecl(name=name, content_lines=content, line=line)

    # ── Basic I/O ──────────────────────────────────────────────────────────────

    def _parse_set(self) -> SetInstr:
        line = self._peek().line
        self._expect("SET")
        target = self._parse_value_ref()
        self._expect("TO")
        value = self._parse_expr(line)
        return SetInstr(target=target, value=value, line=line)

    def _parse_show(self) -> ShowInstr:
        line = self._peek().line
        self._expect("SHOW")
        values = self._parse_value_list(line)
        return ShowInstr(values=values, line=line)

    def _parse_ask(self) -> AskInstr:
        line = self._peek().line
        self._expect("ASK")
        target = self._parse_value_ref()
        return AskInstr(target=target, line=line)

    def _parse_read(self) -> ReadInstr:
        line = self._peek().line
        self._expect("READ")
        targets = [self._parse_value_ref()]
        while self._same_line(line) and self._check("COMMA"):
            self._advance()
            targets.append(self._parse_value_ref())
        self._expect("FROM")
        # Support: from path .ref (dynamic path)
        source_is_path = False
        if self._same_line(line) and self._check("PATH"):
            self._advance()
            source_is_path = True
        source = self._parse_value_ref()
        return ReadInstr(targets=targets, source=source,
                         source_is_path=source_is_path, line=line)

    def _parse_write(self) -> WriteInstr:
        line = self._peek().line
        self._expect("WRITE")
        values = self._parse_value_list(line)
        self._expect("TO")
        # Support: to path .ref (dynamic path)
        dest_is_path = False
        if self._same_line(line) and self._check("PATH"):
            self._advance()
            dest_is_path = True
        dest = self._parse_value_ref()
        return WriteInstr(values=values, dest=dest, dest_is_path=dest_is_path, line=line)

    def _parse_append(self) -> AppendInstr:
        line = self._peek().line
        self._expect("APPEND")
        values = self._parse_value_list(line)
        self._expect("TO")
        # Support: to path .ref (dynamic path)
        dest_is_path = False
        if self._same_line(line) and self._check("PATH"):
            self._advance()
            dest_is_path = True
        dest = self._parse_value_ref()
        return AppendInstr(values=values, dest=dest, dest_is_path=dest_is_path, line=line)

    # ── Run / return ───────────────────────────────────────────────────────────

    def _parse_run(self) -> RunInstr:
        line = self._peek().line
        self._expect("RUN")
        script = self._parse_value_ref()
        args = []
        container = None
        result_names = []
        if self._same_line(line) and self._check("WITH"):
            self._advance()
            args.append(self._parse_run_arg(line))
            while self._same_line(line) and self._check("COMMA"):
                self._advance()
                # Stop parsing args if we've hit a REFERENCE that looks like result
                # (we detect AS below)
                args.append(self._parse_run_arg(line))
        if self._same_line(line) and self._check("CONTAINER_TAG"):
            container = self._advance().value
        # Form 2: as .result [, .result2, ...]
        if self._same_line(line) and self._check("AS"):
            self._advance()
            result_names.append(self._parse_value_ref())
            while self._same_line(line) and self._check("COMMA"):
                self._advance()
                result_names.append(self._parse_value_ref())
        return RunInstr(script=script, args=args, container=container,
                        result_names=result_names, line=line)

    def _parse_invoke(self) -> InvokeInstr:
        """invoke script parametername [with args] [as .result]"""
        line = self._peek().line
        self._expect("INVOKE")
        self._expect("SCRIPT")
        param_name = self._expect("IDENTIFIER").value
        args = []
        result_names = []
        if self._same_line(line) and self._check("WITH"):
            self._advance()
            args.append(self._parse_run_arg(line))
            while self._same_line(line) and self._check("COMMA"):
                self._advance()
                args.append(self._parse_run_arg(line))
        if self._same_line(line) and self._check("AS"):
            self._advance()
            result_names.append(self._parse_value_ref())
            while self._same_line(line) and self._check("COMMA"):
                self._advance()
                result_names.append(self._parse_value_ref())
        return InvokeInstr(param_name=param_name, args=args,
                           result_names=result_names, line=line)

    def _parse_return(self) -> ReturnInstr:
        line = self._peek().line
        self._expect("RETURN")
        value = self._parse_atom()
        dest = None
        if self._same_line(line) and self._check("PASS_TO"):
            self._advance()
            dest = self._parse_value_ref()
        return ReturnInstr(value=value, dest=dest, line=line)

    # ── Type conversion ────────────────────────────────────────────────────────

    def _parse_convert(self) -> ConvertInstr:
        line = self._peek().line
        self._expect("CONVERT")
        # source can be a reference, loop, current item/key/value
        source = self._parse_atom()
        self._expect("TO")
        type_tok = self._expect("NUMBER", "TEXT", "DATE", "TIME")
        self._expect("AS")
        result = self._parse_value_ref()
        return ConvertInstr(source=source, target_type=type_tok.value,
                            result=result, line=line)

    def _parse_type_of(self) -> TypeOfInstr:
        line = self._peek().line
        self._expect("TYPE_OF")
        source = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return TypeOfInstr(source=source, result=result, line=line)

    # ── Conditionals ───────────────────────────────────────────────────────────

    def _parse_if(self) -> Any:
        line = self._peek().line
        self._expect("IF")

        # Determine inline vs block form by scanning ahead for THEN on the same
        # line *before* parsing the condition.  This must be done up front because
        # _parse_condition may not consume every token on the line (e.g. when the
        # condition contains arithmetic in the LHS/RHS), so checking for THEN
        # after the condition parse can give a false negative and silently
        # misidentify an inline if as a block if.
        #
        # THEN is a reserved keyword that cannot appear as a value or operator, so
        # any THEN token on the same line as `if` unambiguously signals inline form.
        is_inline = False
        for _off in range(len(self.tokens) - self.pos):
            _t = self._peek(_off)
            if _t is None or _t.line != line:
                break
            if _t.type == "THEN":
                is_inline = True
                break

        condition = self._parse_condition(line)

        if is_inline:
            self._expect("THEN")
            action = self._parse_instruction()
            return IfInline(condition=condition, action=action, line=line)

        # Block form
        then_body = self._parse_body(("END_IF", "OTHERWISE"))
        else_body = []
        if self._check("OTHERWISE"):
            self._advance()
            else_body = self._parse_body(("END_IF",))
        self._expect("END_IF")
        return IfBlock(condition=condition, then_body=then_body,
                       else_body=else_body, line=line)

    # ── While loop ─────────────────────────────────────────────────────────────

    def _parse_while(self) -> WhileBlock:
        line = self._peek().line
        self._expect("WHILE")
        condition = self._parse_condition(line)
        body = self._parse_body(("END_WHILE",))
        self._expect("END_WHILE")
        return WhileBlock(condition=condition, body=body, line=line)

    # ── Repeat loops ───────────────────────────────────────────────────────────

    def _parse_repeat(self) -> RepeatTimesBlock:
        line = self._peek().line
        self._expect("REPEAT")
        count = self._parse_atom()
        self._expect("TIMES")
        body = self._parse_body(("END_REPEAT",))
        self._expect("END_REPEAT")
        return RepeatTimesBlock(count=count, body=body, line=line)

    def _parse_repeat_through(self) -> Any:
        line = self._peek().line
        self._expect("REPEAT_THROUGH")
        t = self._peek()
        if t is None:
            raise ParseError("'repeat through' must be followed by 'list' or 'dictionary'.", line)

        if t.type == "LIST":
            self._advance()
            if self._check("REFERENCE"):
                name = self._parse_value_ref()  # variable holding a list
            else:
                name = self._expect("IDENTIFIER").value
            file_ref = self._parse_optional_file_ref(line)
            body = self._parse_body(("END_REPEAT",))
            self._expect("END_REPEAT")
            return RepeatThroughListBlock(list_name=name, file_ref=file_ref,
                                          body=body, line=line)

        if t.type == "DICTIONARY":
            self._advance()
            if self._check("REFERENCE"):
                name = self._parse_value_ref()  # variable holding a dict
            else:
                name = self._expect("IDENTIFIER").value
            file_ref = self._parse_optional_file_ref(line)
            body = self._parse_body(("END_REPEAT",))
            self._expect("END_REPEAT")
            return RepeatThroughDictBlock(dict_name=name, file_ref=file_ref,
                                          body=body, line=line)

        raise ParseError(f"'{t.value}' cannot follow 'repeat through'. Write 'repeat through list name' or 'repeat through dictionary name'.", line)

    # ── Attempt / error recovery ───────────────────────────────────────────────

    def _parse_attempt(self) -> AttemptBlock:
        line = self._peek().line
        tok = self._advance()  # ATTEMPT or ATTEMPT_ALL
        try_all = tok.type == "ATTEMPT_ALL"
        # attempt body — stops before the first if fail
        body = self._parse_body(("IF_FAIL",))
        typed_handlers = []
        fail_body = None
        # Parse zero or more typed handlers, then optional catch-all
        while self._check("IF_FAIL"):
            self._advance()  # consume IF_FAIL
            t = self._peek()
            if t and t.type == "TEXT_LITERAL":
                # Typed handler: if fail "category"
                category = self._advance().value
                handler_body = self._parse_body(("IF_FAIL", "END_FAIL"))
                typed_handlers.append((category, handler_body))
            else:
                # Bare catch-all handler
                fail_body = self._parse_body(("END_FAIL",))
                break  # catch-all must be last
        self._expect("END_FAIL")
        self._expect("END_ATTEMPT")
        return AttemptBlock(try_all=try_all, body=body,
                            typed_handlers=typed_handlers,
                            fail_body=fail_body, line=line)

    # ── Import / stop / start_at / define ─────────────────────────────────────

    def _parse_import(self) -> ImportInstr:
        line = self._peek().line
        self._expect("IMPORT")
        path = self._parse_value_ref()
        return ImportInstr(path=path, line=line)

    def _parse_start_at(self) -> StartAt:
        line = self._peek().line
        self._expect("START_AT")
        script = self._parse_value_ref()
        return StartAt(script=script, line=line)

    def _parse_stop(self) -> Any:
        """stop  |  stop .programname.vern"""
        line = self._advance().line   # consume STOP
        t = self._peek()
        # stop .programname.vern — inter-program stop signal
        if t and t.type == "REFERENCE" and t.line == line:
            ref_parts = [p for p in t.value.split('.') if p]
            if any(p in ALL_RECOGNIZED_EXTENSIONS for p in ref_parts):
                ref = self._parse_value_ref()
                return StopProgramInstr(target=ref, line=line)
        return StopInstr(line=line)

    def _parse_wait(self) -> Any:
        """wait N seconds | wait N milliseconds  — or — wait reset | wait keep (execution mode)."""
        line = self._peek().line
        t_next = self._peek(1)   # token after 'wait'
        if t_next and t_next.line == line and t_next.type == "NUMBER_LITERAL":
            self._advance()   # consume WAIT
            num_t = self._advance()   # consume number
            if '.' in num_t.value:
                raise ParseError("'wait' requires a whole number of seconds or milliseconds. Decimal values are not allowed.", line)
            duration = int(num_t.value)
            if duration <= 0:
                raise ParseError("'wait' requires a duration greater than zero.", line)
            unit_t = self._peek()
            if unit_t is None or unit_t.line != line or unit_t.type not in ("SECONDS", "MILLISECONDS"):
                raise ParseError(
                    f"'wait' requires a time unit. Write 'wait {duration} seconds' or 'wait {duration} milliseconds'.", line)
            unit = self._advance().value   # 'seconds' or 'milliseconds'
            return WaitInstr(duration=duration, unit=unit, line=line)
        # Fall through to execution mode (wait reset / wait keep)
        return self._parse_execution_mode()

    def _parse_execution_mode(self) -> ExecutionModeDecl:
        """wait reset | wait keep | cycle reset | cycle keep"""
        line = self._peek().line
        first = self._advance().value   # 'wait' or 'cycle'
        t = self._peek()
        if t is None or t.line != line or t.type not in ("RESET", "KEEP"):
            raise ParseError(
                f"'{first}' must be followed by 'reset' or 'keep' on the same line. Write '{first} reset' or '{first} keep'.",
                line)
        second = self._advance().value   # 'reset' or 'keep'
        return ExecutionModeDecl(mode=f"{first}_{second}", line=line)

    def _parse_serve(self) -> ServeDecl:
        """serve <port>"""
        line = self._advance().line   # consume SERVE
        port_t = self._expect("NUMBER_LITERAL")
        if '.' in port_t.value:
            raise ParseError("The port number after 'serve' must be a whole number, like 'serve 8080'.", line)
        return ServeDecl(port=int(port_t.value), line=line)

    def _parse_route(self) -> RouteDecl:
        """route "/path" to .script"""
        line = self._advance().line   # consume ROUTE
        path_t = self._expect("TEXT_LITERAL")
        self._expect("TO")
        script = self._parse_value_ref()
        return RouteDecl(path=path_t.value, script=script, line=line)

    def _parse_respond(self) -> RespondInstr:
        """respond [file [path] .ref | .value | "text"] [status N]"""
        line = self._advance().line   # consume RESPOND
        # respond file ...
        t = self._peek()
        if t and t.type == "IDENTIFIER" and t.value.lower() == "file" and t.line == line:
            self._advance()   # consume 'file'
            file_is_path = False
            if self._same_line(line) and self._check("PATH"):
                self._advance()
                file_is_path = True
            file_ref = self._parse_value_ref()
            status = self._parse_respond_status(line)
            return RespondInstr(is_file=True, file_ref=file_ref,
                                file_is_path=file_is_path, status=status, line=line)
        # respond .value [status N]
        value = self._parse_expr(line)
        status = self._parse_respond_status(line)
        return RespondInstr(value=value, status=status, line=line)

    def _parse_respond_status(self, base_line: int) -> Optional[int]:
        if self._same_line(base_line) and self._check("STATUS"):
            self._advance()
            t = self._expect("NUMBER_LITERAL")
            if '.' in t.value:
                raise ParseError("The status code after 'status' must be a whole number, like 'status 200'.", base_line)
            return int(t.value)
        return None

    def _parse_launch(self) -> LaunchInstr:
        """launch .programname.vern"""
        line = self._advance().line   # consume LAUNCH
        ref = self._parse_value_ref()
        return LaunchInstr(target=ref, line=line)

    def _parse_define(self) -> DefineInstr:
        line = self._peek().line
        self._expect("DEFINE")
        word = self._expect("TEXT_LITERAL").value
        self._expect("AS")
        action = self._parse_instruction()
        return DefineInstr(word=word, action=action, line=line)

    # ── Collection operations ──────────────────────────────────────────────────

    def _parse_put(self) -> Any:
        line = self._peek().line
        self._expect("PUT")

        # put dictionary <name> in ...
        if self._check("DICTIONARY"):
            self._advance()
            dict_name = self._expect("IDENTIFIER").value
            self._expect("IN")
            if self._check("LIST"):
                self._advance()
                list_name = self._expect("IDENTIFIER").value
                return PutDictInList(dict_name=dict_name, list_name=list_name, line=line)
            if self._check("DICTIONARY"):
                self._advance()
                target = self._expect("IDENTIFIER").value
                self._expect("KEY")
                key = self._parse_atom()
                return PutDictInDict(dict_name=dict_name, target_dict=target,
                                     key=key, line=line)
            raise ParseError("'put dictionary name in' must be followed by 'list' or 'dictionary'.", line)

        # put .value in list/dictionary
        value = self._parse_atom()
        self._expect("IN")

        if self._check("LIST"):
            self._advance()
            name = self._expect("IDENTIFIER").value
            file_ref = self._parse_optional_file_ref(line)
            return PutInList(value=value, list_name=name, file_ref=file_ref, line=line)

        if self._check("DICTIONARY"):
            self._advance()
            # dict ref can be IDENTIFIER or REFERENCE
            if self._check("IDENTIFIER"):
                dict_ref = self._advance().value
            else:
                dict_ref = self._parse_value_ref()
            file_ref = self._parse_optional_file_ref(line)
            self._expect("KEY")
            key = self._parse_atom()
            return PutInDict(value=value, dict_ref=dict_ref, key=key,
                             file_ref=file_ref, line=line)

        raise ParseError("'put' must be followed by 'list' or 'dictionary' to indicate where to add the value.", line)

    def _parse_remove(self) -> Any:
        line = self._peek().line
        self._expect("REMOVE")

        # remove key <k> from dictionary <name>
        if self._check("KEY"):
            self._advance()
            key = self._parse_atom()
            self._expect("FROM")
            self._expect("DICTIONARY")
            name = self._expect("IDENTIFIER").value
            return RemoveKeyFromDict(key=key, dict_name=name, line=line)

        # remove .value from list <name>
        value = self._parse_atom()
        self._expect("FROM")
        self._expect("LIST")
        name = self._expect("IDENTIFIER").value
        file_ref = self._parse_optional_file_ref(line)
        return RemoveFromList(value=value, list_name=name, file_ref=file_ref, line=line)

    def _parse_get(self) -> Any:
        line = self._peek().line
        self._expect("GET")
        t = self._peek()
        if t is None:
            raise ParseError("'get' must be followed by 'date', 'time', 'files', 'list', or 'dictionary'.", line)

        # get date as .today
        if t.type == "DATE":
            self._advance()
            self._expect("AS")
            result = self._parse_value_ref()
            return GetDateInstr(result=result, line=line)

        # get time as .now
        if t.type == "TIME":
            self._advance()
            self._expect("AS")
            result = self._parse_value_ref()
            return GetTimeInstr(result=result, line=line)

        # get files in .folder as list names
        if t.type == "FILES":
            self._advance()
            self._expect("IN")
            folder = self._parse_value_ref()
            self._expect("AS")
            self._expect("LIST")
            list_name = self._expect("IDENTIFIER").value
            return GetFilesInstr(folder=folder, result_list=list_name, line=line)

        # get list <name> <n> as .result
        if t.type == "LIST":
            self._advance()
            name = self._expect("IDENTIFIER").value
            file_ref = self._parse_optional_file_ref(line)
            position = self._parse_atom()
            self._expect("AS")
            result = self._parse_value_ref()
            return GetListItem(list_name=name, position=position, result=result,
                               file_ref=file_ref, line=line)

        # get dictionary <name-or-ref> key <k> as .result
        if t.type == "DICTIONARY":
            self._advance()
            if self._check("IDENTIFIER"):
                dict_ref = self._advance().value
            else:
                dict_ref = self._parse_value_ref()
            self._expect("KEY")
            key = self._parse_atom()
            self._expect("AS")
            result = self._parse_value_ref()
            return GetDictItem(dict_ref=dict_ref, key=key, result=result, line=line)

        raise ParseError(f"'{t.value}' cannot follow 'get'. Use 'get date', 'get time', 'get files', 'get list', or 'get dictionary'.", line)

    def _parse_count(self) -> Any:
        line = self._peek().line
        self._expect("COUNT")
        t = self._peek()
        if t is None:
            raise ParseError("'count' must be followed by 'list' or 'dictionary'.", line)

        if t.type == "LIST":
            self._advance()
            name = self._expect("IDENTIFIER").value
            file_ref = self._parse_optional_file_ref(line)
            self._expect("AS")
            result = self._parse_value_ref()
            return CountList(list_name=name, result=result, file_ref=file_ref, line=line)

        if t.type == "DICTIONARY":
            self._advance()
            name = self._expect("IDENTIFIER").value
            self._expect("AS")
            result = self._parse_value_ref()
            return CountDict(dict_name=name, result=result, line=line)

        raise ParseError(f"'{t.value}' cannot follow 'count'. Write 'count list name' or 'count dictionary name'.", line)

    def _parse_sort(self) -> SortList:
        line = self._peek().line
        self._expect("SORT")
        self._expect("LIST")
        name = self._expect("IDENTIFIER").value
        descending = bool(self._match("DESCENDING"))
        self._expect("AS")
        self._expect("LIST")
        result = self._expect("IDENTIFIER").value
        return SortList(list_name=name, descending=descending,
                        result_name=result, line=line)

    def _parse_reverse(self) -> ReverseList:
        line = self._peek().line
        self._expect("REVERSE")
        self._expect("LIST")
        name = self._expect("IDENTIFIER").value
        self._expect("AS")
        self._expect("LIST")
        result = self._expect("IDENTIFIER").value
        return ReverseList(list_name=name, result_name=result, line=line)

    def _parse_slice(self) -> SliceList:
        line = self._peek().line
        self._expect("SLICE")
        self._expect("LIST")
        name = self._expect("IDENTIFIER").value
        start = self._parse_atom()
        self._expect("TO")
        end = self._parse_atom()
        self._expect("AS")
        self._expect("LIST")
        result = self._expect("IDENTIFIER").value
        return SliceList(list_name=name, start=start, end=end,
                         result_name=result, line=line)

    def _parse_combine(self) -> CombineList:
        line = self._peek().line
        self._expect("COMBINE")
        self._expect("LIST")
        first = self._expect("IDENTIFIER").value
        self._expect("WITH")
        self._expect("LIST")
        second = self._expect("IDENTIFIER").value
        self._expect("AS")
        self._expect("LIST")
        result = self._expect("IDENTIFIER").value
        return CombineList(first=first, second=second, result=result, line=line)

    # ── Extended math ──────────────────────────────────────────────────────────

    def _parse_round_floor_ceiling(self, cls, keyword: str) -> Any:
        line = self._peek().line
        self._expect(keyword)
        value = self._parse_atom()
        decimals = None
        if self._same_line(line) and self._check("TO"):
            self._advance()
            decimals = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return cls(value=value, decimals=decimals, result=result, line=line)

    def _parse_round(self):
        return self._parse_round_floor_ceiling(RoundInstr, "ROUND")

    def _parse_floor(self):
        return self._parse_round_floor_ceiling(FloorInstr, "FLOOR")

    def _parse_ceiling(self):
        return self._parse_round_floor_ceiling(CeilingInstr, "CEILING")

    def _parse_random(self) -> RandomInstr:
        line = self._peek().line
        self._expect("RANDOM")
        min_val = self._parse_atom()
        self._expect("TO")
        max_val = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return RandomInstr(min_val=min_val, max_val=max_val, result=result, line=line)

    def _parse_absolute(self) -> AbsoluteInstr:
        line = self._peek().line
        self._expect("ABSOLUTE")
        value = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return AbsoluteInstr(value=value, result=result, line=line)

    def _parse_minmax(self, op: str) -> MinMaxInstr:
        line = self._peek().line
        self._expect(op.upper())
        t = self._peek()
        if t and t.type == "LIST":
            self._advance()
            name = self._expect("IDENTIFIER").value
            self._expect("AS")
            result = self._parse_value_ref()
            return MinMaxInstr(op=op, operands=name, result=result, line=line)
        a = self._parse_atom()
        b = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return MinMaxInstr(op=op, operands=(a, b), result=result, line=line)

    def _parse_percent(self) -> PercentInstr:
        line = self._peek().line
        self._expect("PERCENT")
        value = self._parse_atom()
        self._expect("OF")
        total = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return PercentInstr(value=value, total=total, result=result, line=line)

    def _parse_sum(self) -> SumInstr:
        line = self._peek().line
        self._expect("SUM")
        self._expect("LIST")
        name = self._expect("IDENTIFIER").value
        self._expect("AS")
        result = self._parse_value_ref()
        return SumInstr(list_name=name, result=result, line=line)

    def _parse_factorial(self) -> FactorialInstr:
        line = self._peek().line
        self._expect("FACTORIAL")
        value = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return FactorialInstr(value=value, result=result, line=line)

    def _parse_combinations(self) -> CombinationsInstr:
        line = self._peek().line
        self._expect("COMBINATIONS")
        n = self._parse_atom()
        k = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return CombinationsInstr(n=n, k=k, result=result, line=line)

    def _parse_permutations(self) -> PermutationsInstr:
        line = self._peek().line
        self._expect("PERMUTATIONS")
        n = self._parse_atom()
        k = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return PermutationsInstr(n=n, k=k, result=result, line=line)

    def _parse_sign(self) -> SignInstr:
        line = self._peek().line
        self._expect("SIGN")
        value = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return SignInstr(value=value, result=result, line=line)

    # ── Trig ───────────────────────────────────────────────────────────────────

    def _parse_trig(self, func: str) -> TrigInstr:
        line = self._peek().line
        # Consume the function token (compound or single)
        func_upper = func.upper().replace(" ", "_")
        self._advance()   # already matched by dispatch

        args = [self._parse_atom()]

        # arctangent can take a second argument (y x form)
        if func == "arctangent":
            t = self._peek()
            if t and t.type == "REFERENCE" and t.line == line:
                args.append(self._parse_atom())

        use_radians = False
        if self._same_line(line) and self._check("RADIANS"):
            self._advance()
            use_radians = True

        self._expect("AS")
        result = self._parse_value_ref()
        return TrigInstr(func=func, args=args, use_radians=use_radians,
                         result=result, line=line)

    # ── Logarithms ─────────────────────────────────────────────────────────────

    def _parse_ln(self) -> LnInstr:
        line = self._peek().line
        self._expect("LN")
        value = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return LnInstr(value=value, result=result, line=line)

    def _parse_log(self) -> LogInstr:
        line = self._peek().line
        self._expect("LOG")
        value = self._parse_atom()
        base = None
        if self._same_line(line) and self._check("BASE"):
            self._advance()
            base = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return LogInstr(value=value, base=base, result=result, line=line)

    # ── Angle conversion ───────────────────────────────────────────────────────

    def _parse_angle_conv(self, direction: str) -> AngleConvInstr:
        line = self._peek().line
        self._advance()   # TO_DEGREES or TO_RADIANS
        value = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return AngleConvInstr(direction=direction, value=value, result=result, line=line)

    # ── String operations ──────────────────────────────────────────────────────

    def _parse_length_of(self) -> LengthOfInstr:
        line = self._peek().line
        self._expect("LENGTH_OF")
        value = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return LengthOfInstr(value=value, result=result, line=line)

    def _parse_find(self) -> FindInstr:
        line = self._peek().line
        self._expect("FIND")
        pattern = self._parse_atom()
        self._expect("IN")
        text = self._parse_value_ref()
        self._expect("AS")
        result = self._parse_value_ref()
        return FindInstr(pattern=pattern, text=text, result=result, line=line)

    def _parse_extract(self) -> ExtractInstr:
        line = self._peek().line
        self._expect("EXTRACT")
        self._expect("FROM")
        text = self._parse_value_ref()
        self._expect("BEGINNING")
        beginning = self._parse_atom()
        self._expect("FINISHING")
        finishing = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return ExtractInstr(text=text, beginning=beginning, finishing=finishing,
                            result=result, line=line)

    def _parse_replace(self) -> ReplaceInstr:
        line = self._peek().line
        self._expect("REPLACE")
        old = self._parse_atom()
        self._expect("WITH")
        new = self._parse_atom()
        self._expect("IN")
        text = self._parse_value_ref()
        self._expect("AS")
        result = self._parse_value_ref()
        return ReplaceInstr(old=old, new=new, text=text, result=result, line=line)

    def _parse_split(self) -> SplitInstr:
        line = self._peek().line
        self._expect("SPLIT")
        text = self._parse_atom()
        self._expect("BY")
        delimiter = self._parse_atom()
        self._expect("AS")
        self._expect("LIST")
        list_name = self._expect("IDENTIFIER").value
        return SplitInstr(text=text, delimiter=delimiter, result_list=list_name, line=line)

    def _parse_join(self) -> JoinInstr:
        line = self._peek().line
        self._expect("JOIN")
        self._expect("LIST")
        name = self._expect("IDENTIFIER").value
        self._expect("BY")
        separator = self._parse_atom()
        self._expect("AS")
        result = self._parse_value_ref()
        return JoinInstr(list_name=name, separator=separator, result=result, line=line)

    def _parse_trim(self) -> TrimInstr:
        line = self._peek().line
        self._expect("TRIM")
        text = self._parse_value_ref()
        self._expect("AS")
        result = self._parse_value_ref()
        return TrimInstr(text=text, result=result, line=line)

    def _parse_uppercase(self) -> UppercaseInstr:
        line = self._peek().line
        self._expect("UPPERCASE")
        text = self._parse_value_ref()
        self._expect("AS")
        result = self._parse_value_ref()
        return UppercaseInstr(text=text, result=result, line=line)

    def _parse_lowercase(self) -> LowercaseInstr:
        line = self._peek().line
        self._expect("LOWERCASE")
        text = self._parse_value_ref()
        self._expect("AS")
        result = self._parse_value_ref()
        return LowercaseInstr(text=text, result=result, line=line)

    # ── Format ─────────────────────────────────────────────────────────────────

    def _parse_format(self) -> Any:
        line = self._peek().line
        self._expect("FORMAT")
        value = self._parse_value_ref()
        self._expect("AS")
        result = self._parse_value_ref()

        # date/time format: followed by USING
        if self._same_line(line) and self._check("USING"):
            self._advance()
            fmt = self._parse_atom()
            return FormatDateTimeInstr(value=value, result=result, fmt=fmt, line=line)

        # number format: followed by DECIMALS, THOUSANDS, or PADDED
        decimals = None
        thousands = False
        padded = None
        found_mod = False
        while self._same_line(line):
            t = self._peek()
            if t is None:
                break
            if t.type == "DECIMALS":
                self._advance()
                decimals = self._parse_atom()
                found_mod = True
            elif t.type == "THOUSANDS":
                self._advance()
                thousands = True
                found_mod = True
            elif t.type == "PADDED":
                self._advance()
                padded = self._parse_atom()
                found_mod = True
            else:
                break
        if not found_mod:
            raise ParseError("'format' requires at least one modifier. For dates and times use 'using'; for numbers use 'decimals', 'thousands', or 'padded'.", line)
        return FormatNumberInstr(value=value, result=result, decimals=decimals,
                                 thousands=thousands, padded=padded, line=line)

    # ── Date / time ────────────────────────────────────────────────────────────

    def _parse_difference_between(self) -> DiffBetweenInstr:
        line = self._peek().line
        self._expect("DIFFERENCE_BETWEEN")
        first = self._parse_value_ref()
        self._expect("AND")
        second = self._parse_value_ref()
        self._expect("IN")
        unit_tok = self._expect("DAYS", "HOURS", "MINUTES")
        self._expect("AS")
        result = self._parse_value_ref()
        return DiffBetweenInstr(first=first, second=second, unit=unit_tok.value,
                                result=result, line=line)

    # ── File ops ───────────────────────────────────────────────────────────────

    def _parse_delete(self) -> Any:
        line = self._peek().line
        self._expect("DELETE")
        # delete path .ref — dynamic file path
        if self._check("PATH"):
            self._advance()
            path_ref = self._parse_value_ref()
            return DeleteInstr(path=path_ref, path_is_path=True, line=line)
        path = self._parse_value_ref()
        # If the ref contains a recognized file extension, it's a static file deletion
        ref_parts = [p for p in path.ref.split('.') if p]
        if any(p in ALL_RECOGNIZED_EXTENSIONS for p in ref_parts):
            return DeleteInstr(path=path, line=line)
        # Otherwise it's HTTP DELETE (url in .valuename)
        headers_dict = None
        status = None
        if self._same_line(line) and self._check("WITH"):
            self._advance()
            self._expect("HEADERS")
            self._expect("DICTIONARY")
            headers_dict = self._expect("IDENTIFIER").value
        if self._same_line(line) and self._check("STATUS"):
            self._advance()
            status = self._parse_value_ref()
        return DeleteUrlInstr(url=path, headers_dict=headers_dict,
                              status=status, line=line)

    # ── Networking ─────────────────────────────────────────────────────────────

    def _parse_fetch(self) -> FetchInstr:
        """fetch .url [with headers dictionary name] [as .result [response headers .ref] [status .ref]]"""
        line = self._peek().line
        self._expect("FETCH")
        url = self._parse_atom()
        headers_dict = None
        result = None
        response_headers = None
        status = None
        if self._same_line(line) and self._check("WITH"):
            self._advance()
            self._expect("HEADERS")
            self._expect("DICTIONARY")
            headers_dict = self._expect("IDENTIFIER").value
        if self._same_line(line) and self._check("AS"):
            self._advance()
            result = self._parse_value_ref()
        if self._same_line(line) and self._check("RESPONSE_HEADERS"):
            self._advance()
            response_headers = self._parse_value_ref()
        if self._same_line(line) and self._check("STATUS"):
            self._advance()
            status = self._parse_value_ref()
        return FetchInstr(url=url, result=result, headers_dict=headers_dict,
                          response_headers=response_headers, status=status,
                          line=line)

    def _parse_send(self) -> SendInstr:
        """send .data to .url [with headers dictionary name] [status .ref]"""
        line = self._peek().line
        self._expect("SEND")
        data = self._parse_atom()
        self._expect("TO")
        url = self._parse_atom()
        headers_dict = None
        status = None
        if self._same_line(line) and self._check("WITH"):
            self._advance()
            self._expect("HEADERS")
            self._expect("DICTIONARY")
            headers_dict = self._expect("IDENTIFIER").value
        if self._same_line(line) and self._check("STATUS"):
            self._advance()
            status = self._parse_value_ref()
        return SendInstr(data=data, url=url, headers_dict=headers_dict,
                         status=status, line=line)

    def _parse_update(self) -> UpdateInstr:
        """update .data to .url [with headers dictionary name] [status .ref]"""
        line = self._peek().line
        self._expect("UPDATE")
        data = self._parse_atom()
        self._expect("TO")
        url = self._parse_atom()
        headers_dict = None
        status = None
        if self._same_line(line) and self._check("WITH"):
            self._advance()
            self._expect("HEADERS")
            self._expect("DICTIONARY")
            headers_dict = self._expect("IDENTIFIER").value
        if self._same_line(line) and self._check("STATUS"):
            self._advance()
            status = self._parse_value_ref()
        return UpdateInstr(data=data, url=url, headers_dict=headers_dict,
                           status=status, line=line)

    def _parse_parse(self) -> ParseInstr:
        """parse json/csv/xml/ini .valuename as list/dictionary resultname"""
        line = self._peek().line
        self._expect("PARSE")
        fmt_tok = self._expect("JSON", "CSV", "XML", "INI")
        fmt = fmt_tok.value
        source = self._parse_value_ref()
        self._expect("AS")
        rt_tok = self._expect("LIST", "DICTIONARY")
        result_type = rt_tok.value  # "list" or "dictionary"
        result_name = self._expect("IDENTIFIER").value
        return ParseInstr(format=fmt, source=source, result_type=result_type,
                          result_name=result_name, line=line)

    def _parse_inspect(self) -> InspectInstr:
        """inspect json/csv/xml/ini .valuename"""
        line = self._peek().line
        self._expect("INSPECT")
        fmt_tok = self._expect("JSON", "CSV", "XML", "INI")
        fmt = fmt_tok.value
        source = self._parse_value_ref()
        return InspectInstr(format=fmt, source=source, line=line)


# ── Public API ─────────────────────────────────────────────────────────────────

def parse(source: str) -> Program:
    tokens = tokenize(source)
    return Parser(tokens).parse_program()


def parse_file(path: str) -> Program:
    tokens = tokenize_file(path)
    return Parser(tokens).parse_program()


# ── CLI ────────────────────────────────────────────────────────────────────────

def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python parser.py <file.vern>", file=sys.stderr)
        sys.exit(1)
    path = sys.argv[1]
    try:
        program = parse_file(path)
        pprint.pprint(program, width=100, depth=6)
    except (TokenizeError, ParseError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print(f"File not found: {path}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
