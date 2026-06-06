#!/usr/bin/env python3
"""
Tests for the VERN tokenizer — English binding, v0.6 spec.

Run with:
    python test_tokenizer.py
"""

import sys
import os
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from tokenizer import tokenize, tokenize_file, Token, TokenizeError


def types(src: str):
    """Return just the token-type list for a source snippet."""
    return [t.type for t in tokenize(src)]


def pairs(src: str):
    """Return (type, value) pairs for a source snippet."""
    return [(t.type, t.value) for t in tokenize(src)]


class TestComments(unittest.TestCase):
    def test_full_line_comment(self):
        self.assertEqual(types("// this is a comment"), [])

    def test_inline_comment(self):
        toks = pairs('set .name to "Gabriel" // ignored')
        self.assertEqual(toks, [
            ("SET", "set"),
            ("REFERENCE", ".name"),
            ("TO", "to"),
            ("TEXT_LITERAL", "Gabriel"),
        ])

    def test_comment_marker_inside_string_is_safe(self):
        toks = pairs('show "hello // world"')
        self.assertEqual(toks, [("SHOW", "show"), ("TEXT_LITERAL", "hello // world")])

    def test_blank_lines_skipped(self):
        self.assertEqual(types("\n\n  \n"), [])


class TestLiterals(unittest.TestCase):
    def test_number_integer(self):
        self.assertEqual(pairs("set .x to 42"), [
            ("SET","set"), ("REFERENCE",".x"), ("TO","to"), ("NUMBER_LITERAL","42"),
        ])

    def test_number_decimal(self):
        toks = pairs("set .x to 3.14")
        self.assertIn(("NUMBER_LITERAL", "3.14"), toks)

    def test_date_literal(self):
        toks = pairs("set .birthday to 1990-03-15")
        self.assertIn(("DATE_LITERAL", "1990-03-15"), toks)

    def test_time_literal(self):
        toks = pairs("set .alarm to 07:30:00")
        self.assertIn(("TIME_LITERAL", "07:30:00"), toks)

    def test_text_literal_preserves_case_and_spaces(self):
        toks = pairs('show "Hello World"')
        self.assertIn(("TEXT_LITERAL", "Hello World"), toks)

    def test_text_literal_preserves_reserved_words(self):
        toks = pairs('show "set to show"')
        self.assertIn(("TEXT_LITERAL", "set to show"), toks)

    def test_date_not_broken_into_numbers(self):
        toks = pairs("set .d to 2026-12-31")
        type_list = [t for t, _ in toks]
        self.assertIn("DATE_LITERAL", type_list)
        self.assertNotIn("MINUS", type_list)

    def test_time_not_broken_into_numbers(self):
        toks = pairs("set .t to 14:30:00")
        type_list = [t for t, _ in toks]
        self.assertIn("TIME_LITERAL", type_list)
        self.assertNotIn("COLON", type_list)

    def test_math_minus_not_date(self):
        # 100-5 is not a date — numbers tokenize as two numbers with MINUS
        toks = pairs("set .x to 100 - 5")
        type_list = [t for t, _ in toks]
        self.assertIn("MINUS", type_list)
        self.assertNotIn("DATE_LITERAL", type_list)


class TestReferences(unittest.TestCase):
    def test_simple_reference(self):
        self.assertIn(("REFERENCE", ".name"), pairs("show .name"))

    def test_chain_reference(self):
        toks = pairs("run .cleanup.script.utilities.vern")
        self.assertIn(("REFERENCE", ".cleanup.script.utilities.vern"), toks)

    def test_file_reference(self):
        toks = pairs("import .utilities.vern")
        self.assertIn(("REFERENCE", ".utilities.vern"), toks)

    def test_script_reference(self):
        toks = pairs("start at .main.script")
        self.assertIn(("REFERENCE", ".main.script"), toks)

    def test_dot_period_not_standalone(self):
        # A lone period followed by a digit is not a reference — should raise
        with self.assertRaises(TokenizeError):
            tokenize("set .x to .3")


class TestContainerTags(unittest.TestCase):
    def test_container_tag(self):
        toks = pairs("run .greet.script #english")
        self.assertIn(("CONTAINER_TAG", "#english"), toks)

    def test_container_definition(self):
        toks = pairs("#english")
        self.assertEqual(toks, [("CONTAINER_TAG", "#english")])


