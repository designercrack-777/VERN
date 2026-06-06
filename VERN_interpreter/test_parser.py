#!/usr/bin/env python3
"""
Tests for the VERN parser — v0.6 spec.

Run with:
    python test_parser.py
"""

import sys, os, unittest
sys.path.insert(0, os.path.dirname(__file__))
from parser import parse, parse_file, ParseError
from ast_nodes import *


def first(src: str) -> Any:
    """Parse and return the first top-level node."""
    return parse(src).body[0]


def body0(src: str) -> Any:
    """First node inside the first script body."""
    return parse(src).body[0].body[0]


EXAMPLES = os.path.join(os.path.dirname(__file__), "examples")


# ── Example programs ───────────────────────────────────────────────────────────

class TestExamplePrograms(unittest.TestCase):

    def _parse(self, name):
        prog = parse_file(os.path.join(EXAMPLES, name))
        self.assertIsInstance(prog, Program)
        self.assertGreater(len(prog.body), 0)
        return prog

    def test_calculator(self):
        prog = self._parse("calculator.vern")
        script = prog.body[0]
        self.assertIsInstance(script, ScriptDef)
        self.assertEqual(script.name.ref, ".calculation")
        # ends with start_at and stop
        self.assertIsInstance(prog.body[-1], StopInstr)
        self.assertIsInstance(prog.body[-2], StartAt)

    def test_quiz(self):
        prog = self._parse("quiz.vern")
        # 10 set instructions at file level, then a script, then stop
        sets = [n for n in prog.body if isinstance(n, SetInstr)]
        self.assertEqual(len(sets), 10)
        scripts = [n for n in prog.body if isinstance(n, ScriptDef)]
        self.assertEqual(len(scripts), 1)
        self.assertEqual(scripts[0].name.ref, ".quiz")

    def test_days_until(self):
        prog = self._parse("days_until.vern")
        # first node: set .target to 2026-12-31 (date literal)
        node = prog.body[0]
        self.assertIsInstance(node, SetInstr)
        self.assertIsInstance(node.value, DateLit)
        self.assertEqual(node.value.value, "2026-12-31")
        # script contains difference_between
        script = next(n for n in prog.body if isinstance(n, ScriptDef))
        diff = next(n for n in script.body if isinstance(n, DiffBetweenInstr))
        self.assertEqual(diff.unit, "days")

    def test_name_registry(self):
        prog = self._parse("name_registry.vern")
        # first node: empty list declaration
        ld = prog.body[0]
        self.assertIsInstance(ld, ListDecl)
        self.assertEqual(ld.name, "names")
        self.assertEqual(ld.items, [])

    def test_safe_input(self):
        prog = self._parse("safe_input.vern")
        script = next(n for n in prog.body if isinstance(n, ScriptDef) and ".main" in n.name.ref)
        while_node = script.body[0]
        self.assertIsInstance(while_node, WhileBlock)
        attempt = while_node.body[0]
        self.assertIsInstance(attempt, AttemptBlock)
        self.assertFalse(attempt.try_all)

    def test_localization(self):
        prog = self._parse("localization.vern")
        containers = [n for n in prog.body if isinstance(n, ContainerDef)]
        self.assertEqual(len(containers), 3)
        tags = {c.tag for c in containers}
        self.assertIn("#english", tags)
        self.assertIn("#spanish", tags)
        self.assertIn("#swahili", tags)
        # each container has 3 set instructions
        for c in containers:
            self.assertEqual(len(c.body), 3)


# ── Expressions ────────────────────────────────────────────────────────────────

