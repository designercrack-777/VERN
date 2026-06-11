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
        self.script_scopes: Dict[str, Dict[str, Any]] = {}  # persisted after execution
        self.containers: Dict[str, Dict[str, Any]] = {}
        self.imported: List['VernExecutor'] = []
        self.logger: Optional[VernLogger] = logger
        self._loading_files: set = set()  # for circular import detection

    # ── Entry point ────────────────────────────────────────────────────────────

    @staticmethod
    def _check_nesting_depth(value, depth: int = 1, max_depth: int = 4, path: str = '') -> None:
        """Recursively check that nested list/dict structures don't exceed max_depth."""
        if depth > max_depth:
            raise FatalError(
                f"data structure exceeds maximum nesting depth of {max_depth}"
                + (f" at {path}" if path else ""), 0)
        if isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, (dict, list)):
                    VernExecutor._check_nesting_depth(
                        v, depth + 1, max_depth, f"{path}.{k}" if path else str(k))
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, (dict, list)):
                    VernExecutor._check_nesting_depth(
                        item, depth + 1, max_depth, f"{path}[{i}]" if path else f"[{i}]")

    def run_program(self, program: Program):
        # Initialize return collector state
        self._return_collector: Optional[list] = None
        self._is_multi_return: bool = False

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
            if node.source_is_path:
                path = self._eval_expr(node.source, scope, loop_ctx, container_tag)
                if not isinstance(path, str):
                    raise FatalError(
                        f"read: path must be a text value, got {self._type_name(path)}",
                        node.line)
            else:
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
            if node.dest_is_path:
                path = self._eval_expr(node.dest, scope, loop_ctx, container_tag)
                if not isinstance(path, str):
                    raise FatalError(
                        f"write: path must be a text value, got {self._type_name(path)}",
                        node.line)
            else:
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
            if node.dest_is_path:
                path = self._eval_expr(node.dest, scope, loop_ctx, container_tag)
                if not isinstance(path, str):
                    raise FatalError(
                        f"append: path must be a text value, got {self._type_name(path)}",
                        node.line)
            else:
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
            if node.path_is_path:
                path = self._eval_expr(node.path, scope, loop_ctx, container_tag)
                if not isinstance(path, str):
                    raise FatalError(
                        f"delete: path must be a text value, got {self._type_name(path)}",
                        node.line)
            else:
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
            args = []
            for a in node.args:
                if isinstance(a, tuple):
                    args.append(a)   # ("list", name), ("dict", name), ("script", ref)
                else:
                    args.append(self._eval_expr(a, scope, loop_ctx, container_tag))
            self._exec_script(script_node, args, node.container, container_tag,
                              result_names=node.result_names if node.result_names else None)

        elif t is InvokeInstr:
            # invoke script parametername [with args] [as .result]
            script_def = scope.get(node.param_name)
            if script_def is None:
                raise FatalError(
                    f"invoke: script parameter '{node.param_name}' not found in scope",
                    node.line)
            if not isinstance(script_def, ScriptDef):
                raise FatalError(
                    f"invoke: '{node.param_name}' is not a script", node.line)
            args = []
            for a in node.args:
                if isinstance(a, tuple):
                    args.append(a)
                else:
                    args.append(self._eval_expr(a, scope, loop_ctx, container_tag))
            self._exec_script(script_def, args, None, container_tag,
                              result_names=node.result_names if node.result_names else None)

        elif t is ReturnInstr:
            val = self._eval_expr(node.value, scope, loop_ctx, container_tag)
            if node.dest is not None:
                # Form 1: return .value pass to .dest
                raise ReturnSignal(val, node.dest)
            else:
                # Form 2: bare return .value
                collector = getattr(self, '_return_collector', None)
                if collector is None:
                    raise FatalError(
                        "bare 'return' used outside a Form 2 script", node.line)
                collector.append(val)
                if not getattr(self, '_is_multi_return', False):
                    # Single-return: stop execution via signal
                    raise ReturnSignal(val, None)

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
            # list_name can be a str (declared list) or ValueRef (variable holding a list)
            if isinstance(node.list_name, ValueRef):
                lst = self._eval_expr(node.list_name, scope, loop_ctx, container_tag)
                if not isinstance(lst, list):
                    raise FatalError(
                        f"repeat through list: '{self._ref_name(node.list_name)}' "
                        f"is not a list", node.line)
            else:
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
            # dict_name can be a str (declared dict) or ValueRef (variable holding a dict)
            if isinstance(node.dict_name, ValueRef):
                d = self._eval_expr(node.dict_name, scope, loop_ctx, container_tag)
                if not isinstance(d, dict):
                    raise FatalError(
                        f"repeat through dictionary: '{self._ref_name(node.dict_name)}' "
                        f"is not a dictionary", node.line)
            else:
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
                import urllib.error
                req = urllib.request.Request(url)
                # Request headers
                if node.headers_dict:
                    hd = self._get_dict(node.headers_dict, None)
                    for k, v in hd.items():
                        req.add_header(str(k), str(v))
                content = ''
                status_code = 0
                resp_headers = {}
                try:
                    with urllib.request.urlopen(req) as resp:
                        content = resp.read().decode('utf-8', errors='replace')
                        status_code = resp.status
                        resp_headers = dict(resp.headers)
                except urllib.error.HTTPError as he:
                    # Non-200 status — not fatal; capture status if requested
                    content = he.read().decode('utf-8', errors='replace') if he.fp else ''
                    status_code = he.code
                    resp_headers = dict(he.headers) if he.headers else {}
                if node.result:
                    self._set_var(node.result, content, scope)
                if node.response_headers:
                    rh = OrderedDict((k, str(v)) for k, v in resp_headers.items())
                    rh_name = self._ref_name(node.response_headers)
                    self.dicts[rh_name] = rh
                    # Also store as a value so type of / set work on it
                    self._set_var(node.response_headers, rh, scope)
                if node.status:
                    self._set_var(node.status, float(status_code), scope)
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
                import urllib.request, urllib.error
                req = urllib.request.Request(url, data=data.encode('utf-8'), method='POST')
                if node.headers_dict:
                    hd = self._get_dict(node.headers_dict, None)
                    for k, v in hd.items():
                        req.add_header(str(k), str(v))
                status_code = 0
                try:
                    with urllib.request.urlopen(req) as resp:
                        status_code = resp.status
                except urllib.error.HTTPError as he:
                    status_code = he.code
                if node.status:
                    self._set_var(node.status, float(status_code), scope)
            except FatalError:
                raise
            except Exception as e:
                raise FatalError(f"send failed: {e}", node.line)

        elif t is UpdateInstr:
            data = self._eval_expr(node.data, scope, loop_ctx, container_tag)
            url = self._eval_expr(node.url, scope, loop_ctx, container_tag)
            if not isinstance(data, str):
                raise FatalError(
                    f"update: data must be a text value, got {self._type_name(data)}.", node.line)
            if not isinstance(url, str):
                raise FatalError(
                    f"update: URL must be a text value, got {self._type_name(url)}.", node.line)
            try:
                import urllib.request, urllib.error
                req = urllib.request.Request(url, data=data.encode('utf-8'), method='PUT')
                if node.headers_dict:
                    hd = self._get_dict(node.headers_dict, None)
                    for k, v in hd.items():
                        req.add_header(str(k), str(v))
                status_code = 0
                try:
                    with urllib.request.urlopen(req) as resp:
                        status_code = resp.status
                except urllib.error.HTTPError as he:
                    status_code = he.code
                if node.status:
                    self._set_var(node.status, float(status_code), scope)
            except FatalError:
                raise
            except Exception as e:
                raise FatalError(f"update failed: {e}", node.line)

        elif t is DeleteUrlInstr:
            url = self._eval_expr(node.url, scope, loop_ctx, container_tag)
            if not isinstance(url, str):
                raise FatalError(
                    f"delete: URL must be a text value, got {self._type_name(url)}.", node.line)
            try:
                import urllib.request, urllib.error
                req = urllib.request.Request(url, method='DELETE')
                if node.headers_dict:
                    hd = self._get_dict(node.headers_dict, None)
                    for k, v in hd.items():
                        req.add_header(str(k), str(v))
                status_code = 0
                try:
                    with urllib.request.urlopen(req) as resp:
                        status_code = resp.status
                except urllib.error.HTTPError as he:
                    status_code = he.code
                if node.status:
                    self._set_var(node.status, float(status_code), scope)
            except FatalError:
                raise
            except Exception as e:
                raise FatalError(f"delete failed: {e}", node.line)

        elif t is ParseInstr:
            self._exec_parse(node, scope, loop_ctx, container_tag)

        elif t is InspectInstr:
            self._exec_inspect(node, scope, loop_ctx, container_tag)

        # ── Misc ──────────────────────────────────────────────────────────────

        elif t is DefineInstr:
            pass  # extensible vocabulary — deferred

        else:
            pass  # unknown node — silently skip

    # ── Script execution ───────────────────────────────────────────────────────

    @staticmethod
    def _count_top_level_returns(body) -> int:
        """Count Form 2 (bare) return statements at the top level of a body."""
        return sum(1 for n in body if isinstance(n, ReturnInstr) and n.dest is None)

    def _exec_script(self, script_node: ScriptDef, args: list,
                     run_container: Optional[str], caller_container: Optional[str],
                     result_names=None):
        scope: Dict[str, Any] = {}

        # Bind parameters (supports plain, list, dict, script typed params)
        num_params = len(script_node.params)
        num_args = len(args)
        if num_args != num_params:
            raise FatalError(
                f"script '{script_node.name.ref}' expects {num_params} "
                f"parameter(s), got {num_args}", script_node.line)

        # Track temp list/dict bindings for cleanup
        temp_list_saves: Dict[str, Any] = {}
        temp_dict_saves: Dict[str, Any] = {}

        for param, arg in zip(script_node.params, args):
            if isinstance(param, tuple):
                kind, param_name = param
                if kind == 'list':
                    if not (isinstance(arg, tuple) and arg[0] == 'list'):
                        raise FatalError(
                            f"script '{script_node.name.ref}': parameter '{param_name}' "
                            f"expects a list argument", script_node.line)
                    arg_list_name = arg[1]
                    src = self._get_list(arg_list_name, None)
                    temp_list_saves[param_name] = self.lists.get(param_name)
                    self.lists[param_name] = src
                elif kind == 'dict':
                    if not (isinstance(arg, tuple) and arg[0] == 'dict'):
                        raise FatalError(
                            f"script '{script_node.name.ref}': parameter '{param_name}' "
                            f"expects a dictionary argument", script_node.line)
                    arg_dict_name = arg[1]
                    src = self._get_dict(arg_dict_name, None)
                    temp_dict_saves[param_name] = self.dicts.get(param_name)
                    self.dicts[param_name] = src
                elif kind == 'script':
                    if not (isinstance(arg, tuple) and arg[0] == 'script'):
                        raise FatalError(
                            f"script '{script_node.name.ref}': parameter '{param_name}' "
                            f"expects a script argument", script_node.line)
                    script_ref = arg[1]   # ValueRef
                    script_def = self._find_script(script_ref)
                    scope[param_name] = script_def
                else:
                    raise FatalError(f"unknown param kind: {kind}", script_node.line)
            else:
                # Plain ValueRef param
                scope[self._ref_name(param)] = arg

        # Determine if this script uses Form 2 multi-return
        num_returns = self._count_top_level_returns(script_node.body)
        is_multi = num_returns > 1

        # Save and set up return collector for Form 2
        old_collector = getattr(self, '_return_collector', None)
        old_is_multi = getattr(self, '_is_multi_return', False)
        self._return_collector: Optional[list] = []
        self._is_multi_return: bool = is_multi

        # Container priority: run-level > script-definition
        effective_container = (self._strip_tag(run_container) or
                               self._strip_tag(script_node.container))

        try:
            self._exec_body(script_node.body, scope, None, effective_container)
        except ReturnSignal as rs:
            if rs.dest is not None:
                # Form 1: return .value pass to .dest
                dest_name = self._ref_name(rs.dest)
                self.file_scope[dest_name] = rs.value
            # else: Form 2 single-return — value already appended to collector
        # StopSignal propagates naturally

        # Assign Form 2 results from collector
        if result_names and self._return_collector is not None:
            collector = self._return_collector
            if len(result_names) > len(collector):
                raise FatalError(
                    f"script '{script_node.name.ref}' returned {len(collector)} "
                    f"value(s) but {len(result_names)} were requested",
                    script_node.line)
            for i, rname in enumerate(result_names):
                dest_name = self._ref_name(rname)
                self.file_scope[dest_name] = collector[i]

        # Restore return collector
        self._return_collector = old_collector
        self._is_multi_return = old_is_multi

        # Restore temp list/dict bindings
        for name, old_val in temp_list_saves.items():
            if old_val is None:
                self.lists.pop(name, None)
            else:
                self.lists[name] = old_val
        for name, old_val in temp_dict_saves.items():
            if old_val is None:
                self.dicts.pop(name, None)
            else:
                self.dicts[name] = old_val

        # Persist scope so cross-script references (.val.scriptname.script) can resolve
        script_name = self._ref_name(script_node.name)
        self.script_scopes[script_name] = dict(scope)

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

    _FAIL_CATEGORIES = frozenset(('type', 'file', 'network', 'value'))

    @staticmethod
    def _classify_error(msg: str) -> str:
        """Classify an error message into one of the four fail categories."""
        m = msg.lower()
        if any(k in m for k in ('fetch', 'send', 'update', 'connection', 'network',
                                 'http', 'url', 'socket')):
            return 'network'
        if any(k in m for k in ('file', 'folder', 'read', 'write', 'append',
                                 'delete', 'permission', 'does not exist')):
            return 'file'
        if any(k in m for k in ('type mismatch', 'expected number', 'expected text',
                                 'cannot convert', 'type')):
            return 'type'
        return 'value'

    def _run_fail_handlers(self, msg: str, node: AttemptBlock,
                           scope, loop_ctx, container_tag):
        """Run the appropriate fail handler(s) for a given error message."""
        category = self._classify_error(msg)
        fail_scope = dict(scope)
        fail_scope['__fail_reason__'] = msg
        fail_scope['__fail_type__'] = category

        # Try typed handlers first
        for handler_category, handler_body in (node.typed_handlers or []):
            if handler_category == category:
                self._exec_body(handler_body, fail_scope, loop_ctx, container_tag)
                return

        # Fall back to catch-all
        if node.fail_body is not None:
            self._exec_body(node.fail_body, fail_scope, loop_ctx, container_tag)

    def _exec_attempt(self, node: AttemptBlock, scope, loop_ctx, container_tag):
        # Validate: no handler body at all means unhandled on fail
        has_handlers = bool(node.typed_handlers) or node.fail_body is not None

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
                self._run_fail_handlers(fail_msg, node, scope, loop_ctx, container_tag)
        else:
            try:
                self._exec_body(node.body, scope, loop_ctx, container_tag)
            except (FatalError, RecoverableError) as e:
                msg = e.msg if hasattr(e, 'msg') else str(e)
                line = e.line if hasattr(e, 'line') else 0
                if self.logger:
                    self.logger.fatal(msg, line, recovered=True)
                self._run_fail_handlers(msg, node, scope, loop_ctx, container_tag)

    # ── Parse / Inspect ───────────────────────────────────────────────────────

    def _exec_parse(self, node: ParseInstr, scope, loop_ctx, container_tag):
        """Execute a parse instruction — parses text into list or dictionary."""
        import json as _json
        import csv as _csv
        import xml.etree.ElementTree as _ET
        import configparser as _cp
        import io as _io

        source_val = self._eval_expr(node.source, scope, loop_ctx, container_tag)
        if not isinstance(source_val, str):
            raise FatalError(
                f"parse: source must be a text value, got {self._type_name(source_val)}",
                node.line)

        fmt = node.format.lower()
        result_type = node.result_type.lower()
        result_name = node.result_name

        try:
            if fmt == 'json':
                data = _json.loads(source_val)
                if result_type == 'dictionary':
                    if not isinstance(data, dict):
                        raise FatalError(
                            f"parse json: expected an object, got {type(data).__name__}",
                            node.line)
                    od = OrderedDict((str(k), str(v) if not isinstance(v, dict) else v)
                                     for k, v in data.items())
                    self.dicts[result_name] = od
                else:  # list
                    if not isinstance(data, list):
                        raise FatalError(
                            f"parse json: expected an array, got {type(data).__name__}",
                            node.line)
                    self.lists[result_name] = [str(i) if not isinstance(i, dict) else i
                                               for i in data]

            elif fmt == 'csv':
                if result_type != 'list':
                    raise FatalError("parse csv: result type must be 'list'", node.line)
                reader = _csv.DictReader(_io.StringIO(source_val))
                rows = []
                for row in reader:
                    rows.append(OrderedDict((k, str(v)) for k, v in row.items()))
                self.lists[result_name] = rows

            elif fmt == 'xml':
                if result_type != 'dictionary':
                    raise FatalError("parse xml: result type must be 'dictionary'", node.line)
                root = _ET.fromstring(source_val)
                od = OrderedDict()
                for child in root:
                    od[child.tag] = child.text or ''
                self.dicts[result_name] = od

            elif fmt == 'ini':
                if result_type != 'dictionary':
                    raise FatalError("parse ini: result type must be 'dictionary'", node.line)
                config = _cp.ConfigParser()
                config.read_string(source_val)
                od = OrderedDict()
                for section in config.sections():
                    section_od = OrderedDict(config.items(section))
                    od[section] = section_od
                self.dicts[result_name] = od

            else:
                raise FatalError(f"parse: unknown format '{fmt}'", node.line)

        except (FatalError, RecoverableError):
            raise
        except Exception as e:
            raise FatalError(f"parse {fmt}: {e}", node.line)

    def _exec_inspect(self, node: InspectInstr, scope, loop_ctx, container_tag):
        """Execute an inspect instruction — prints structure to terminal."""
        import json as _json
        import csv as _csv
        import xml.etree.ElementTree as _ET
        import configparser as _cp
        import io as _io

        source_val = self._eval_expr(node.source, scope, loop_ctx, container_tag)
        if not isinstance(source_val, str):
            raise FatalError(
                f"inspect: source must be a text value, got {self._type_name(source_val)}",
                node.line)

        fmt = node.format.lower()
        try:
            if fmt == 'json':
                data = _json.loads(source_val)
                print(f"[inspect json]")
                self._print_structure(data, indent=2)
            elif fmt == 'csv':
                reader = _csv.DictReader(_io.StringIO(source_val))
                rows = list(reader)
                print(f"[inspect csv] {len(rows)} row(s), fields: "
                      f"{', '.join(reader.fieldnames or [])}")
                for i, row in enumerate(rows[:5], 1):
                    print(f"  row {i}: {dict(row)}")
                if len(rows) > 5:
                    print(f"  ... ({len(rows) - 5} more rows)")
            elif fmt == 'xml':
                root = _ET.fromstring(source_val)
                print(f"[inspect xml] root: <{root.tag}>, children: "
                      f"{', '.join(f'<{c.tag}>' for c in root)}")
            elif fmt == 'ini':
                config = _cp.ConfigParser()
                config.read_string(source_val)
                print(f"[inspect ini] sections: {', '.join(config.sections())}")
                for section in config.sections():
                    print(f"  [{section}]: {', '.join(config.options(section))}")
            else:
                raise FatalError(f"inspect: unknown format '{fmt}'", node.line)
        except (FatalError, RecoverableError):
            raise
        except Exception as e:
            raise FatalError(f"inspect {fmt}: {e}", node.line)

    def _print_structure(self, data, indent: int = 0):
        """Recursively print a parsed data structure."""
        pad = ' ' * indent
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, (dict, list)):
                    print(f"{pad}{k}:")
                    self._print_structure(v, indent + 2)
                else:
                    print(f"{pad}{k}: {v}")
        elif isinstance(data, list):
            for i, item in enumerate(data):
                if isinstance(item, (dict, list)):
                    print(f"{pad}[{i}]:")
                    self._print_structure(item, indent + 2)
                else:
                    print(f"{pad}[{i}]: {item}")
        else:
            print(f"{pad}{data}")

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

        elif t is NoneLit:
            return None   # none type

        elif t is FailReason:
            reason = scope.get('__fail_reason__')
            if reason is None:
                raise FatalError("fail reason: used outside if fail block", expr.line)
            return reason

        elif t is FailType:
            ft = scope.get('__fail_type__')
            if ft is None:
                raise FatalError("fail type: used outside if fail block", expr.line)
            return ft

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

        elif t is PathExistCheck:
            # path .value exist — dynamic file path from runtime value
            path_str = self._eval_expr(cond.ref, scope, loop_ctx, container_tag)
            if not isinstance(path_str, str):
                raise FatalError(
                    f"path exist: path must be a text value, got {self._type_name(path_str)}",
                    cond.line)
            return os.path.exists(path_str)

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

        # ── Explicit cross-script reference: .valuename.scriptname.script ────────
        # Chain has the form  .value[.more].scriptname.script[.filename.vern]
        # "script" descriptor means: look in the named script's persisted scope.
        ref_parts = [p for p in vref.ref.lstrip('.').split('.') if p]
        if 'script' in ref_parts:
            script_idx = ref_parts.index('script')
            if script_idx >= 2:
                # parts[0] is value name, parts[1..script_idx-1] are script name
                val_name = ref_parts[0]
                script_name = ref_parts[script_idx - 1]
                # Check current file's script_scopes
                if script_name in self.script_scopes:
                    saved = self.script_scopes[script_name]
                    if val_name in saved:
                        return saved[val_name]
                # Check imported executors
                for imp in self.imported:
                    if script_name in imp.script_scopes:
                        saved = imp.script_scopes[script_name]
                        if val_name in saved:
                            return saved[val_name]
                raise FatalError(
                    f"undefined value: .{val_name} in script .{script_name}",
                    vref.line)

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
        # None (none type) — only equality comparisons are valid
        if left is None or right is None:
            if op in ('IS_EQUAL_TO', 'EQ'):
                return left is right
            if op in ('IS_NOT', 'NEQ'):
                return left is not right
            raise FatalError(
                f"comparison: 'none' values only support = and !=", line)

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
        if val is None:
            return 'none'
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
        if val is None:
            return 'none'
        if type(val) is bool:
            return 'true' if val else 'false'
        if isinstance(val, float):
            if math.isinf(val):
                return 'infinity' if val > 0 else '-infinity'
            if math.isnan(val):
                return 'nan'
            if val == int(val) and abs(val) < 1e15:
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
        # Fallback: if not found relative to the program, and the path contains
        # .lib.folder, retry relative to the interpreter's own directory so the
        # stdlib in lib/ alongside vern.exe works regardless of where the user's
        # program lives. Only .lib.folder imports get this treatment — all other
        # import failures are fatal immediately.
        if not os.path.exists(path):
            ref = node.path.ref
            parts = [p for p in ref.split('.') if p]
            pairs = list(zip(parts, parts[1:]))
            if ('lib', 'folder') in pairs:
                executor_dir = os.path.dirname(os.path.abspath(sys.executable))
                file_name, folders, use_parent = self._parse_ref_chain(ref, node.line)
                if not use_parent:
                    alt_path = os.path.join(executor_dir, *folders, file_name) if file_name else None
                    if alt_path and os.path.exists(alt_path):
                        path = alt_path
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