class TestSymbols(unittest.TestCase):
    def test_eq(self):
        self.assertIn(("EQ", "="), pairs("if .x = 5 then show .x"))

    def test_neq(self):
        self.assertIn(("NEQ", "!="), pairs("if .x != 5 then show .x"))

    def test_gte(self):
        self.assertIn(("GTE", ">="), pairs("if .score >= 4 then show .score"))

    def test_lte(self):
        self.assertIn(("LTE", "<="), pairs("if .score <= 4 then show .score"))

    def test_plus(self):
        self.assertIn(("PLUS", "+"), pairs("set .x to .a + .b"))

    def test_minus(self):
        self.assertIn(("MINUS", "-"), pairs("set .x to .a - .b"))

    def test_star(self):
        self.assertIn(("STAR", "*"), pairs("set .x to .a * .b"))

    def test_slash(self):
        self.assertIn(("SLASH", "/"), pairs("set .x to .a / .b"))

    def test_comma(self):
        self.assertIn(("COMMA", ","), pairs("show .a, .b"))

    def test_colon_in_dict(self):
        toks = pairs('"alice" : 95')
        self.assertIn(("COLON", ":"), toks)


class TestCompoundKeywords(unittest.TestCase):
    """Compound tokens must be emitted as single atomic tokens."""

    def test_is_greater_than_or_equal_to(self):
        toks = pairs("if .x is greater than or equal to 10 then show .x")
        comp_types = [t for t, _ in toks]
        self.assertIn("IS_GREATER_THAN_OR_EQUAL_TO", comp_types)
        # Must NOT be broken into components
        self.assertNotIn("IS_GREATER_THAN", comp_types)

    def test_is_less_than_or_equal_to(self):
        toks = pairs("if .x is less than or equal to 10 then show .x")
        self.assertIn("IS_LESS_THAN_OR_EQUAL_TO", [t for t, _ in toks])

    def test_is_greater_than(self):
        toks = pairs("if .x is greater than 5 then show .x")
        type_list = [t for t, _ in toks]
        self.assertIn("IS_GREATER_THAN", type_list)
        self.assertNotIn("IS_GREATER_THAN_OR_EQUAL_TO", type_list)

    def test_is_less_than(self):
        self.assertIn("IS_LESS_THAN", types("if .x is less than 5 then show .x"))

    def test_is_equal_to(self):
        self.assertIn("IS_EQUAL_TO", types("if .x is equal to 5 then show .x"))

    def test_is_not(self):
        toks = pairs("if .x is not 5 then show .x")
        type_list = [t for t, _ in toks]
        self.assertIn("IS_NOT", type_list)
        # IS_NOT must not also emit bare IS
        self.assertNotIn("IS", type_list)

    def test_is_in(self):
        self.assertIn("IS_IN", types("if .x is in list names then show .x"))

    def test_not_in(self):
        self.assertIn("NOT_IN", types("if .x not in list names then show .x"))

    def test_current_item(self):
        toks = pairs("show current item")
        self.assertEqual([t for t, _ in toks], ["SHOW", "CURRENT_ITEM"])

    def test_current_key(self):
        toks = pairs("show current key")
        self.assertEqual([t for t, _ in toks], ["SHOW", "CURRENT_KEY"])

    def test_current_value(self):
        toks = pairs("show current value")
        self.assertEqual([t for t, _ in toks], ["SHOW", "CURRENT_VALUE"])

    def test_fail_reason(self):
        self.assertIn("FAIL_REASON", types("show fail reason"))

    def test_exit_loop(self):
        self.assertIn("EXIT_LOOP", types("exit loop"))

    def test_next_item(self):
        self.assertIn("NEXT_ITEM", types("next item"))

    def test_starts_with(self):
        self.assertIn("STARTS_WITH", types('if .text starts with "hello" then show "ok"'))

    def test_ends_with(self):
        self.assertIn("ENDS_WITH", types('if .text ends with "world" then show "ok"'))

    def test_repeat_through(self):
        self.assertIn("REPEAT_THROUGH", types("repeat through list names"))

    def test_attempt_all(self):
        self.assertIn("ATTEMPT_ALL", types("attempt all"))

    def test_start_at(self):
        self.assertIn("START_AT", types("start at .main.script"))

    def test_end_script(self):
        self.assertIn("END_SCRIPT", types("end script"))

    def test_end_list(self):
        self.assertIn("END_LIST", types("end list"))

    def test_end_dictionary(self):
        self.assertIn("END_DICTIONARY", types("end dictionary"))

    def test_end_repeat(self):
        self.assertIn("END_REPEAT", types("end repeat"))

    def test_end_while(self):
        self.assertIn("END_WHILE", types("end while"))

    def test_end_if(self):
        self.assertIn("END_IF", types("end if"))

    def test_end_attempt(self):
        self.assertIn("END_ATTEMPT", types("end attempt"))

    def test_end_fail(self):
        self.assertIn("END_FAIL", types("end fail"))

    def test_end_text(self):
        self.assertIn("END_TEXT", types("end text"))

    def test_if_fail(self):
        self.assertIn("IF_FAIL", types("if fail"))

    def test_pass_to(self):
        self.assertIn("PASS_TO", types("return .x pass to .result"))

    def test_type_of(self):
        self.assertIn("TYPE_OF", types("type of .value as .kind"))

    def test_length_of(self):
        self.assertIn("LENGTH_OF", types("length of .text as .result"))

    def test_to_degrees(self):
        self.assertIn("TO_DEGREES", types("to degrees .angle as .result"))

    def test_to_radians(self):
        self.assertIn("TO_RADIANS", types("to radians .angle as .result"))

    def test_difference_between(self):
        self.assertIn("DIFFERENCE_BETWEEN",
                      types("difference between .date1 and .date2 in days as .result"))

    def test_hyperbolic_sine(self):
        self.assertIn("HYPERBOLIC_SINE", types("hyperbolic sine .x as .result"))

    def test_arc_hyperbolic_cosine(self):
        self.assertIn("ARC_HYPERBOLIC_COSINE",
                      types("arc hyperbolic cosine .x as .result"))

    def test_arc_before_hyperbolic_greedy(self):
        # "arc hyperbolic sine" must win over "hyperbolic sine" alone
        toks = types("arc hyperbolic sine .x as .result")
        self.assertIn("ARC_HYPERBOLIC_SINE", toks)
        self.assertNotIn("HYPERBOLIC_SINE", toks)

    def test_is_greater_greedy_over_is_greater_than(self):
        # "is greater than or equal to" must win when the full phrase is present
        src = "if .x is greater than or equal to 5 then show .x"
        toks = types(src)
        self.assertIn("IS_GREATER_THAN_OR_EQUAL_TO", toks)
        self.assertNotIn("IS_GREATER_THAN", toks)


