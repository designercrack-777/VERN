#!/usr/bin/env python3
"""VERN executor — walks the AST and runs the program."""

import math
import os
import sys
import random as _random
from collections import OrderedDict
from typing import Any, Dict, List, Optional

from ast_nodes import *
from parser import parse_file
from error_logger import VernLogger


# ── Signals ────────────────────────────────────────────────────────────────────

class StopSignal(Exception):
    pass

class ExitLoopSignal(Exception):
    pass

class NextItemSignal(Exception):
    pass

class ReturnSignal(Exception):
    def __init__(self, value, dest: ValueRef):
        self.value = value
        self.dest = dest

class FatalError(Exception):
    def __init__(self, msg: str, line: int = 0):
        self.msg = msg
        self.line = line
        super().__init__(f"Fatal error (line {line}): {msg}")

class RecoverableError(Exception):
    def __init__(self, msg: str, line: int = 0):
        self.msg = msg
        self.line = line


# ── Executor ───────────────────────────────────────────────────────────────────

class VernExecutor:
    def __init__(self, program_path: str, logger: Optional[VernLogger] = None):
        self.program_path = os.path.abspath(program_path)
        self.program_dir = os.path.dirname(self.program_path)
        self.file_scope: Dict[str, Any] = {}
        self.lists: Dict[str, list] = {}
        self.dicts: Dict[str, OrderedDict] = {}
        self.scripts: Dict[str, ScriptDef] = {}
        self.containers: Dict[str, Dict[str, Any]] = {}
        self.imported: List['VernExecutor'] = []
        self.logger: Optional[VernLogger] = logger
        self._loading_files: set = set()  # for circular import detection

    # ── Entry point ────────────────────────────────────────────────────────────

    def run_program(self, program: Program):
        # Phase 1: register scripts and containers (so they're available anywhere)
        for node in program.body:
            if isinstance(node, ScriptDef):
                key = node.name.ref
                self.scripts[key] = node
            elif isinstance(node, ContainerDef):
                tag = node.tag.lstrip('#')
                self.containers[tag] = {}
                for instr in node.body:
                    if isinstance(instr, SetInstr):
                        val = self._eval_expr(instr.value, {}, None, None)
                        name = self._ref_name(instr.target)
                        self.containers[tag][name] = val

        # Phase 2: execute top-to-bottom
        try:
            self._exec_body(program.body, self.file_scope, None, None, top_level=True)
        except StopSignal:
            pass

    # ── Body / node execution ──────────────────────────────────────────────────

    def _exec_body(self, body, scope, loop_ctx, container_tag, top_level=False):
        for node in body:
            if top_level and isinstance(node, (ScriptDef, ContainerDef)):
                continue
            self._exec_node(node, scope, loop_ctx, container_tag)

    def _exec_node(self, node, scope, loop_ctx, container_tag):  # noqa: C901
        t = type(node)

        # ── Assignment ────────────────────────────────────────────────────────

        if t is SetInstr:
            val = self._eval_expr(node.value, scope, loop_ctx, container_tag)
            self._set_var(node.target, val, scope)

        # ── Output ────────────────────────────────────────────────────────────

        elif t is ShowInstr:
            for v in node.values:
                val = self._eval_expr(v, scope, loop_ctx, container_tag)
                print(self._to_display(val))

        # ── Input ─────────────────────────────────────────────────────────────

        elif t is AskInstr:
            try:
                user_input = input()
            except EOFError:
                user_input = ""
            self._set_var(node.target, user_input, scope)

        # ── File I/O ──────────────────────────────────────────────────────────

        elif t is ReadInstr:
            path = self._resolve_file_ref(node.source)
            filename = os.path.basename(path)
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    # Strip platform line endings; skip trailing blank created by
                    # a file that ends with a newline (standard VERN write format).
                    raw = [ln.rstrip('\r\n') for ln in f.readlines()]
                    lines = [ln for ln in raw if ln != ''] if raw and raw[-1] == '' \
                            else raw
                    # More robustly: keep ALL lines including empties except a
                    # trailing empty line left by the final newline.
                    lines = raw
                    if lines and lines[-1] == '':
                        lines = lines[:-1]
            except FileNotFoundError:
                raise FatalError(
                    f"Cannot read '{filename}' — the file does not exist.", node.line)
            except PermissionError:
                raise FatalError(
                    f"Cannot read '{filename}' — permission denied.", node.line)
            if len(lines) < len(node.targets):
                raise FatalError(
                    f"Cannot read '{filename}' — the file has {len(lines)} "
                    f"line(s) but {len(node.targets)} value(s) were requested.",
                    node.line)
            for i, target in enumerate(node.targets):
                self._set_var(target, lines[i], scope)

        elif t is WriteInstr:
            path = self._resolve_file_ref(node.dest)
            filename = os.path.basename(path)
            parent_dir = os.path.dirname(path)
            if parent_dir and not os.path.isdir(parent_dir):
                raise FatalError(
                    f"Cannot write '{filename}' — the folder does not exist: "
                    f"{parent_dir}", node.line)
            content = [self._to_display(self._eval_expr(v, scope, loop_ctx, container_tag))
                       for v in node.values]
            try:
                with open(path, 'w', encoding='utf-8') as f:
                    # One value per line, always end with newline so append
                    # and subsequent reads work correctly.
                    f.write('\n'.join(content) + '\n')
            except PermissionError:
                raise FatalError(
                    f"Cannot write '{filename}' — permission denied.", node.line)

        elif t is AppendInstr:
            path = self._resolve_file_ref(node.dest)
            filename = os.path.basename(path)
            parent_dir = os.path.dirname(path)
            if parent_dir and not os.path.isdir(parent_dir):
                raise FatalError(
                    f"Cannot append to '{filename}' — the folder does not exist: "
                    f"{parent_dir}", node.line)
            content = [self._to_display(self._eval_expr(v, scope, loop_ctx, container_tag))
                       for v in node.values]
            try:
                with open(path, 'a', encoding='utf-8') as f:
                    f.write('\n'.join(content) + '\n')
            except PermissionError:
                raise FatalError(
                    f"Cannot append to '{filename}' — permission denied.", node.line)

        elif t is DeleteInstr:
            path = self._resolve_file_ref(node.path)
            filename = os.path.basename(path)
            if not os.path.exists(path):
                raise FatalError(
                    f"Cannot delete '{filename}' — the file does not exist. "
                    f"Use 'if .{filename} exist' to check before deleting.",
                    node.line)
            try:
                os.remove(path)
            except PermissionError:
                raise FatalError(
                    f"Cannot delete '{filename}' — permission denied.", node.line)

        elif t is GetFilesInstr:
            folder = self._resolve_folder_ref(node.folder)
            if os.path.isdir(folder):
                # Return only files (not subdirectories), sorted for consistency
                files = sorted(
                    f for f in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder, f))
                )
            else:
                files = []
            self.lists[node.result_list] = files

        # ── Control flow ──────────────────────────────────────────────────────

        elif t is StopInstr:
            raise StopSignal()

        elif t is StartAt:
            script_node = self._find_script(node.script)
            self._exec_script(script_node, [], None, container_tag)

        elif t is RunInstr:
            script_node = self._find_script(node.script)
            args = [self._eval_expr(a, scope, loop_ctx, container_tag) for a in node.args]
            self._exec_script(script_node, args, node.container, container_tag)

        elif t is ReturnInstr:
            val = self._eval_expr(node.value, scope, loop_ctx, container_tag)
            raise ReturnSignal(val, node.dest)

        elif t is ImportInstr:
            self._handle_import(node)

        # ── Conditionals ──────────────────────────────────────────────────────

        elif t is IfInline:
            if self._eval_cond(node.condition, scope, loop_ctx, container_tag):
                self._exec_node(node.action, scope, loop_ctx, container_tag)

        elif t is IfBlock:
            if self._eval_cond(node.condition, scope, loop_ctx, container_tag):
                self._exec_body(node.then_body, scope, loop_ctx, container_tag)
            elif node.else_body:
                self._exec_body(node.else_body, scope, loop_ctx, container_tag)

        # ── Loops ─────────────────────────────────────────────────────────────

        elif t is WhileBlock:
            iteration = 0
            while self._eval_cond(node.condition, scope, loop_ctx, container_tag):
                iteration += 1
                try:
                    self._exec_body(node.body, scope, ('while', iteration), container_tag)
                except ExitLoopSignal:
                    break
                except NextItemSignal:
                    continue

        elif t is RepeatTimesBlock:
            count = int(self._to_number(
                self._eval_expr(node.count, scope, loop_ctx, container_tag), node.line))
            for i in range(1, count + 1):
                try:
                    self._exec_body(node.body, scope, ('repeat', i), container_tag)
                except ExitLoopSignal:
                    break
                except NextItemSignal:
                    continue

        elif t is RepeatThroughListBlock:
            lst = self._get_list(node.list_name, node.file_ref)
            iteration = 0
            for item in list(lst):
                iteration += 1
                try:
                    self._exec_body(node.body, scope,
                                    ('list', iteration, item, lst), container_tag)
                except ExitLoopSignal:
                    break
                except NextItemSignal:
                    continue

        elif t is RepeatThroughDictBlock:
            d = self._get_dict(node.dict_name, node.file_ref)
            iteration = 0
            for k, v in list(d.items()):
                iteration += 1
                try:
                    self._exec_body(node.body, scope,
                                    ('dict', iteration, k, v), container_tag)
                except ExitLoopSignal:
                    break
                except NextItemSignal:
                    continue

        elif t is ExitLoopInstr:
            if loop_ctx is None:
                raise FatalError("exit loop: used outside a loop block", node.line)
            raise ExitLoopSignal()

        elif t is NextItemInstr:
            if loop_ctx is None:
                raise FatalError("next item: used outside a loop block", node.line)
            raise NextItemSignal()

        # ── Error recovery ────────────────────────────────────────────────────

        elif t is AttemptBlock:
            self._exec_attempt(node, scope, loop_ctx, container_tag)

        # ── Type ops ──────────────────────────────────────────────────────────

        elif t is ConvertInstr:
            src = self._eval_expr(node.source, scope, loop_ctx, container_tag)
            result = self._convert(src, node.target_type, node.line)
            self._set_var(node.result, result, scope)

        elif t is TypeOfInstr:
            val = self._eval_expr(node.source, scope, loop_ctx, container_tag)
            self._set_var(node.result, self._type_name(val), scope)

        # ── Collections ───────────────────────────────────────────────────────

        elif t is ListDecl:
            items = []
            for item_expr in node.items:
                if isinstance(item_expr, str):
                    # Dictionary reference by name
                    if item_expr in self.dicts:
                        items.append(self.dicts[item_expr])
                    else:
                        raise FatalError(f"list: '{item_expr}' is not a declared dictionary",
                                         node.line)
                else:
                    items.append(self._eval_expr(item_expr, scope, loop_ctx, container_tag))
            self.lists[node.name] = items

        elif t is DictDecl:
            d: OrderedDict = OrderedDict()
            seen_keys = set()
            for key_expr, val_expr in node.pairs:
                k = self._eval_expr(key_expr, scope, loop_ctx, container_tag)
                if k in seen_keys:
                    raise FatalError(f"dictionary: duplicate key '{k}'", node.line)
                seen_keys.add(k)
                # Check if val_expr is a bare identifier referencing a dict
                if isinstance(val_expr, str):
                    if val_expr in self.dicts:
                        d[str(k)] = self.dicts[val_expr]
                    else:
                        raise FatalError(f"dictionary: '{val_expr}' is not a declared dictionary",
                                         node.line)
                else:
                    d[str(k)] = self._eval_expr(val_expr, scope, loop_ctx, container_tag)
            self.dicts[node.name] = d

        elif t is TextBlockDecl:
            content = '\n'.join(node.content_lines)
            name = self._ref_name(node.name)
            self.file_scope[name] = content

        elif t is PutInList:
            val = self._eval_expr(node.value, scope, loop_ctx, container_tag)
            lst = self._get_list_mut(node.list_name, node.file_ref, node.line)
            if lst:
                expected = self._type_name(lst[0])
                actual = self._type_name(val)
                if actual != expected:
                    display_val = self._to_display(val)
                    raise FatalError(
                        f"Cannot add '{display_val}' ({actual}) to list '{node.list_name}' "
                        f"— the list already contains {expected} values.", node.line)
            lst.append(val)

        elif t is PutInDict:
            val = self._eval_expr(node.value, scope, loop_ctx, container_tag)
            key = str(self._eval_expr(node.key, scope, loop_ctx, container_tag))
            if isinstance(node.dict_ref, str):
                d = self._get_dict(node.dict_ref, True, node.line)  # searches imports
            else:
                d = self._eval_expr(node.dict_ref, scope, loop_ctx, container_tag)
            # Type homogeneity check — all values in a dictionary must be the same type
            if d:
                existing_type = self._type_name(next(iter(d.values())))
                actual_type = self._type_name(val)
                if actual_type != existing_type:
                    dict_label = node.dict_ref if isinstance(node.dict_ref, str) else 'inline'
                    raise FatalError(
                        f"Cannot add a {actual_type} value to dictionary '{dict_label}' "
                        f"— the dictionary already contains {existing_type} values.",
                        node.line)
            d[key] = val

        elif t is PutDictInList:
            d = self.dicts.get(node.dict_name)
            if d is None:
                raise FatalError(f"dictionary '{node.dict_name}' not found", node.line)
            self.lists[node.list_name].append(d)

        elif t is PutDictInDict:
            d = self.dicts.get(node.dict_name)
            if d is None:
                raise FatalError(f"dictionary '{node.dict_name}' not found", node.line)
            key = str(self._eval_expr(node.key, scope, loop_ctx, container_tag))
            self.dicts[node.target_dict][key] = d

        elif t is RemoveFromList:
            val = self._eval_expr(node.value, scope, loop_ctx, container_tag)
            lst = self._get_list_mut(node.list_name, node.file_ref, node.line)
            if val in lst:
                lst.remove(val)
            else:
                display_val = self._to_display(val)
                self._log(
                    f"remove: '{display_val}' was not found in list '{node.list_name}' "
                    f"— nothing was removed.", node.line)

        elif t is RemoveKeyFromDict:
            key = str(self._eval_expr(node.key, scope, loop_ctx, container_tag))
            d = self._get_dict(node.dict_name, True, node.line)  # searches imports
            if key in d:
                del d[key]
            else:
                self._log(
                    f"remove key: key '{key}' not found in dictionary '{node.dict_name}' "
                    f"— nothing was removed.", node.line)

        elif t is GetListItem:
            pos = int(self._to_number(
                self._eval_expr(node.position, scope, loop_ctx, container_tag), node.line))
            lst = self._get_list(node.list_name, node.file_ref)
            if pos < 1 or pos > len(lst):
                raise FatalError(
                    f"Cannot get position {pos} from list '{node.list_name}' "
                    f"— the list has {len(lst)} item(s). Positions begin at 1.", node.line)
            self._set_var(node.result, lst[pos - 1], scope)

        elif t is GetDictItem:
            key = str(self._eval_expr(node.key, scope, loop_ctx, container_tag))
            if isinstance(node.dict_ref, str):
                d = self._get_dict(node.dict_ref, True, node.line)  # searches imports
            else:
                d = self._eval_expr(node.dict_ref, scope, loop_ctx, container_tag)
            if key not in d:
                raise FatalError(
                    f"get dictionary: key '{key}' not found in dictionary "
                    f"'{node.dict_ref if isinstance(node.dict_ref, str) else 'inline'}'.",
                    node.line)
            self._set_var(node.result, d[key], scope)

        elif t is CountList:
            lst = self._get_list(node.list_name, node.file_ref)
            self._set_var(node.result, float(len(lst)), scope)

        elif t is CountDict:
            d = self._get_dict(node.dict_name, True, node.line)  # searches imports
            self._set_var(node.result, float(len(d)), scope)

        elif t is SortList:
            if node.result_name not in self.lists:
                raise FatalError(
                    f"Cannot sort: target list '{node.result_name}' must be declared "
                    f"before sort is called.", node.line)
            lst = self.lists.get(node.list_name, [])
            if not lst:
                self.lists[node.result_name] = []
            else:
                lst_type = self._type_name(lst[0])
                if lst_type == 'dictionary':
                    raise FatalError(
                        f"Cannot sort list '{node.list_name}' — "
                        f"sorting a list of dictionaries is not supported.", node.line)
                try:
                    # Dates and times are tuples ('date'/'time', 'YYYY-MM-DD'/'HH:MM:SS').
                    # Sort by the value string — both formats are lexicographically ordered.
                    if isinstance(lst[0], tuple):
                        key_fn = lambda x: x[1]
                    else:
                        key_fn = None
                    self.lists[node.result_name] = sorted(lst, key=key_fn, reverse=node.descending)
                except TypeError as e:
                    raise FatalError(
                        f"Cannot sort list '{node.list_name}': {e}", node.line)

        elif t is ReverseList:
            if node.result_name not in self.lists:
                raise FatalError(
                    f"Cannot reverse: target list '{node.result_name}' must be declared "
                    f"before reverse is called.", node.line)
            lst = self.lists.get(node.list_name, [])
            self.lists[node.result_name] = lst[::-1]

        elif t is SliceList:
            if node.result_name not in self.lists:
                raise FatalError(
                    f"Cannot slice: target list '{node.result_name}' must be declared "
                    f"before slice is called.", node.line)
            lst = self.lists.get(node.list_name, [])
            start = int(self._to_number(
                self._eval_expr(node.start, scope, loop_ctx, container_tag), node.line))
            end = int(self._to_number(
                self._eval_expr(node.end, scope, loop_ctx, container_tag), node.line))
            if start > end:
                raise FatalError(
                    f"Cannot slice list '{node.list_name}': start position ({start}) "
                    f"is greater than end position ({end}).", node.line)
            if start < 1 or end > len(lst):
                raise FatalError(
                    f"Cannot slice list '{node.list_name}': positions {start}–{end} "
                    f"are out of range (list has {len(lst)} item(s)). Positions begin at 1.",
                    node.line)
            self.lists[node.result_name] = lst[start - 1:end]

        elif t is CombineList:
            if node.result not in self.lists:
                raise FatalError(
                    f"Cannot combine: target list '{node.result}' must be declared "
                    f"before combine is called.", node.line)
            first = self.lists.get(node.first, [])
            second = self.lists.get(node.second, [])
            if first and second:
                first_type = self._type_name(first[0])
                second_type = self._type_name(second[0])
                if first_type != second_type:
                    raise FatalError(
                        f"Cannot combine list '{node.first}' ({first_type}) "
                        f"with list '{node.second}' ({second_type}) "
                        f"— both lists must contain the same type.", node.line)
            self.lists[node.result] = first + second

        # ── Extended math ─────────────────────────────────────────────────────

        elif t is RoundInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            d = (int(self._to_number(
                self._eval_expr(node.decimals, scope, loop_ctx, container_tag), node.line))
                 if node.decimals is not None else 0)
            result = round(val, d) if d > 0 else float(round(val))
            if node.result:
                self._set_var(node.result, result, scope)

        elif t is FloorInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            d = (int(self._to_number(
                self._eval_expr(node.decimals, scope, loop_ctx, container_tag), node.line))
                 if node.decimals is not None else 0)
            factor = 10 ** d
            result = math.floor(val * factor) / factor
            if node.result:
                self._set_var(node.result, result, scope)

        elif t is CeilingInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            d = (int(self._to_number(
                self._eval_expr(node.decimals, scope, loop_ctx, container_tag), node.line))
                 if node.decimals is not None else 0)
            factor = 10 ** d
            result = math.ceil(val * factor) / factor
            if node.result:
                self._set_var(node.result, result, scope)

        elif t is RandomInstr:
            mn = int(self._to_number(
                self._eval_expr(node.min_val, scope, loop_ctx, container_tag), node.line))
            mx = int(self._to_number(
                self._eval_expr(node.max_val, scope, loop_ctx, container_tag), node.line))
            if mn > mx:
                raise FatalError("random: min bound greater than max bound", node.line)
            self._set_var(node.result, float(_random.randint(mn, mx)), scope)

        elif t is AbsoluteInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            self._set_var(node.result, abs(val), scope)

        elif t is MinMaxInstr:
            if isinstance(node.operands, str):
                lst = self.lists.get(node.operands, [])
                if not lst:
                    raise FatalError(f"{node.op} on empty list", node.line)
                nums = [self._to_number(x, node.line) for x in lst]
                result = min(nums) if node.op == 'minimum' else max(nums)
            else:
                v1 = self._to_number(
                    self._eval_expr(node.operands[0], scope, loop_ctx, container_tag), node.line)
                v2 = self._to_number(
                    self._eval_expr(node.operands[1], scope, loop_ctx, container_tag), node.line)
                result = min(v1, v2) if node.op == 'minimum' else max(v1, v2)
            self._set_var(node.result, float(result), scope)

        elif t is PercentInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            total = self._to_number(
                self._eval_expr(node.total, scope, loop_ctx, container_tag), node.line)
            if total == 0:
                raise FatalError("percent: zero total", node.line)
            self._set_var(node.result, (val / total) * 100.0, scope)

        elif t is SumInstr:
            lst = self.lists.get(node.list_name, [])
            self._set_var(node.result,
                          float(sum(self._to_number(x, node.line) for x in lst)), scope)

        elif t is FactorialInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            if val < 0 or val != int(val):
                raise FatalError("factorial: requires non-negative whole number", node.line)
            self._set_var(node.result, float(math.factorial(int(val))), scope)

        elif t is CombinationsInstr:
            n = int(self._to_number(
                self._eval_expr(node.n, scope, loop_ctx, container_tag), node.line))
            k = int(self._to_number(
                self._eval_expr(node.k, scope, loop_ctx, container_tag), node.line))
            self._set_var(node.result, float(math.comb(n, k)), scope)

        elif t is PermutationsInstr:
            n = int(self._to_number(
                self._eval_expr(node.n, scope, loop_ctx, container_tag), node.line))
            k = int(self._to_number(
                self._eval_expr(node.k, scope, loop_ctx, container_tag), node.line))
            self._set_var(node.result, float(math.perm(n, k)), scope)

        elif t is SignInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            result = 0.0 if val == 0 else (1.0 if val > 0 else -1.0)
            self._set_var(node.result, result, scope)

        # ── Trig / log / angle ────────────────────────────────────────────────

        elif t is TrigInstr:
            args = [self._to_number(self._eval_expr(a, scope, loop_ctx, container_tag), node.line)
                    for a in node.args]
            result = self._exec_trig(node.func, args, node.use_radians, node.line)
            self._set_var(node.result, result, scope)

        elif t is LnInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            if val <= 0:
                raise FatalError("ln: value must be positive", node.line)
            self._set_var(node.result, math.log(val), scope)

        elif t is LogInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            if val <= 0:
                raise FatalError("log: value must be positive", node.line)
            if node.base is not None:
                base = self._to_number(
                    self._eval_expr(node.base, scope, loop_ctx, container_tag), node.line)
                if base <= 0 or base == 1:
                    raise FatalError("log: base must be positive and not 1", node.line)
                result = math.log(val, base)
            else:
                result = math.log10(val)
            self._set_var(node.result, result, scope)

        elif t is AngleConvInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            if node.direction == 'radians':
                result = math.radians(val)
            else:
                result = math.degrees(val)
            self._set_var(node.result, result, scope)

        # ── String ops ────────────────────────────────────────────────────────

        elif t is LengthOfInstr:
            val = self._eval_expr(node.value, scope, loop_ctx, container_tag)
            if not isinstance(val, str):
                raise FatalError(f"length of: expected text, got {self._type_name(val)}", node.line)
            self._set_var(node.result, float(len(val)), scope)

        elif t is FindInstr:
            pattern = self._eval_expr(node.pattern, scope, loop_ctx, container_tag)
            text = self._eval_expr(node.text, scope, loop_ctx, container_tag)
            if not isinstance(text, str):
                raise FatalError(
                    f"find: the text to search must be a text value, "
                    f"got {self._type_name(text)}.", node.line)
            if not isinstance(pattern, str):
                raise FatalError(
                    f"find: the search pattern must be a text value, "
                    f"got {self._type_name(pattern)}.", node.line)
            pos = text.find(pattern)
            self._set_var(node.result, float(pos + 1) if pos >= 0 else 0.0, scope)

        elif t is ExtractInstr:
            text = str(self._eval_expr(node.text, scope, loop_ctx, container_tag))
            beg = int(self._to_number(
                self._eval_expr(node.beginning, scope, loop_ctx, container_tag), node.line))
            fin = int(self._to_number(
                self._eval_expr(node.finishing, scope, loop_ctx, container_tag), node.line))
            if beg < 1 or fin > len(text) or beg > fin:
                raise FatalError(
                    f"extract: positions {beg}-{fin} out of range (length {len(text)})", node.line)
            self._set_var(node.result, text[beg - 1:fin], scope)

        elif t is ReplaceInstr:
            old = self._eval_expr(node.old, scope, loop_ctx, container_tag)
            new = self._eval_expr(node.new, scope, loop_ctx, container_tag)
            text = self._eval_expr(node.text, scope, loop_ctx, container_tag)
            if not isinstance(text, str):
                raise FatalError(
                    f"replace: the text value must be text, "
                    f"got {self._type_name(text)}.", node.line)
            if not isinstance(old, str):
                raise FatalError(
                    f"replace: the search value must be text, "
                    f"got {self._type_name(old)}.", node.line)
            if not isinstance(new, str):
                raise FatalError(
                    f"replace: the replacement value must be text, "
                    f"got {self._type_name(new)}.", node.line)
            if old in text:
                result = text.replace(old, new, 1)
            else:
                result = text
                self._log(f"replace: '{old}' not found in text — original assigned unchanged.",
                          node.line)
            self._set_var(node.result, result, scope)

        elif t is SplitInstr:
            if node.result_list not in self.lists:
                raise FatalError(
                    f"Cannot split: target list '{node.result_list}' must be declared "
                    f"before split is called.", node.line)
            text = self._eval_expr(node.text, scope, loop_ctx, container_tag)
            if not isinstance(text, str):
                raise FatalError(
                    f"split: the value to split must be text, "
                    f"got {self._type_name(text)}.", node.line)
            delim = str(self._eval_expr(node.delimiter, scope, loop_ctx, container_tag))
            if not delim:
                raise FatalError("split: delimiter cannot be empty.", node.line)
            self.lists[node.result_list] = text.split(delim) if text else []

        elif t is JoinInstr:
            lst = self._get_list(node.list_name, True)
            sep = str(self._eval_expr(node.separator, scope, loop_ctx, container_tag))
            if lst and not isinstance(lst[0], str):
                raise FatalError(
                    f"join: list '{node.list_name}' contains {self._type_name(lst[0])} values "
                    f"— join requires a text list.", node.line)
            self._set_var(node.result, sep.join(lst), scope)

        elif t is TrimInstr:
            val = str(self._eval_expr(node.text, scope, loop_ctx, container_tag))
            self._set_var(node.result, val.strip(), scope)

        elif t is UppercaseInstr:
            val = str(self._eval_expr(node.text, scope, loop_ctx, container_tag))
            self._set_var(node.result, val.upper(), scope)

        elif t is LowercaseInstr:
            val = str(self._eval_expr(node.text, scope, loop_ctx, container_tag))
            self._set_var(node.result, val.lower(), scope)

        # ── Date / time ───────────────────────────────────────────────────────

        elif t is GetDateInstr:
            from datetime import date
            self._set_var(node.result, ('date', date.today().strftime('%Y-%m-%d')), scope)

        elif t is GetTimeInstr:
            from datetime import datetime
            self._set_var(node.result, ('time', datetime.now().strftime('%H:%M:%S')), scope)

        elif t is DiffBetweenInstr:
            v1 = self._eval_expr(node.first, scope, loop_ctx, container_tag)
            v2 = self._eval_expr(node.second, scope, loop_ctx, container_tag)
            self._set_var(node.result, self._diff_between(v1, v2, node.unit, node.line), scope)

        elif t is FormatDateTimeInstr:
            val = self._eval_expr(node.value, scope, loop_ctx, container_tag)
            fmt = str(self._eval_expr(node.fmt, scope, loop_ctx, container_tag))
            self._set_var(node.result, self._format_datetime(val, fmt, node.line), scope)

        elif t is FormatNumberInstr:
            val = self._to_number(
                self._eval_expr(node.value, scope, loop_ctx, container_tag), node.line)
            result = self._format_number(val, node.decimals, node.thousands, node.padded,
                                         scope, loop_ctx, container_tag, node.line)
            self._set_var(node.result, result, scope)

        # ── Networking ────────────────────────────────────────────────────────

        elif t is FetchInstr:
            url = self._eval_expr(node.url, scope, loop_ctx, container_tag)
            if not isinstance(url, str):
                raise FatalError(
                    f"fetch: URL must be a text value, got {self._type_name(url)}.", node.line)
            try:
                import urllib.request
                with urllib.request.urlopen(url) as resp:
                    content = resp.read().decode('utf-8', errors='replace')
                self._set_var(node.result, content, scope)
            except FatalError:
                raise
            except Exception as e:
                raise FatalError(f"fetch failed: {e}", node.line)

        elif t is SendInstr:
            data = self._eval_expr(node.data, scope, loop_ctx, container_tag)
            url = self._eval_expr(node.url, scope, loop_ctx, container_tag)
            if not isinstance(data, str):
                raise FatalError(
                    f"send: data must be a text value, got {self._type_name(data)}.", node.line)
            if not isinstance(url, str):
                raise FatalError(
                    f"send: URL must be a text value, got {self._type_name(url)}.", node.line)
            try:
                import urllib.request
                req = urllib.request.Request(url, data=data.encode('utf-8'), method='POST')
                urllib.request.urlopen(req)
            except FatalError:
                raise
            except Exception as e:
                raise FatalError(f"send failed: {e}", node.line)

        # ── Misc ──────────────────────────────────────────────────────────────

        elif t is DefineInstr:
            pass  # extensible vocabulary — deferred

        else:
            pass  # unknown node — silently skip

    # ── Script execution ───────────────────────────────────────────────────────

    def _exec_script(self, script_node: ScriptDef, args: list,
                     run_container: Optional[str], caller_container: Optional[str]):
        scope: Dict[str, Any] = {}

        # Bind parameters
        if args and not script_node.params:
            raise FatalError(
                f"script '{script_node.name.ref}' takes no parameters but "
                f"{len(args)} value(s) were passed", script_node.line)
        if script_node.params and len(args) != len(script_node.params):
            raise FatalError(
                f"script '{script_node.name.ref}' expects {len(script_node.params)} "
                f"parameter(s), got {len(args)}", script_node.line)
        for param, val in zip(script_node.params, args):
            scope[self._ref_name(param)] = val

        # Container priority: run-level > script-definition
        effective_container = (self._strip_tag(run_container) or
                               self._strip_tag(script_node.container))

        try:
            self._exec_body(script_node.body, scope, None, effective_container)
        except ReturnSignal as rs:
            dest_name = self._ref_name(rs.dest)
            self.file_scope[dest_name] = rs.value
        # StopSignal propagates naturally

    def _find_script(self, script_ref: ValueRef) -> ScriptDef:
        ref = script_ref.ref  # e.g. ".greet" or ".greet.script" or ".calculation.script"
        # Extract the script name (first part)
        parts = [p for p in ref.split('.') if p]
        name = parts[0]
        key = '.' + name

        if key in self.scripts:
            return self.scripts[key]
        # Try exact match
        if ref in self.scripts:
            return self.scripts[ref]
        # Try imported executors
        for imp in self.imported:
            try:
                return imp._find_script(script_ref)
            except FatalError:
                pass
        raise FatalError(f"script not found: {ref}", script_ref.line)

    # ── Attempt block ──────────────────────────────────────────────────────────

    @staticmethod
    def _instr_result_name(instr) -> Optional[str]:
        """Return the variable name this instruction writes to, for dependency tracking."""
        # Most instructions expose their output as 'result' (a ValueRef)
        result = getattr(instr, 'result', None)
        if result is not None and hasattr(result, 'ref'):
            return result.ref.lstrip('.').split('.')[0]
        # SetInstr writes to 'target'
        target = getattr(instr, 'target', None)
        if target is not None and hasattr(target, 'ref'):
            return target.ref.lstrip('.').split('.')[0]
        # ReadInstr writes to the first of 'targets'
        targets = getattr(instr, 'targets', None)
        if targets and hasattr(targets[0], 'ref'):
            return targets[0].ref.lstrip('.').split('.')[0]
        return None

    def _exec_attempt(self, node: AttemptBlock, scope, loop_ctx, container_tag):
        if node.try_all:
            failures = []
            tainted: set = set()   # names of values that failed to initialize
            for instr in node.body:
                try:
                    self._exec_node(instr, scope, loop_ctx, container_tag)
                except (FatalError, RecoverableError) as e:
                    msg = e.msg if hasattr(e, 'msg') else str(e)
                    line = e.line if hasattr(e, 'line') else 0
                    # Dependent failure: "undefined value: .name" where .name was tainted
                    if msg.startswith('undefined value: .') and tainted:
                        ref_name = msg[len('undefined value: .'):].split('.')[0]
                        if ref_name in tainted:
                            msg = (f"could not execute — depends on .{ref_name} "
                                   f"which failed to initialize")
                    # Mark this instruction's output target as tainted
                    out = self._instr_result_name(instr)
                    if out:
                        tainted.add(out)
                    if self.logger:
                        self.logger.fatal(msg, line, recovered=True)
                    failures.append(msg)
            for fail_msg in failures:
                fail_scope = dict(scope)
                fail_scope['__fail_reason__'] = fail_msg
                self._exec_body(node.fail_body, fail_scope, loop_ctx, container_tag)
        else:
            try:
                self._exec_body(node.body, scope, loop_ctx, container_tag)
            except (FatalError, RecoverableError) as e:
                msg = e.msg if hasattr(e, 'msg') else str(e)
                line = e.line if hasattr(e, 'line') else 0
                if self.logger:
                    self.logger.fatal(msg, line, recovered=True)
                fail_scope = dict(scope)
                fail_scope['__fail_reason__'] = msg
                self._exec_body(node.fail_body, fail_scope, loop_ctx, container_tag)

    # ── Expression evaluation ──────────────────────────────────────────────────

    def _eval_expr(self, expr, scope, loop_ctx, container_tag):  # noqa: C901
        t = type(expr)

        if t is TextLit:
            return expr.value

        elif t is NumberLit:
            return float(expr.value)

        elif t is DateLit:
            return ('date', expr.value)

        elif t is TimeLit:
            return ('time', expr.value)

        elif t is BoolLit:
            return expr.value  # Python True/False

        elif t is Constant:
            return {'pi': math.pi, 'e': math.e, 'tau': math.tau,
                    'infinity': math.inf}[expr.name]

        elif t is LoopVar:
            if loop_ctx is None:
                raise FatalError("loop: used outside loop block", expr.line)
            return float(loop_ctx[1])

        elif t is CurrentItem:
            if loop_ctx is None or loop_ctx[0] != 'list':
                raise FatalError("current item: used outside repeat through list block", expr.line)
            return loop_ctx[2]

        elif t is CurrentKey:
            if loop_ctx is None or loop_ctx[0] != 'dict':
                raise FatalError("current key: used outside repeat through dictionary block",
                                 expr.line)
            return loop_ctx[2]

        elif t is CurrentValue:
            if loop_ctx is None or loop_ctx[0] != 'dict':
                raise FatalError("current value: used outside repeat through dictionary block",
                                 expr.line)
            return loop_ctx[3]

        elif t is FailReason:
            reason = scope.get('__fail_reason__')
            if reason is None:
                raise FatalError("fail reason: used outside if fail block", expr.line)
            return reason

        elif t is ValueRef:
            return self._resolve_ref(expr, scope, loop_ctx, container_tag)

        elif t is BinOp:
            left = self._eval_expr(expr.left, scope, loop_ctx, container_tag)
            right = self._eval_expr(expr.right, scope, loop_ctx, container_tag)
            return self._apply_binop(expr.op, left, right, expr.line)

        else:
            raise FatalError(f"unknown expression type: {t.__name__}", 0)

    # ── Condition evaluation ───────────────────────────────────────────────────

    def _eval_cond(self, cond, scope, loop_ctx, container_tag) -> bool:  # noqa: C901
        t = type(cond)

        if t is BoolLit:
            return cond.value

        elif t is ValueRef:
            val = self._resolve_ref(cond, scope, loop_ctx, container_tag)
            if type(val) is not bool:
                raise FatalError(
                    f"condition: expected true/false value, got {self._type_name(val)}", cond.line)
            return val

        elif t is Comparison:
            left = self._eval_expr(cond.left, scope, loop_ctx, container_tag)
            right = self._eval_expr(cond.right, scope, loop_ctx, container_tag)
            return self._compare(cond.op, left, right, cond.line)

        elif t is MemberCheck:
            val = self._eval_expr(cond.value, scope, loop_ctx, container_tag)
            if cond.collection_kind == 'list':
                lst = self._get_list(cond.collection, cond.file_ref)
                result = val in lst
            elif cond.collection_kind == 'dictionary':
                d = self.dicts.get(cond.collection, OrderedDict())
                result = str(val) in d
            else:  # text
                text = self._eval_expr(cond.collection, scope, loop_ctx, container_tag)
                result = str(val) in str(text)
            return (not result) if cond.negated else result

        elif t is ExistCheck:
            # exist works for both files (.name.vern) and directories (.name.folder, .parent)
            ref_str = cond.ref.ref
            parts = [p for p in ref_str.split('.') if p]
            if parts and parts[-1] in ('folder', 'parent'):
                path = self._resolve_folder_ref(cond.ref)
            else:
                path = self._resolve_file_ref(cond.ref)
            return os.path.exists(path)

        elif t is StartsWithCond:
            text = str(self._eval_expr(cond.ref, scope, loop_ctx, container_tag))
            pat = str(self._eval_expr(cond.pattern, scope, loop_ctx, container_tag))
            return text.startswith(pat)

        elif t is EndsWithCond:
            text = str(self._eval_expr(cond.ref, scope, loop_ctx, container_tag))
            pat = str(self._eval_expr(cond.pattern, scope, loop_ctx, container_tag))
            return text.endswith(pat)

        elif t is NotCond:
            return not self._eval_cond(cond.cond, scope, loop_ctx, container_tag)

        elif t is AndCond:
            return (self._eval_cond(cond.left, scope, loop_ctx, container_tag) and
                    self._eval_cond(cond.right, scope, loop_ctx, container_tag))

        elif t is OrCond:
            return (self._eval_cond(cond.left, scope, loop_ctx, container_tag) or
                    self._eval_cond(cond.right, scope, loop_ctx, container_tag))

        else:
            raise FatalError(f"unknown condition type: {t.__name__}", 0)

    # ── Reference resolution ───────────────────────────────────────────────────

    @staticmethod
    def _strip_tag(tag: Optional[str]) -> Optional[str]:
        """Normalize container tag by removing leading '#'."""
        if tag is None:
            return None
        return tag.lstrip('#') or None

    def _resolve_ref(self, vref: ValueRef, scope, loop_ctx, container_tag):
        name = self._ref_name(vref)
        effective_tag = self._strip_tag(vref.container) or self._strip_tag(container_tag)

        # Container lookup first
        if effective_tag and effective_tag in self.containers:
            c = self.containers[effective_tag]
            if name in c:
                return c[name]
            # Fall through to untagged baseline

        # Script scope
        if name in scope:
            return scope[name]

        # File scope
        if name in self.file_scope:
            return self.file_scope[name]

        # Imported executors
        for imp in self.imported:
            try:
                return imp._resolve_simple(name, effective_tag)
            except FatalError:
                pass

        raise FatalError(f"undefined value: .{name}", vref.line)

    def _resolve_simple(self, name: str, container_tag: Optional[str]):
        if container_tag and container_tag in self.containers:
            c = self.containers[container_tag]
            if name in c:
                return c[name]
        if name in self.file_scope:
            return self.file_scope[name]
        raise FatalError(f"undefined value: .{name}")

    def _set_var(self, vref: ValueRef, value, scope):
        name = self._ref_name(vref)
        # If already in current script scope, update there
        if name in scope and scope is not self.file_scope:
            scope[name] = value
        # If in file scope, update there
        elif name in self.file_scope:
            self.file_scope[name] = value
        # Otherwise create in current scope
        else:
            scope[name] = value

    @staticmethod
    def _ref_name(vref: ValueRef) -> str:
        """Extract the simple value name from a ValueRef."""
        return vref.ref.lstrip('.').split('.')[0]

    # ── Binary operators ───────────────────────────────────────────────────────

    def _apply_binop(self, op: str, left, right, line: int):
        if op == '+':
            if isinstance(left, str) and isinstance(right, str):
                return left + right
            elif isinstance(left, float) and isinstance(right, float):
                return left + right
            elif type(left) is bool or type(right) is bool:
                raise FatalError(f"+: cannot add true/false values", line)
            else:
                raise FatalError(
                    f"+: type mismatch ({self._type_name(left)}, {self._type_name(right)})", line)
        elif op == '-':
            return self._to_number(left, line) - self._to_number(right, line)
        elif op == '*':
            return self._to_number(left, line) * self._to_number(right, line)
        elif op == '/':
            r = self._to_number(right, line)
            if r == 0:
                raise FatalError("division by zero", line)
            return self._to_number(left, line) / r
        elif op == 'power':
            return self._to_number(left, line) ** self._to_number(right, line)
        elif op == 'root':
            n = self._to_number(right, line)
            v = self._to_number(left, line)
            if n % 2 == 0 and v < 0:
                raise FatalError("root: even root of negative number", line)
            return v ** (1.0 / n)
        elif op == 'remainder':
            r = self._to_number(right, line)
            if r == 0:
                raise FatalError("remainder: division by zero", line)
            return math.fmod(self._to_number(left, line), r)
        else:
            raise FatalError(f"unknown operator: {op}", line)

    # ── Comparison ─────────────────────────────────────────────────────────────

    def _compare(self, op: str, left, right, line: int) -> bool:
        # Normalize date/time tuples for comparison
        if isinstance(left, tuple):
            left = left[1]
        if isinstance(right, tuple):
            right = right[1]

        ops = {
            'IS_EQUAL_TO': lambda a, b: a == b,
            'EQ': lambda a, b: a == b,
            'IS_NOT': lambda a, b: a != b,
            'NEQ': lambda a, b: a != b,
            'IS_GREATER_THAN': lambda a, b: a > b,
            'GT': lambda a, b: a > b,
            'IS_LESS_THAN': lambda a, b: a < b,
            'LT': lambda a, b: a < b,
            'IS_GREATER_THAN_OR_EQUAL_TO': lambda a, b: a >= b,
            'GTE': lambda a, b: a >= b,
            'IS_LESS_THAN_OR_EQUAL_TO': lambda a, b: a <= b,
            'LTE': lambda a, b: a <= b,
        }
        fn = ops.get(op)
        if fn is None:
            raise FatalError(f"unknown comparison operator: {op}", line)
        try:
            return fn(left, right)
        except TypeError:
            raise FatalError(
                f"comparison: type mismatch ({self._type_name(left)}, {self._type_name(right)})",
                line)

    # ── Type helpers ───────────────────────────────────────────────────────────

    def _to_number(self, val, line: int = 0) -> float:
        if type(val) is bool:
            raise FatalError(f"expected number, got true/false", line)
        if isinstance(val, float):
            return val
        if isinstance(val, int):
            return float(val)
        raise FatalError(f"expected number, got {self._type_name(val)}", line)

    def _list_item_type(self, lst_name: str) -> Optional[str]:
        """Return the VERN type of items in a named list, or None if empty."""
        lst = self.lists.get(lst_name, [])
        return self._type_name(lst[0]) if lst else None

    def _type_name(self, val) -> str:
        if type(val) is bool:
            return 'true/false'
        if isinstance(val, float):
            return 'number'
        if isinstance(val, str):
            return 'text'
        if isinstance(val, tuple) and len(val) == 2 and val[0] in ('date', 'time'):
            return val[0]
        if isinstance(val, dict):
            return 'dictionary'
        return type(val).__name__

    def _to_display(self, val) -> str:
        if type(val) is bool:
            return 'true' if val else 'false'
        if isinstance(val, float):
            if val == int(val) and abs(val) < 1e15 and not math.isinf(val):
                return str(int(val))
            return str(val)
        if isinstance(val, tuple) and len(val) == 2:
            return val[1]
        if isinstance(val, str):
            return val
        return str(val)

    # ── Type conversion ────────────────────────────────────────────────────────

    def _convert(self, val, target_type: str, line: int):
        src = self._type_name(val)
        if target_type == 'number':
            if src == 'text':
                try:
                    return float(val)
                except ValueError:
                    raise FatalError(f"cannot convert '{val}' to number", line)
            raise FatalError(f"cannot convert {src} to number", line)
        elif target_type == 'text':
            if src == 'number':
                return self._to_display(val)
            if src in ('date', 'time'):
                return val[1]
            if src == 'true/false':
                return 'true' if val else 'false'
            return str(val)
        elif target_type == 'date':
            if src == 'text':
                import re
                if re.match(r'^\d{4}-\d{2}-\d{2}$', val):
                    return ('date', val)
                raise FatalError(f"cannot convert '{val}' to date: must be YYYY-MM-DD", line)
            raise FatalError(f"cannot convert {src} to date", line)
        elif target_type == 'time':
            if src == 'text':
                import re
                if re.match(r'^\d{2}:\d{2}:\d{2}$', val):
                    return ('time', val)
                raise FatalError(f"cannot convert '{val}' to time: must be HH:MI:SS", line)
            raise FatalError(f"cannot convert {src} to time", line)
        raise FatalError(f"unknown target type: {target_type}", line)

    # ── Trig ───────────────────────────────────────────────────────────────────

    def _exec_trig(self, func: str, args: list, use_radians: bool, line: int) -> float:
        simple = {'sine': math.sin, 'cosine': math.cos, 'tangent': math.tan}
        inverse = {'arcsine': math.asin, 'arccosine': math.acos, 'arctangent': math.atan}
        hyperbolic = {
            'hyperbolic sine': math.sinh, 'hyperbolic cosine': math.cosh,
            'hyperbolic tangent': math.tanh,
            'arc hyperbolic sine': math.asinh, 'arc hyperbolic cosine': math.acosh,
            'arc hyperbolic tangent': math.atanh,
        }

        try:
            if func in simple:
                # Tangent is undefined at 90° and 270°. Python float arithmetic means
                # math.tan(math.radians(90.0)) returns a large finite number rather than
                # inf, so we must pre-check the angle before computing.
                if func == 'tangent':
                    if use_radians:
                        norm = args[0] % (2 * math.pi)
                        if (abs(norm - math.pi / 2) < 1e-10 or
                                abs(norm - 3 * math.pi / 2) < 1e-10):
                            raise FatalError(
                                f"tangent: undefined at {args[0]:.6g} radians "
                                f"— tangent of 90° and 270° is undefined.", line)
                    else:
                        norm = args[0] % 360.0
                        if norm in (90.0, 270.0):
                            raise FatalError(
                                f"tangent: undefined at {args[0]:.4g}° "
                                f"— tangent of 90° and 270° is undefined.", line)
                angle = args[0] if use_radians else math.radians(args[0])
                return simple[func](angle)
            elif func == 'arctangent':
                if len(args) == 2:
                    r = math.atan2(args[0], args[1])
                else:
                    r = math.atan(args[0])
                return r if use_radians else math.degrees(r)
            elif func in inverse:
                r = inverse[func](args[0])
                return r if use_radians else math.degrees(r)
            elif func in hyperbolic:
                return hyperbolic[func](args[0])
            else:
                raise FatalError(f"unknown trig function: {func}", line)
        except FatalError:
            raise  # re-raise FatalErrors we raised ourselves above
        except ValueError:
            # Python math domain errors — convert each to a spec-matching FatalError
            domain_msgs = {
                'arcsine':
                    f"arcsine: value {args[0]} is outside the valid domain -1 to 1.",
                'arccosine':
                    f"arccosine: value {args[0]} is outside the valid domain -1 to 1.",
                'arc hyperbolic tangent':
                    f"arc hyperbolic tangent: value {args[0]} "
                    f"is outside the valid domain -1 to 1.",
                'arc hyperbolic cosine':
                    f"arc hyperbolic cosine: value {args[0]} "
                    f"must be 1 or greater.",
            }
            msg = domain_msgs.get(func, f"{func}: math domain error.")
            raise FatalError(msg, line)

    # ── Date/time helpers ──────────────────────────────────────────────────────

    def _diff_between(self, v1, v2, unit: str, line: int) -> float:
        if not (isinstance(v1, tuple) and isinstance(v2, tuple)):
            raise FatalError("difference between: values must be date or time", line)
        kind1, raw1 = v1
        kind2, raw2 = v2
        if kind1 != kind2:
            raise FatalError("difference between: type mismatch (date vs time)", line)
        if kind1 == 'date':
            from datetime import date
            d1 = date.fromisoformat(raw1)
            d2 = date.fromisoformat(raw2)
            return float(abs((d2 - d1).days))
        elif kind1 == 'time':
            from datetime import datetime
            t1 = datetime.strptime(raw1, '%H:%M:%S')
            t2 = datetime.strptime(raw2, '%H:%M:%S')
            diff_secs = abs((t2 - t1).total_seconds())
            if unit == 'hours':
                return diff_secs / 3600.0
            elif unit == 'minutes':
                return diff_secs / 60.0
            else:
                raise FatalError(f"difference between: unknown unit '{unit}'", line)
        raise FatalError(f"difference between: unknown kind '{kind1}'", line)

    def _format_datetime(self, val, fmt_str: str, line: int) -> str:
        import re as _re
        if not isinstance(val, tuple):
            raise FatalError("format: value is not date or time", line)
        kind, raw = val
        if kind == 'date':
            # Detect invalid codes BEFORE replacement to avoid substring collisions
            # (e.g. "MONTH" contains valid code "MO" — must catch "MONTH" as invalid).
            valid = {'YYYY', 'MO', 'DD'}
            found = set(_re.findall(r'[A-Z]{2,}', fmt_str))
            unknown = sorted(found - valid)
            if unknown:
                self._log(
                    f"format date: unrecognized format code(s) {unknown} "
                    f"— passed through as literal text.", line)
            year, mo, dd = raw.split('-')
            return fmt_str.replace('YYYY', year).replace('MO', mo).replace('DD', dd)
        elif kind == 'time':
            valid = {'HH', 'MI', 'SS'}
            found = set(_re.findall(r'[A-Z]{2,}', fmt_str))
            unknown = sorted(found - valid)
            if unknown:
                self._log(
                    f"format time: unrecognized format code(s) {unknown} "
                    f"— passed through as literal text.", line)
            hh, mi, ss = raw.split(':')
            return fmt_str.replace('HH', hh).replace('MI', mi).replace('SS', ss)
        raise FatalError(f"format: unknown kind '{kind}'", line)

    def _format_number(self, val: float, decimals_expr, thousands: bool,
                       padded_expr, scope, loop_ctx, container_tag, line: int) -> str:
        # Apply decimals first
        if decimals_expr is not None:
            raw_d = self._to_number(
                self._eval_expr(decimals_expr, scope, loop_ctx, container_tag), line)
            if raw_d != int(raw_d):
                raise FatalError(
                    f"format: decimals value must be a whole number, "
                    f"got {self._to_display(raw_d)}.", line)
            d = int(raw_d)
            if d < 0:
                raise FatalError(
                    f"format: decimals value must be 0 or greater, got {d}.", line)
            s = f"{val:.{d}f}"
        else:
            if val == int(val) and not math.isinf(val):
                s = str(int(val))
            else:
                s = str(val)

        # Apply thousands separator
        if thousands:
            dot_idx = s.find('.')
            if dot_idx >= 0:
                int_part = s[:dot_idx]
                dec_part = s[dot_idx:]
            else:
                int_part = s
                dec_part = ''
            neg = int_part.startswith('-')
            digits = int_part[1:] if neg else int_part
            groups = []
            while digits:
                groups.append(digits[-3:])
                digits = digits[:-3]
            int_formatted = (','.join(reversed(groups)))
            if neg:
                int_formatted = '-' + int_formatted
            s = int_formatted + dec_part

        # Apply padding
        if padded_expr is not None:
            raw_p = self._to_number(
                self._eval_expr(padded_expr, scope, loop_ctx, container_tag), line)
            if raw_p != int(raw_p):
                raise FatalError(
                    f"format: padded value must be a whole number, "
                    f"got {self._to_display(raw_p)}.", line)
            p = int(raw_p)
            if p <= 0:
                raise FatalError(
                    f"format: padded value must be greater than 0, got {p}.", line)
            s = s.rjust(p)

        return s

    # ── Collection accessors ───────────────────────────────────────────────────

    def _get_list(self, name: str, file_ref) -> list:
        if name in self.lists:
            return self.lists[name]
        if file_ref is not None:
            for imp in self.imported:
                if name in imp.lists:
                    return imp.lists[name]
        raise FatalError(f"list '{name}' not found")

    def _get_list_mut(self, name: str, file_ref, line: int) -> list:
        if name in self.lists:
            return self.lists[name]
        if file_ref is not None:
            for imp in self.imported:
                if name in imp.lists:
                    return imp.lists[name]
        raise FatalError(f"list '{name}' not found", line)

    def _get_dict(self, name: str, file_ref, line: int = 0) -> OrderedDict:
        if name in self.dicts:
            return self.dicts[name]
        if file_ref is not None:
            for imp in self.imported:
                if name in imp.dicts:
                    return imp.dicts[name]
        raise FatalError(f"dictionary '{name}' not found", line)

    def _get_dict_mut(self, name: str, line: int) -> OrderedDict:
        if name in self.dicts:
            return self.dicts[name]
        raise FatalError(f"dictionary '{name}' not found", line)

    # ── File path resolution ───────────────────────────────────────────────────

    def _parse_ref_chain(self, ref: str, line: int = 0):
        """
        Parse a VERN period-chain reference into (file_name, folders, use_parent).

        Chain reads most-specific → least-specific, e.g.:
          .data.vern.backups.folder.docs.folder.parent
          → file 'data.vern' inside docs/backups/ from system root

        The returned folders list is already reversed into filesystem order
        (least-specific first), so os.path.join(base, *folders, file_name) works.

        Validates:
          - .parent may appear at most once (spec §File Operations)
        """
        parts = [p for p in ref.split('.') if p]
        file_name: Optional[str] = None
        folders: List[str] = []
        parent_count = 0
        i = 0
        while i < len(parts):
            if parts[i] == 'parent':
                parent_count += 1
                if parent_count > 1:
                    raise FatalError(
                        "Invalid file reference: '.parent' may appear only once "
                        "in a path chain.", line)
                i += 1
            elif i + 1 < len(parts) and parts[i + 1] == 'vern':
                file_name = parts[i] + '.vern'
                i += 2
            elif i + 1 < len(parts) and parts[i + 1] == 'folder':
                folders.append(parts[i])
                i += 2
            else:
                # Bare name with no recognised descriptor — treat as folder name
                # (handles .parent alone, or partial chains passed for exist checks)
                folders.append(parts[i])
                i += 1
        folders.reverse()   # most→least specific → least→most specific (fs order)
        use_parent = parent_count > 0
        return file_name, folders, use_parent

    def _resolve_file_ref(self, vref: ValueRef) -> str:
        """Resolve a VERN file reference to an absolute filesystem path."""
        ref = vref.ref
        line = vref.line

        # Fast path: simple same-directory reference  .name.vern
        parts = [p for p in ref.split('.') if p]
        if len(parts) == 2 and parts[1] == 'vern':
            return os.path.join(self.program_dir, parts[0] + '.vern')

        file_name, folders, use_parent = self._parse_ref_chain(ref, line)
        if use_parent:
            # System root — os.path.abspath(os.sep) gives C:\ on Windows, / on Unix
            base = os.path.abspath(os.sep)
        else:
            base = self.program_dir
        components = folders + ([file_name] if file_name else [])
        return os.path.join(base, *components) if components else base

    def _resolve_folder_ref(self, vref: ValueRef) -> str:
        """Resolve a VERN folder reference to an absolute filesystem path."""
        ref = vref.ref
        line = vref.line
        _, folders, use_parent = self._parse_ref_chain(ref, line)
        if use_parent:
            base = os.path.abspath(os.sep)
        else:
            base = self.program_dir
        return os.path.join(base, *folders) if folders else base

    # ── Import ─────────────────────────────────────────────────────────────────

    def _handle_import(self, node: ImportInstr):
        path = self._resolve_file_ref(node.path)
        if path in self._loading_files:
            raise FatalError(f"circular import: {path}", node.line)
        if not os.path.exists(path):
            raise FatalError(f"import: file not found: {path}", node.line)
        imp = VernExecutor(path, logger=self.logger)
        imp._loading_files = self._loading_files | {self.program_path}
        program = parse_file(path)
        imp.run_program(program)
        self.imported.append(imp)

    # ── Logging ────────────────────────────────────────────────────────────────

    def _log(self, msg: str, line: int = 0):
        """Record a non-fatal (warning) log entry."""
        if self.logger:
            self.logger.warning(msg, line)
        else:
            # Fallback: print to stderr when running without a logger
            label = f"[Line {line}] " if line else ""
            print(f"WARNING: {label}{msg}", file=sys.stderr)


