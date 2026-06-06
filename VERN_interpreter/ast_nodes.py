#!/usr/bin/env python3
"""VERN AST node definitions — v0.6 spec."""

from dataclasses import dataclass, field
from typing import Any, List, Optional, Union


# ── Expressions ────────────────────────────────────────────────────────────────

@dataclass
class ValueRef:
    """A dotted reference chain: .name, .name.script.vern, etc."""
    ref: str
    container: Optional[str] = None   # inline #tag if present
    line: int = 0

@dataclass
class TextLit:
    value: str
    line: int = 0

@dataclass
class NumberLit:
    value: str   # keep as string to preserve "3.14" vs "3"
    line: int = 0

@dataclass
class DateLit:
    value: str   # YYYY-MM-DD
    line: int = 0

@dataclass
class TimeLit:
    value: str   # HH:MI:SS
    line: int = 0

@dataclass
class BoolLit:
    value: bool
    line: int = 0

@dataclass
class Constant:
    name: str    # "pi", "e", "tau", "infinity"
    line: int = 0

@dataclass
class LoopVar:
    line: int = 0

@dataclass
class CurrentItem:
    line: int = 0

@dataclass
class CurrentKey:
    line: int = 0

@dataclass
class CurrentValue:
    line: int = 0

@dataclass
class FailReason:
    line: int = 0

@dataclass
class BinOp:
    left: Any
    op: str      # "+", "-", "*", "/", "power", "root", "remainder"
    right: Any
    line: int = 0

# Expr union (for type hints)
Expr = Union[
    ValueRef, TextLit, NumberLit, DateLit, TimeLit, BoolLit,
    Constant, LoopVar, CurrentItem, CurrentKey, CurrentValue, FailReason, BinOp
]


# ── Conditions ─────────────────────────────────────────────────────────────────

@dataclass
class Comparison:
    left: Any
    op: str      # token type: IS_EQUAL_TO, IS_NOT, EQ, NEQ, GT, LT, GTE, LTE,
                 #             IS_GREATER_THAN, IS_LESS_THAN,
                 #             IS_GREATER_THAN_OR_EQUAL_TO, IS_LESS_THAN_OR_EQUAL_TO
    right: Any
    line: int = 0

@dataclass
class MemberCheck:
    """expr (is in | not in) (list name | dictionary name | .ref)"""
    value: Any
    negated: bool
    collection_kind: str   # "list", "dictionary", "text"
    collection: Any        # str (list/dict IDENTIFIER) or ValueRef (text ref)
    file_ref: Optional[Any] = None   # cross-file ValueRef
    line: int = 0

@dataclass
class ExistCheck:
    ref: ValueRef
    line: int = 0

@dataclass
class StartsWithCond:
    ref: Any
    pattern: Any
    line: int = 0

@dataclass
class EndsWithCond:
    ref: Any
    pattern: Any
    line: int = 0

@dataclass
class NotCond:
    cond: Any
    line: int = 0

@dataclass
class AndCond:
    left: Any
    right: Any
    line: int = 0

@dataclass
class OrCond:
    left: Any
    right: Any
    line: int = 0

Condition = Union[
    Comparison, MemberCheck, ExistCheck, StartsWithCond, EndsWithCond,
    NotCond, AndCond, OrCond, BoolLit, ValueRef
]


# ── Instructions ───────────────────────────────────────────────────────────────

@dataclass
class SetInstr:
    target: ValueRef
    value: Any   # Expr
    line: int = 0

@dataclass
class ShowInstr:
    values: List[Any]
    line: int = 0

@dataclass
class AskInstr:
    target: ValueRef
    line: int = 0

@dataclass
class ReadInstr:
    targets: List[ValueRef]
    source: ValueRef
    line: int = 0

@dataclass
class WriteInstr:
    values: List[Any]
    dest: ValueRef
    line: int = 0

@dataclass
class AppendInstr:
    values: List[Any]
    dest: ValueRef
    line: int = 0

@dataclass
class RunInstr:
    script: ValueRef
    args: List[Any]           # positional args after "with"
    container: Optional[str]  # #tag name
    line: int = 0

@dataclass
class ReturnInstr:
    value: ValueRef
    dest: ValueRef
    line: int = 0

@dataclass
class ConvertInstr:
    source: Any     # Expr (ValueRef, CurrentItem, CurrentKey, CurrentValue, LoopVar)
    target_type: str
    result: ValueRef
    line: int = 0

@dataclass
class TypeOfInstr:
    source: Any
    result: ValueRef
    line: int = 0