class TestCaseInsensitivity(unittest.TestCase):
    def test_keyword_upper(self):
        self.assertEqual(pairs("SET .x TO 1"), pairs("set .x to 1"))

    def test_keyword_mixed(self):
        self.assertEqual(pairs("Set .x To 1"), pairs("set .x to 1"))

    def test_compound_mixed_case(self):
        toks = types("IF .x IS GREATER THAN 5 THEN SHOW .x")
        self.assertIn("IS_GREATER_THAN", toks)

    def test_text_literal_preserves_case(self):
        toks = pairs('show "Gabriel"')
        self.assertIn(("TEXT_LITERAL", "Gabriel"), toks)
        # Should NOT be lowercased
        self.assertNotIn(("TEXT_LITERAL", "gabriel"), toks)


class TestIdentifiers(unittest.TestCase):
    def test_list_name_is_identifier(self):
        # In "list names", "names" is an IDENTIFIER
        toks = pairs("list names")
        self.assertEqual(toks, [("LIST", "list"), ("IDENTIFIER", "names")])

    def test_dictionary_name_is_identifier(self):
        toks = pairs("dictionary scores")
        self.assertEqual(toks, [("DICTIONARY", "dictionary"), ("IDENTIFIER", "scores")])

    def test_script_name_in_reference(self):
        # Script name appears in a reference chain, not bare
        self.assertIn(("REFERENCE", ".greet.script"), pairs("run .greet.script"))


class TestTextBlock(unittest.TestCase):
    def test_text_block_content_is_text_line(self):
        src = "text .welcome\n    hello world\n    second line\nend text"
        toks = tokenize(src)
        types_list = [t.type for t in toks]
        self.assertIn("TEXT_LINE", types_list)
        self.assertIn("END_TEXT", types_list)

    def test_reserved_words_in_text_block_are_raw(self):
        src = "text .msg\n    set show if repeat\nend text"
        toks = tokenize(src)
        # The middle line must be TEXT_LINE, not tokenized as keywords
        text_lines = [t for t in toks if t.type == "TEXT_LINE"]
        self.assertEqual(len(text_lines), 1)
        self.assertIn("set show if repeat", text_lines[0].value)

    def test_text_block_closes_correctly(self):
        src = "text .msg\n    content\nend text\nshow .msg"
        toks = tokenize(src)
        type_list = [t.type for t in toks]
        self.assertIn("END_TEXT", type_list)
        self.assertIn("SHOW", type_list)