# ── CLI ────────────────────────────────────────────────────────────────────────

def execute_file(path: str):
    """Parse and execute a VERN program, writing a log file if any errors occur."""
    from error_logger import VernLogger

    logger = VernLogger(path)
    program = parse_file(path)
    executor = VernExecutor(path, logger=logger)

    exit_code = 0
    try:
        executor.run_program(program)
        logger.completed = True
    except FatalError as e:
        # Unrecovered fatal — program halted
        logger.fatal(e.msg, e.line, recovered=False)
        # Print the error to the terminal so the user sees it immediately
        loc = f"Line {e.line}: " if e.line else ""
        print(f"\nFatal error — {loc}{e.msg}", file=sys.stderr)
        exit_code = 1
    except Exception as e:
        # Unexpected interpreter error (should not happen in production)
        logger.fatal(f"Internal interpreter error: {e}", 0, recovered=False)
        import traceback
        traceback.print_exc(file=sys.stderr)
        exit_code = 1

    # Write log file whenever there are any errors
    if logger.has_errors:
        log_path = logger.write_log()
        print(f"\nError log written to: {log_path}", file=sys.stderr)

    if exit_code:
        sys.exit(exit_code)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage: python executor.py <file.vern>", file=sys.stderr)
        sys.exit(1)
    execute_file(sys.argv[1])