class TestExpressions(unittest.TestCase):

    def test_number_literal(self):
        n = first("set .x to 42")
        self.assertIsInstance(n.value, NumberLit)
        self.assertEqual(n.value.value, "42")

    def test_text_literal(self):
        n = first('set .x to "hello"')
        self.assertIsInstance(n.value, TextLit)
        self.assertEqual(n.value.value, "hello")

    def test_date_literal(self):
        n = first("set .x to 2026-12-31")
        self.assertIsInstance(n.value, DateLit)

    def test_time_literal(self):
        n = first("set .x to 14:30:00")
        self.assertIsInstance(n.value, TimeLit)

    def test_bool_true(self):
        n = first("set .x to true")
        self.assertIsInstance(n.value, BoolLit)
        self.assertTrue(n.value.value)

    def test_bool_false(self):
        n = first("set .x to false")
        self.assertIsInstance(n.value, BoolLit)
        self.assertFalse(n.value.value)

    def test_constant_pi(self):
        n = first("set .x to pi")
        self.assertIsInstance(n.value, Constant)
        self.assertEqual(n.value.name, "pi")

    def test_constant_e(self):
        n = first("set .x to e")
        self.assertIsInstance(n.value, Constant)

    def test_binop_plus(self):
        n = first("set .x to .a + .b")
        self.assertIsInstance(n.value, BinOp)
        self.assertEqual(n.value.op, "+")

    def test_binop_minus(self):
        n = first("set .x to .a - .b")
        self.assertIsInstance(n.value, BinOp)
        self.assertEqual(n.value.op, "-")

    def test_binop_multiply(self):
        n = first("set .x to .a * .b")
        self.assertIsInstance(n.value, BinOp)
        self.assertEqual(n.value.op, "*")

    def test_binop_divide(self):
        n = first("set .x to .a / .b")
        self.assertIsInstance(n.value, BinOp)
        self.assertEqual(n.value.op, "/")

    def test_binop_power(self):
        n = first("set .x to .n power 2")
        self.assertIsInstance(n.value, BinOp)
        self.assertEqual(n.value.op, "power")

    def test_binop_root(self):
        n = first("set .x to .n root 2")
        self.assertIsInstance(n.value, BinOp)
        self.assertEqual(n.value.op, "root")

    def test_binop_remainder(self):
        n = first("set .x to .n remainder .m")
        self.assertIsInstance(n.value, BinOp)
        self.assertEqual(n.value.op, "remainder")

    def test_chained_binop_left_assoc(self):
        n = first("set .x to .a + .b + .c")
        # should be (a+b)+c
        self.assertIsInstance(n.value, BinOp)
        self.assertIsInstance(n.value.left, BinOp)

    def test_value_ref(self):
        n = first("set .x to .myvalue")
        self.assertIsInstance(n.value, ValueRef)
        self.assertEqual(n.value.ref, ".myvalue")

    def test_inline_container_on_ref(self):
        n = first("show .greeting #spanish")
        self.assertIsInstance(n, ShowInstr)
        ref = n.values[0]
        self.assertIsInstance(ref, ValueRef)
        self.assertEqual(ref.container, "#spanish")

    def test_loop_var(self):
        src = "script .s\n    show loop\nend script"
        n = parse(src).body[0].body[0]
        self.assertIsInstance(n, ShowInstr)
        self.assertIsInstance(n.values[0], LoopVar)

    def test_current_item(self):
        src = "script .s\n    show current item\nend script"
        n = parse(src).body[0].body[0]
        self.assertIsInstance(n.values[0], CurrentItem)

    def test_string_concat_in_show(self):
        n = first('show "hello " + .name')
        self.assertIsInstance(n, ShowInstr)
        self.assertIsInstance(n.values[0], BinOp)


# ── Conditions ─────────────────────────────────────────────────────────────────