class TestErrorHandling(unittest.TestCase):
    def test_unknown_token_raises(self):
        with self.assertRaises(TokenizeError) as ctx:
            tokenize("set .x to @invalid")
        self.assertIn("Line", str(ctx.exception))  # line info present

    def test_unterminated_string_raises(self):
        with self.assertRaises(TokenizeError):
            tokenize('show "unterminated')

    def test_error_records_line_number(self):
        src = "set .x to 1\nset .y to 2\nset .z to @bad"
        with self.assertRaises(TokenizeError) as ctx:
            tokenize(src)
        self.assertEqual(ctx.exception.line, 3)


class TestExamplePrograms(unittest.TestCase):
    """Every example program from the spec must tokenize without error."""

    examples_dir = os.path.join(os.path.dirname(__file__), "examples")

    def _tokenize_example(self, filename):
        path = os.path.join(self.examples_dir, filename)
        tokens = tokenize_file(path)
        self.assertGreater(len(tokens), 0, f"{filename} produced no tokens")
        return tokens

    def test_calculator(self):
        toks = self._tokenize_example("calculator.vern")
        type_list = [t.type for t in toks]
        # Must contain key structures
        self.assertIn("START_AT", type_list)
        self.assertIn("END_SCRIPT", type_list)
        self.assertIn("STOP", type_list)
        # Compound comparison operators
        self.assertIn("EQ", type_list)
        # OR keyword present
        self.assertIn("OR", type_list)

    def test_quiz(self):
        toks = self._tokenize_example("quiz.vern")
        type_list = [t.type for t in toks]
        self.assertIn("SET", type_list)
        self.assertIn("ASK", type_list)
        self.assertIn("GTE", type_list)
        self.assertIn("END_SCRIPT", type_list)

    def test_days_until(self):
        toks = self._tokenize_example("days_until.vern")
        type_list = [t.type for t in toks]
        self.assertIn("DATE_LITERAL", type_list)
        self.assertIn("DIFFERENCE_BETWEEN", type_list)
        self.assertIn("START_AT", type_list)

    def test_name_registry(self):
        toks = self._tokenize_example("name_registry.vern")
        type_list = [t.type for t in toks]
        self.assertIn("LIST", type_list)
        self.assertIn("REPEAT_THROUGH", type_list)
        self.assertIn("CURRENT_ITEM", type_list)
        self.assertIn("PUT", type_list)

    def test_safe_input(self):
        toks = self._tokenize_example("safe_input.vern")
        type_list = [t.type for t in toks]
        self.assertIn("ATTEMPT", type_list)
        self.assertIn("IF_FAIL", type_list)
        self.assertIn("END_FAIL", type_list)
        self.assertIn("END_ATTEMPT", type_list)
        self.assertIn("WHILE", type_list)
        self.assertIn("END_WHILE", type_list)

    def test_localization(self):
        toks = self._tokenize_example("localization.vern")
        type_list = [t.type for t in toks]
        self.assertIn("CONTAINER_TAG", type_list)
        self.assertIn("START_AT", type_list)
        # Container tags on run calls
        container_tags = [t.value for t in toks if t.type == "CONTAINER_TAG"]
        self.assertIn("#english", container_tags)
        self.assertIn("#spanish", container_tags)
        self.assertIn("#swahili", container_tags)