@dataclass
class ImportInstr:
    path: ValueRef
    line: int = 0

@dataclass
class StopInstr:
    line: int = 0

@dataclass
class StartAt:
    script: ValueRef
    line: int = 0

@dataclass
class DefineInstr:
    word: str
    action: Any
    line: int = 0

@dataclass
class ExitLoopInstr:
    line: int = 0

@dataclass
class NextItemInstr:
    line: int = 0


# ── Control flow ───────────────────────────────────────────────────────────────

@dataclass
class IfInline:
    condition: Any
    action: Any
    line: int = 0

@dataclass
class IfBlock:
    condition: Any
    then_body: List[Any] = field(default_factory=list)
    else_body: List[Any] = field(default_factory=list)
    line: int = 0

@dataclass
class WhileBlock:
    condition: Any
    body: List[Any] = field(default_factory=list)
    line: int = 0

@dataclass
class RepeatTimesBlock:
    count: Any
    body: List[Any] = field(default_factory=list)
    line: int = 0

@dataclass
class RepeatThroughListBlock:
    list_name: str
    file_ref: Optional[Any] = None
    body: List[Any] = field(default_factory=list)
    line: int = 0

@dataclass
class RepeatThroughDictBlock:
    dict_name: str
    file_ref: Optional[Any] = None
    body: List[Any] = field(default_factory=list)
    line: int = 0

@dataclass
class AttemptBlock:
    try_all: bool
    body: List[Any] = field(default_factory=list)
    fail_body: List[Any] = field(default_factory=list)
    line: int = 0


# ── Collection declarations ────────────────────────────────────────────────────

@dataclass
class ListDecl:
    name: str
    items: List[Any]            # Expr list or IDENTIFIER strings for dict refs
    file_ref: Optional[Any] = None
    line: int = 0

@dataclass
class DictDecl:
    name: str
    pairs: List[tuple] = field(default_factory=list)   # (key_expr, value_expr)
    line: int = 0

@dataclass
class TextBlockDecl:
    name: ValueRef
    content_lines: List[str] = field(default_factory=list)
    line: int = 0


# ── Collection operations ──────────────────────────────────────────────────────

@dataclass
class PutInList:
    value: Any
    list_name: str
    file_ref: Optional[Any] = None
    line: int = 0

@dataclass
class PutInDict:
    value: Any
    dict_ref: Any    # str IDENTIFIER or ValueRef
    key: Any
    file_ref: Optional[Any] = None
    line: int = 0

@dataclass
class PutDictInList:
    dict_name: str
    list_name: str
    line: int = 0

@dataclass
class PutDictInDict:
    dict_name: str
    target_dict: str
    key: Any
    line: int = 0

@dataclass
class RemoveFromList:
    value: Any
    list_name: str
    file_ref: Optional[Any] = None
    line: int = 0

@dataclass
class RemoveKeyFromDict:
    key: Any
    dict_name: str
    line: int = 0

@dataclass
class GetListItem:
    list_name: str
    position: Any
    result: ValueRef
    file_ref: Optional[Any] = None
    line: int = 0

@dataclass
class GetDictItem:
    dict_ref: Any    # str or ValueRef
    key: Any
    result: ValueRef
    line: int = 0

@dataclass
class CountList:
    list_name: str
    result: ValueRef
    file_ref: Optional[Any] = None
    line: int = 0

@dataclass
class CountDict:
    dict_name: str
    result: ValueRef
    line: int = 0

@dataclass
class SortList:
    list_name: str
    descending: bool
    result_name: str
    line: int = 0

@dataclass
class ReverseList:
    list_name: str
    result_name: str
    line: int = 0

@dataclass
class SliceList:
    list_name: str
    start: Any
    end: Any
    result_name: str
    line: int = 0

@dataclass
class CombineList:
    first: str
    second: str
    result: str
    line: int = 0


# ── Extended math ──────────────────────────────────────────────────────────────

@dataclass
class RoundInstr:
    value: Any
    decimals: Optional[Any] = None
    result: Optional[ValueRef] = None
    line: int = 0

@dataclass
class FloorInstr:
    value: Any
    decimals: Optional[Any] = None
    result: Optional[ValueRef] = None
    line: int = 0

@dataclass
class CeilingInstr:
    value: Any
    decimals: Optional[Any] = None
    result: Optional[ValueRef] = None
    line: int = 0

@dataclass
class RandomInstr:
    min_val: Any
    max_val: Any
    result: ValueRef
    line: int = 0