class TestConditions(unittest.TestCase):

    def _cond(self, src: str) -> Any:
        return first(src).condition

    def test_eq_symbol(self):
        c = self._cond("if .x = 5 then stop")
        self.assertIsInstance(c, Comparison)
        self.assertEqual(c.op, "EQ")

    def test_neq_symbol(self):
        c = self._cond("if .x != 5 then stop")
        self.assertEqual(c.op, "NEQ")

    def test_gte_symbol(self):
        c = self._cond("if .score >= 4 then stop")
        self.assertEqual(c.op, "GTE")

    def test_lte_symbol(self):
        c = self._cond("if .score <= 4 then stop")
        self.assertEqual(c.op, "LTE")

    def test_is_equal_to(self):
        c = self._cond("if .x is equal to 5 then stop")
        self.assertEqual(c.op, "IS_EQUAL_TO")

    def test_is_not(self):
        c = self._cond("if .x is not 5 then stop")
        self.assertEqual(c.op, "IS_NOT")

    def test_is_greater_than(self):
        c = self._cond("if .x is greater than 5 then stop")
        self.assertEqual(c.op, "IS_GREATER_THAN")

    def test_is_less_than(self):
        c = self._cond("if .x is less than 5 then stop")
        self.assertEqual(c.op, "IS_LESS_THAN")

    def test_is_greater_than_or_equal_to(self):
        c = self._cond("if .x is greater than or equal to 5 then stop")
        self.assertEqual(c.op, "IS_GREATER_THAN_OR_EQUAL_TO")

    def test_is_less_than_or_equal_to(self):
        c = self._cond("if .x is less than or equal to 5 then stop")
        self.assertEqual(c.op, "IS_LESS_THAN_OR_EQUAL_TO")

    def test_not_condition(self):
        c = self._cond("if not .active then stop")
        self.assertIsInstance(c, NotCond)

    def test_and_condition(self):
        c = self._cond("if .a = 1 and .b = 2 then stop")
        self.assertIsInstance(c, AndCond)

    def test_or_condition(self):
        c = self._cond("if .a = 1 or .b = 2 then stop")
        self.assertIsInstance(c, OrCond)

    def test_and_or_left_assoc(self):
        # a=1 and b=2 or c=3 → (a=1 and b=2) or c=3
        c = self._cond("if .a = 1 and .b = 2 or .c = 3 then stop")
        self.assertIsInstance(c, OrCond)
        self.assertIsInstance(c.left, AndCond)

    def test_is_in_list(self):
        c = self._cond("if .x is in list names then stop")
        self.assertIsInstance(c, MemberCheck)
        self.assertFalse(c.negated)
        self.assertEqual(c.collection_kind, "list")

    def test_not_in_list(self):
        c = self._cond("if .x not in list names then stop")
        self.assertIsInstance(c, MemberCheck)
        self.assertTrue(c.negated)

    def test_is_in_text(self):
        c = self._cond('if "hello" is in .message then stop')
        self.assertIsInstance(c, MemberCheck)
        self.assertEqual(c.collection_kind, "text")

    def test_exist_check(self):
        c = self._cond("if .records.vern exist then stop")
        self.assertIsInstance(c, ExistCheck)

    def test_starts_with(self):
        c = self._cond('if .text starts with "hello" then stop')
        self.assertIsInstance(c, StartsWithCond)

    def test_ends_with(self):
        c = self._cond('if .text ends with "world" then stop')
        self.assertIsInstance(c, EndsWithCond)


# ── Instructions ───────────────────────────────────────────────────────────────