class TestSpecificInstructions(unittest.TestCase):
    """Spot-check individual instructions from the spec."""

    def test_set(self):
        toks = pairs("set .score to 0")
        self.assertEqual(toks, [
            ("SET","set"), ("REFERENCE",".score"), ("TO","to"), ("NUMBER_LITERAL","0"),
        ])

    def test_show_multiple(self):
        toks = pairs("show .name, .score")
        self.assertEqual(toks, [
            ("SHOW","show"),
            ("REFERENCE",".name"), ("COMMA",","),
            ("REFERENCE",".score"),
        ])

    def test_convert(self):
        toks = pairs("convert .input to number as .value")
        self.assertEqual(toks, [
            ("CONVERT","convert"), ("REFERENCE",".input"),
            ("TO","to"), ("NUMBER","number"),
            ("AS","as"), ("REFERENCE",".value"),
        ])

    def test_run_with_container(self):
        toks = pairs("run .greet.script #english")
        self.assertEqual(toks, [
            ("RUN","run"), ("REFERENCE",".greet.script"), ("CONTAINER_TAG","#english"),
        ])

    def test_repeat_n_times(self):
        toks = pairs("repeat 5 times")
        self.assertEqual(toks, [
            ("REPEAT","repeat"), ("NUMBER_LITERAL","5"), ("TIMES","times"),
        ])

    def test_put_in_list(self):
        toks = pairs("put .input in list names")
        self.assertEqual(toks, [
            ("PUT","put"), ("REFERENCE",".input"),
            ("IN","in"), ("LIST","list"), ("IDENTIFIER","names"),
        ])

    def test_count_list(self):
        toks = pairs("count list names as .total")
        self.assertEqual(toks, [
            ("COUNT","count"), ("LIST","list"), ("IDENTIFIER","names"),
            ("AS","as"), ("REFERENCE",".total"),
        ])

    def test_string_concat(self):
        toks = pairs('"hello " + .name')
        self.assertEqual(toks, [
            ("TEXT_LITERAL","hello "), ("PLUS","+"), ("REFERENCE",".name"),
        ])

    def test_math_constants(self):
        self.assertIn("PI", types("set .x to pi * .r"))
        self.assertIn("E", types("set .x to e power 2"))
        self.assertIn("TAU", types("set .x to tau"))
        self.assertIn("INFINITY", types("if .x is less than infinity then show .x"))

    def test_format_date(self):
        toks = pairs('format .today as .display using "DD/MO/YYYY"')
        type_list = [t for t, _ in toks]
        self.assertIn("FORMAT", type_list)
        self.assertIn("USING", type_list)

    def test_format_number_decimals(self):
        toks = pairs("format .price as .display decimals 2")
        type_list = [t for t, _ in toks]
        self.assertIn("FORMAT", type_list)
        self.assertIn("DECIMALS", type_list)

    def test_dictionary_declaration(self):
        src = 'dictionary scores\n    "alice" : 95\nend dictionary'
        toks = tokenize(src)
        type_list = [t.type for t in toks]
        self.assertIn("DICTIONARY", type_list)
        self.assertIn("TEXT_LITERAL", type_list)
        self.assertIn("COLON", type_list)
        self.assertIn("NUMBER_LITERAL", type_list)
        self.assertIn("END_DICTIONARY", type_list)

    def test_sort_descending(self):
        toks = pairs("sort list scores descending as list rankedscores")
        type_list = [t for t, _ in toks]
        self.assertIn("SORT", type_list)
        self.assertIn("DESCENDING", type_list)

    def test_script_takes(self):
        toks = pairs("script .greet takes .name")
        type_list = [t for t, _ in toks]
        self.assertIn("SCRIPT", type_list)
        self.assertIn("TAKES", type_list)
        self.assertIn("REFERENCE", type_list)

    def test_fetch(self):
        toks = pairs("fetch .url as .response")
        type_list = [t for t, _ in toks]
        self.assertIn("FETCH", type_list)

    def test_send(self):
        toks = pairs("send .payload to .url")
        type_list = [t for t, _ in toks]
        self.assertIn("SEND", type_list)

    def test_type_of_current_item(self):
        toks = pairs("type of current item as .kind")
        type_list = [t for t, _ in toks]
        self.assertIn("TYPE_OF", type_list)
        self.assertIn("CURRENT_ITEM", type_list)

    def test_return_pass_to(self):
        toks = pairs("return .total pass to .answer")
        type_list = [t for t, _ in toks]
        self.assertIn("RETURN", type_list)
        self.assertIn("PASS_TO", type_list)

    def test_exist_condition(self):
        toks = pairs("if .records.vern exist then show .name")
        type_list = [t for t, _ in toks]
        self.assertIn("EXIST", type_list)

    def test_split(self):
        toks = pairs('split .csv by "," as list parts')
        type_list = [t for t, _ in toks]
        self.assertIn("SPLIT", type_list)
        self.assertIn("BY", type_list)

    def test_join(self):
        toks = pairs('join list names by ", " as .result')
        type_list = [t for t, _ in toks]
        self.assertIn("JOIN", type_list)


if __name__ == "__main__":
    unittest.main(verbosity=2)