@dataclass
class AbsoluteInstr:
    value: Any
    result: ValueRef
    line: int = 0

@dataclass
class MinMaxInstr:
    op: str             # "minimum" or "maximum"
    operands: Any       # (Expr, Expr) tuple or str list_name
    result: ValueRef
    line: int = 0

@dataclass
class PercentInstr:
    value: Any
    total: Any
    result: ValueRef
    line: int = 0

@dataclass
class SumInstr:
    list_name: str
    result: ValueRef
    line: int = 0

@dataclass
class FactorialInstr:
    value: Any
    result: ValueRef
    line: int = 0

@dataclass
class CombinationsInstr:
    n: Any
    k: Any
    result: ValueRef
    line: int = 0

@dataclass
class PermutationsInstr:
    n: Any
    k: Any
    result: ValueRef
    line: int = 0

@dataclass
class SignInstr:
    value: Any
    result: ValueRef
    line: int = 0


# ── Trig / log / angle ─────────────────────────────────────────────────────────

@dataclass
class TrigInstr:
    func: str            # "sine", "cosine", "tangent", "arcsine", etc.
    args: List[Any]      # 1 or 2 value refs (arctangent y x)
    use_radians: bool
    result: ValueRef
    line: int = 0

@dataclass
class LnInstr:
    value: Any
    result: ValueRef
    line: int = 0

@dataclass
class LogInstr:
    value: Any
    base: Optional[Any]
    result: ValueRef
    line: int = 0

@dataclass
class AngleConvInstr:
    direction: str   # "degrees" or "radians"
    value: Any
    result: ValueRef
    line: int = 0


# ── String operations ──────────────────────────────────────────────────────────

@dataclass
class LengthOfInstr:
    value: Any
    result: ValueRef
    line: int = 0

@dataclass
class FindInstr:
    pattern: Any
    text: Any
    result: ValueRef
    line: int = 0

@dataclass
class ExtractInstr:
    text: Any
    beginning: Any
    finishing: Any
    result: ValueRef
    line: int = 0

@dataclass
class ReplaceInstr:
    old: Any
    new: Any
    text: Any
    result: ValueRef
    line: int = 0

@dataclass
class SplitInstr:
    text: Any
    delimiter: Any
    result_list: str
    line: int = 0

@dataclass
class JoinInstr:
    list_name: str
    separator: Any
    result: ValueRef
    line: int = 0

@dataclass
class TrimInstr:
    text: Any
    result: ValueRef
    line: int = 0

@dataclass
class UppercaseInstr:
    text: Any
    result: ValueRef
    line: int = 0

@dataclass
class LowercaseInstr:
    text: Any
    result: ValueRef
    line: int = 0


# ── Date / time ────────────────────────────────────────────────────────────────

@dataclass
class GetDateInstr:
    result: ValueRef
    line: int = 0

@dataclass
class GetTimeInstr:
    result: ValueRef
    line: int = 0

@dataclass
class DiffBetweenInstr:
    first: ValueRef
    second: ValueRef
    unit: str   # "days", "hours", "minutes"
    result: ValueRef
    line: int = 0

@dataclass
class FormatDateTimeInstr:
    value: ValueRef
    result: ValueRef
    fmt: Any
    line: int = 0

@dataclass
class FormatNumberInstr:
    value: ValueRef
    result: ValueRef
    decimals: Optional[Any] = None
    thousands: bool = False
    padded: Optional[Any] = None
    line: int = 0


# ── File operations ────────────────────────────────────────────────────────────

@dataclass
class DeleteInstr:
    path: ValueRef
    line: int = 0

@dataclass
class GetFilesInstr:
    folder: ValueRef
    result_list: str
    line: int = 0


# ── Networking ─────────────────────────────────────────────────────────────────

@dataclass
class FetchInstr:
    url: Any
    result: ValueRef
    line: int = 0

@dataclass
class SendInstr:
    data: Any
    url: Any
    line: int = 0


# ── Script / container ─────────────────────────────────────────────────────────

@dataclass
class ScriptDef:
    name: ValueRef
    params: List[ValueRef] = field(default_factory=list)
    container: Optional[str] = None
    body: List[Any] = field(default_factory=list)
    line: int = 0

@dataclass
class ContainerDef:
    tag: str          # "#english" — full token value
    body: List[Any]   # SetInstr nodes
    line: int = 0


# ── Top-level program ──────────────────────────────────────────────────────────

@dataclass
class Program:
    body: List[Any] = field(default_factory=list)