class TestInstructions(unittest.TestCase):

    def test_set(self):
        n = first("set .score to 0")
        self.assertIsInstance(n, SetInstr)
        self.assertEqual(n.target.ref, ".score")

    def test_show_single(self):
        n = first("show .name")
        self.assertIsInstance(n, ShowInstr)
        self.assertEqual(len(n.values), 1)

    def test_show_multiple(self):
        n = first("show .a, .b, .c")
        self.assertIsInstance(n, ShowInstr)
        self.assertEqual(len(n.values), 3)

    def test_ask(self):
        n = first("ask .input")
        self.assertIsInstance(n, AskInstr)

    def test_read_single(self):
        n = first("read .name from .file.vern")
        self.assertIsInstance(n, ReadInstr)
        self.assertEqual(len(n.targets), 1)

    def test_read_multiple(self):
        n = first("read .name, .score from .file.vern")
        self.assertIsInstance(n, ReadInstr)
        self.assertEqual(len(n.targets), 2)

    def test_write(self):
        n = first("write .name to .file.vern")
        self.assertIsInstance(n, WriteInstr)

    def test_append(self):
        n = first("append .name, .score to .file.vern")
        self.assertIsInstance(n, AppendInstr)
        self.assertEqual(len(n.values), 2)

    def test_run_plain(self):
        n = first("run .main.script")
        self.assertIsInstance(n, RunInstr)
        self.assertEqual(n.args, [])
        self.assertIsNone(n.container)

    def test_run_with_container(self):
        n = first("run .greet.script #english")
        self.assertIsInstance(n, RunInstr)
        self.assertEqual(n.container, "#english")

    def test_run_with_args(self):
        n = first("run .add.script with 10, 20")
        self.assertIsInstance(n, RunInstr)
        self.assertEqual(len(n.args), 2)

    def test_return(self):
        n = first("return .total pass to .answer")
        self.assertIsInstance(n, ReturnInstr)
        self.assertEqual(n.value.ref, ".total")
        self.assertEqual(n.dest.ref, ".answer")

    def test_convert(self):
        n = first("convert .input to number as .value")
        self.assertIsInstance(n, ConvertInstr)
        self.assertEqual(n.target_type, "number")

    def test_type_of(self):
        n = first("type of .value as .kind")
        self.assertIsInstance(n, TypeOfInstr)

    def test_import(self):
        n = first("import .utilities.vern")
        self.assertIsInstance(n, ImportInstr)

    def test_stop(self):
        n = first("stop")
        self.assertIsInstance(n, StopInstr)

    def test_start_at(self):
        n = first("start at .main.script")
        self.assertIsInstance(n, StartAt)

    def test_define(self):
        n = first('define "greet" as run .greet.script')
        self.assertIsInstance(n, DefineInstr)
        self.assertEqual(n.word, "greet")
        self.assertIsInstance(n.action, RunInstr)

    def test_exit_loop(self):
        src = "script .s\n    exit loop\nend script"
        n = parse(src).body[0].body[0]
        self.assertIsInstance(n, ExitLoopInstr)

    def test_next_item(self):
        src = "script .s\n    next item\nend script"
        n = parse(src).body[0].body[0]
        self.assertIsInstance(n, NextItemInstr)


# ── Control flow ───────────────────────────────────────────────────────────────

class TestControlFlow(unittest.TestCase):

    def test_if_inline(self):
        n = first("if .x = 5 then show .x")
        self.assertIsInstance(n, IfInline)
        self.assertIsInstance(n.action, ShowInstr)

    def test_if_block(self):
        src = "if .x = 5\n    show .x\nend if"
        n = first(src)
        self.assertIsInstance(n, IfBlock)
        self.assertEqual(len(n.then_body), 1)
        self.assertEqual(len(n.else_body), 0)

    def test_if_otherwise(self):
        src = "if .x = 5\n    show .x\notherwise\n    show .y\nend if"
        n = first(src)
        self.assertIsInstance(n, IfBlock)
        self.assertEqual(len(n.then_body), 1)
        self.assertEqual(len(n.else_body), 1)

    def test_while(self):
        src = "while .x = false\n    ask .x\nend while"
        n = first(src)
        self.assertIsInstance(n, WhileBlock)
        self.assertEqual(len(n.body), 1)

    def test_repeat_times(self):
        src = "repeat 3 times\n    show loop\nend repeat"
        n = first(src)
        self.assertIsInstance(n, RepeatTimesBlock)
        self.assertIsInstance(n.count, NumberLit)

    def test_repeat_times_ref_count(self):
        src = "repeat .count times\n    show loop\nend repeat"
        n = first(src)
        self.assertIsInstance(n.count, ValueRef)

    def test_repeat_through_list(self):
        src = "list names\nend list\nrepeat through list names\n    show current item\nend repeat"
        prog = parse(src)
        n = prog.body[1]
        self.assertIsInstance(n, RepeatThroughListBlock)
        self.assertEqual(n.list_name, "names")

    def test_repeat_through_dict(self):
        src = "dictionary scores\nend dictionary\nrepeat through dictionary scores\n    show current key\nend repeat"
        prog = parse(src)
        n = prog.body[1]
        self.assertIsInstance(n, RepeatThroughDictBlock)

    def test_attempt_block(self):
        src = "attempt\n    ask .x\nif fail\n    show fail reason\nend fail\nend attempt"
        n = first(src)
        self.assertIsInstance(n, AttemptBlock)
        self.assertFalse(n.try_all)
        self.assertEqual(len(n.body), 1)
        self.assertEqual(len(n.fail_body), 1)

    def test_attempt_all(self):
        src = "attempt all\n    ask .x\nif fail\n    show fail reason\nend fail\nend attempt"
        n = first(src)
        self.assertIsInstance(n, AttemptBlock)
        self.assertTrue(n.try_all)

    def test_nested_if_in_while(self):
        src = ("while .x = false\n"
               "    if .y = 1 then set .x to true\n"
               "end while")
        n = first(src)
        self.assertIsInstance(n, WhileBlock)
        self.assertIsInstance(n.body[0], IfInline)


# ── Script definitions ──────────────────────────────────────────────────────────

class TestScriptDef(unittest.TestCase):

    def test_basic_script(self):
        src = "script .greet\n    show .greeting\nend script"
        n = first(src)
        self.assertIsInstance(n, ScriptDef)
        self.assertEqual(n.name.ref, ".greet")
        self.assertEqual(n.params, [])

    def test_script_with_params(self):
        src = "script .add takes .first, .second\n    show .first\nend script"
        n = first(src)
        self.assertIsInstance(n, ScriptDef)
        self.assertEqual(len(n.params), 2)
        self.assertEqual(n.params[0].ref, ".first")

    def test_script_with_container_tag(self):
        src = "script .greet #english\n    show .greeting\nend script"
        n = first(src)
        self.assertIsInstance(n, ScriptDef)
        self.assertEqual(n.container, "#english")

    def test_nested_script_raises(self):
        src = "script .outer\n    script .inner\n    end script\nend script"
        with self.assertRaises(ParseError):
            parse(src)


# ── Collections ────────────────────────────────────────────────────────────────

class TestCollections(unittest.TestCase):

    def test_empty_list_decl(self):
        n = first("list names\nend list")
        self.assertIsInstance(n, ListDecl)
        self.assertEqual(n.name, "names")
        self.assertEqual(n.items, [])

    def test_list_with_items(self):
        src = 'list names\n    "alice"\n    "bob"\nend list'
        n = first(src)
        self.assertIsInstance(n, ListDecl)
        self.assertEqual(len(n.items), 2)

    def test_empty_dict_decl(self):
        n = first("dictionary scores\nend dictionary")
        self.assertIsInstance(n, DictDecl)
        self.assertEqual(n.name, "scores")

    def test_dict_with_pairs(self):
        src = 'dictionary scores\n    "alice" : 95\n    "bob" : 87\nend dictionary'
        n = first(src)
        self.assertIsInstance(n, DictDecl)
        self.assertEqual(len(n.pairs), 2)
        self.assertIsInstance(n.pairs[0][0], TextLit)
        self.assertIsInstance(n.pairs[0][1], NumberLit)

    def test_put_in_list(self):
        n = first("put .input in list names")
        self.assertIsInstance(n, PutInList)
        self.assertEqual(n.list_name, "names")

    def test_put_in_dict(self):
        n = first('put .score in dictionary scores key "alice"')
        self.assertIsInstance(n, PutInDict)

    def test_put_dict_in_list(self):
        n = first("put dictionary alicedata in list people")
        self.assertIsInstance(n, PutDictInList)
        self.assertEqual(n.dict_name, "alicedata")
        self.assertEqual(n.list_name, "people")

    def test_remove_from_list(self):
        n = first("remove .name from list names")
        self.assertIsInstance(n, RemoveFromList)

    def test_remove_key_from_dict(self):
        n = first('remove key "alice" from dictionary scores')
        self.assertIsInstance(n, RemoveKeyFromDict)

    def test_get_list_item(self):
        n = first("get list names 3 as .result")
        self.assertIsInstance(n, GetListItem)
        self.assertEqual(n.list_name, "names")

    def test_get_dict_item(self):
        n = first('get dictionary scores key "alice" as .result')
        self.assertIsInstance(n, GetDictItem)

    def test_count_list(self):
        n = first("count list names as .total")
        self.assertIsInstance(n, CountList)

    def test_count_dict(self):
        n = first("count dictionary scores as .total")
        self.assertIsInstance(n, CountDict)

    def test_sort_ascending(self):
        n = first("sort list scores as list ranked")
        self.assertIsInstance(n, SortList)
        self.assertFalse(n.descending)

    def test_sort_descending(self):
        n = first("sort list scores descending as list ranked")
        self.assertIsInstance(n, SortList)
        self.assertTrue(n.descending)

    def test_reverse_list(self):
        n = first("reverse list names as list reversed")
        self.assertIsInstance(n, ReverseList)

    def test_slice_list(self):
        n = first("slice list names 2 to 4 as list subset")
        self.assertIsInstance(n, SliceList)
        self.assertIsInstance(n.start, NumberLit)
        self.assertIsInstance(n.end, NumberLit)

    def test_combine_list(self):
        n = first("combine list first with list second as list merged")
        self.assertIsInstance(n, CombineList)

    def test_repeat_through_with_current_item(self):
        src = "list names\nend list\nrepeat through list names\n    show current item\nend repeat"
        prog = parse(src)
        loop = prog.body[1]
        self.assertIsInstance(loop, RepeatThroughListBlock)
        show = loop.body[0]
        self.assertIsInstance(show.values[0], CurrentItem)


# ── Extended math ──────────────────────────────────────────────────────────────

class TestExtendedMath(unittest.TestCase):

    def test_round(self):
        n = first("round .x as .result")
        self.assertIsInstance(n, RoundInstr)
        self.assertIsNone(n.decimals)

    def test_round_with_decimals(self):
        n = first("round .x to 2 as .result")
        self.assertIsInstance(n, RoundInstr)
        self.assertIsNotNone(n.decimals)

    def test_floor(self):
        n = first("floor .x as .result")
        self.assertIsInstance(n, FloorInstr)

    def test_ceiling(self):
        n = first("ceiling .x as .result")
        self.assertIsInstance(n, CeilingInstr)

    def test_random(self):
        n = first("random .min to .max as .result")
        self.assertIsInstance(n, RandomInstr)

    def test_absolute(self):
        n = first("absolute .n as .result")
        self.assertIsInstance(n, AbsoluteInstr)

    def test_minimum_two_values(self):
        n = first("minimum .a .b as .result")
        self.assertIsInstance(n, MinMaxInstr)
        self.assertEqual(n.op, "minimum")
        self.assertIsInstance(n.operands, tuple)

    def test_maximum_list(self):
        n = first("maximum list scores as .result")
        self.assertIsInstance(n, MinMaxInstr)
        self.assertEqual(n.op, "maximum")
        self.assertIsInstance(n.operands, str)

    def test_percent(self):
        n = first("percent .value of .total as .result")
        self.assertIsInstance(n, PercentInstr)

    def test_sum(self):
        n = first("sum list numbers as .result")
        self.assertIsInstance(n, SumInstr)

    def test_factorial(self):
        n = first("factorial .n as .result")
        self.assertIsInstance(n, FactorialInstr)

    def test_combinations(self):
        n = first("combinations .n .k as .result")
        self.assertIsInstance(n, CombinationsInstr)

    def test_permutations(self):
        n = first("permutations .n .k as .result")
        self.assertIsInstance(n, PermutationsInstr)

    def test_sign(self):
        n = first("sign .value as .result")
        self.assertIsInstance(n, SignInstr)


# ── Trig / log / angle ─────────────────────────────────────────────────────────

class TestTrigLog(unittest.TestCase):

    def test_sine(self):
        n = first("sine .angle as .result")
        self.assertIsInstance(n, TrigInstr)
        self.assertEqual(n.func, "sine")
        self.assertFalse(n.use_radians)

    def test_sine_radians(self):
        n = first("sine .angle radians as .result")
        self.assertIsInstance(n, TrigInstr)
        self.assertTrue(n.use_radians)

    def test_arctangent_two_args(self):
        n = first("arctangent .y .x as .result")
        self.assertIsInstance(n, TrigInstr)
        self.assertEqual(len(n.args), 2)

    def test_hyperbolic_sine(self):
        n = first("hyperbolic sine .value as .result")
        self.assertIsInstance(n, TrigInstr)
        self.assertEqual(n.func, "hyperbolic sine")

    def test_arc_hyperbolic_cosine(self):
        n = first("arc hyperbolic cosine .value as .result")
        self.assertIsInstance(n, TrigInstr)
        self.assertEqual(n.func, "arc hyperbolic cosine")

    def test_ln(self):
        n = first("ln .value as .result")
        self.assertIsInstance(n, LnInstr)

    def test_log_base10(self):
        n = first("log .value as .result")
        self.assertIsInstance(n, LogInstr)
        self.assertIsNone(n.base)

    def test_log_arbitrary_base(self):
        n = first("log .value base 2 as .result")
        self.assertIsInstance(n, LogInstr)
        self.assertIsNotNone(n.base)

    def test_to_degrees(self):
        n = first("to degrees .angle as .result")
        self.assertIsInstance(n, AngleConvInstr)
        self.assertEqual(n.direction, "degrees")

    def test_to_radians(self):
        n = first("to radians .angle as .result")
        self.assertIsInstance(n, AngleConvInstr)
        self.assertEqual(n.direction, "radians")


# ── String operations ──────────────────────────────────────────────────────────

class TestStringOps(unittest.TestCase):

    def test_length_of(self):
        n = first("length of .text as .result")
        self.assertIsInstance(n, LengthOfInstr)

    def test_find(self):
        n = first('find "hello" in .message as .pos')
        self.assertIsInstance(n, FindInstr)

    def test_extract(self):
        n = first("extract from .text beginning 1 finishing 5 as .result")
        self.assertIsInstance(n, ExtractInstr)

    def test_replace(self):
        n = first('replace "old" with "new" in .text as .result')
        self.assertIsInstance(n, ReplaceInstr)

    def test_split(self):
        n = first('split .csv by "," as list parts')
        self.assertIsInstance(n, SplitInstr)
        self.assertEqual(n.result_list, "parts")

    def test_join(self):
        n = first('join list names by ", " as .result')
        self.assertIsInstance(n, JoinInstr)

    def test_trim(self):
        n = first("trim .text as .result")
        self.assertIsInstance(n, TrimInstr)

    def test_uppercase(self):
        n = first("uppercase .name as .result")
        self.assertIsInstance(n, UppercaseInstr)

    def test_lowercase(self):
        n = first("lowercase .name as .result")
        self.assertIsInstance(n, LowercaseInstr)


# ── Date / time / format ───────────────────────────────────────────────────────

class TestDateTime(unittest.TestCase):

    def test_get_date(self):
        n = first("get date as .today")
        self.assertIsInstance(n, GetDateInstr)

    def test_get_time(self):
        n = first("get time as .now")
        self.assertIsInstance(n, GetTimeInstr)

    def test_difference_between_days(self):
        n = first("difference between .date1 and .date2 in days as .result")
        self.assertIsInstance(n, DiffBetweenInstr)
        self.assertEqual(n.unit, "days")

    def test_difference_between_hours(self):
        n = first("difference between .t1 and .t2 in hours as .result")
        self.assertIsInstance(n, DiffBetweenInstr)
        self.assertEqual(n.unit, "hours")

    def test_format_datetime(self):
        n = first('format .today as .display using "DD/MO/YYYY"')
        self.assertIsInstance(n, FormatDateTimeInstr)

    def test_format_number_decimals(self):
        n = first("format .price as .display decimals 2")
        self.assertIsInstance(n, FormatNumberInstr)
        self.assertIsNotNone(n.decimals)
        self.assertFalse(n.thousands)

    def test_format_number_thousands(self):
        n = first("format .population as .display thousands")
        self.assertIsInstance(n, FormatNumberInstr)
        self.assertTrue(n.thousands)

    def test_format_number_combined(self):
        n = first("format .amount as .display decimals 2 thousands padded 15")
        self.assertIsInstance(n, FormatNumberInstr)
        self.assertIsNotNone(n.decimals)
        self.assertTrue(n.thousands)
        self.assertIsNotNone(n.padded)

    def test_format_no_modifier_raises(self):
        with self.assertRaises(ParseError):
            parse("format .x as .y")


# ── File / network ─────────────────────────────────────────────────────────────

class TestFileNetwork(unittest.TestCase):

    def test_delete(self):
        n = first("delete .records.vern")
        self.assertIsInstance(n, DeleteInstr)

    def test_get_files(self):
        n = first("get files in .projects.folder as list filenames")
        self.assertIsInstance(n, GetFilesInstr)
        self.assertEqual(n.result_list, "filenames")

    def test_fetch(self):
        n = first("fetch .url as .response")
        self.assertIsInstance(n, FetchInstr)

    def test_send(self):
        n = first("send .payload to .url")
        self.assertIsInstance(n, SendInstr)


# ── Text blocks ────────────────────────────────────────────────────────────────

class TestTextBlock(unittest.TestCase):

    def test_text_block_decl(self):
        src = "text .welcome\n    hello world\n    second line\nend text"
        n = first(src)
        self.assertIsInstance(n, TextBlockDecl)
        self.assertEqual(n.name.ref, ".welcome")
        self.assertEqual(len(n.content_lines), 2)

    def test_empty_text_block(self):
        src = "text .msg\nend text"
        n = first(src)
        self.assertIsInstance(n, TextBlockDecl)
        self.assertEqual(n.content_lines, [])


# ── Error cases ────────────────────────────────────────────────────────────────

class TestParseErrors(unittest.TestCase):

    def test_unknown_instruction_raises(self):
        with self.assertRaises(ParseError):
            parse("blahblah .x")

    def test_missing_as_in_convert(self):
        with self.assertRaises(ParseError):
            parse("convert .x to number .result")

    def test_missing_end_script(self):
        with self.assertRaises(ParseError):
            parse("script .greet\n    show .x")

    def test_missing_end_if(self):
        with self.assertRaises(ParseError):
            parse("if .x = 1\n    show .x")

    def test_missing_end_while(self):
        with self.assertRaises(ParseError):
            parse("while .x = true\n    ask .x")

    def test_missing_end_repeat(self):
        with self.assertRaises(ParseError):
            parse("repeat 3 times\n    show loop")

    def test_attempt_missing_end_fail(self):
        with self.assertRaises(ParseError):
            parse("attempt\n    ask .x\nif fail\n    show fail reason\nend attempt")

    def test_non_set_in_container_raises(self):
        with self.assertRaises(ParseError):
            parse("#english\n    show .greeting")

    def test_error_includes_line_number(self):
        src = "set .x to 1\nset .y to 2\nblahblah .z"
        with self.assertRaises(ParseError) as ctx:
            parse(src)
        self.assertEqual(ctx.exception.line, 3)


if __name__ == "__main__":
    unittest.main(verbosity=2)
