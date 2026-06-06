#!/usr/bin/env python3
"""VERN error logger — records fatal and non-fatal errors from program execution.

Two error states (per spec §Error Handling):

  FATAL   — execution halted. The error log records what went wrong, the line
             number, and that execution was stopped.

  WARNING — non-fatal. The error log records what went wrong and the line
             number, and notes that execution continued.

A FATAL error inside an attempt block is caught and becomes recoverable.
The log records it as a recovered error — it did occur, but execution continued
because the attempt block handled it.
"""

import os
import sys
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


# ── Log entry ──────────────────────────────────────────────────────────────────

@dataclass
class LogEntry:
    severity: str       # "FATAL" | "WARNING"
    line: int           # source line number (0 = unknown)
    message: str        # human-readable description
    recovered: bool     # True  → caught by attempt block, execution continued
    halted: bool        # True  → execution stopped due to this error


# ── Logger ─────────────────────────────────────────────────────────────────────

class VernLogger:
    """
    Collects error entries during program execution and writes a formatted
    log file when the program finishes (or halts on a fatal error).
    """

    def __init__(self, program_path: str):
        self.program_path = os.path.abspath(program_path)
        self.program_name = os.path.basename(program_path)
        self.run_time: datetime = datetime.now()
        self.entries: List[LogEntry] = []
        self.completed: bool = False   # set True when program finishes normally

    # ── Recording ──────────────────────────────────────────────────────────────

    def fatal(self, message: str, line: int = 0, recovered: bool = False) -> None:
        """
        Record a fatal error.
        recovered=True  → caught by an attempt block; execution continued.
        recovered=False → program is halting because of this error.
        """
        self.entries.append(LogEntry(
            severity="FATAL",
            line=line,
            message=message,
            recovered=recovered,
            halted=(not recovered),
        ))

    def warning(self, message: str, line: int = 0) -> None:
        """Record a non-fatal error. Execution always continues after a warning."""
        self.entries.append(LogEntry(
            severity="WARNING",
            line=line,
            message=message,
            recovered=False,
            halted=False,
        ))

    # ── Counts ─────────────────────────────────────────────────────────────────

    @property
    def warning_count(self) -> int:
        return sum(1 for e in self.entries if e.severity == "WARNING")

    @property
    def recovered_count(self) -> int:
        return sum(1 for e in self.entries if e.severity == "FATAL" and e.recovered)

    @property
    def halting_count(self) -> int:
        return sum(1 for e in self.entries if e.halted)

    @property
    def has_errors(self) -> bool:
        return len(self.entries) > 0

    # ── Output ─────────────────────────────────────────────────────────────────

    def write_log(self, log_path: Optional[str] = None) -> str:
        """
        Write the error log to a file next to the source program.
        Returns the path of the file written.
        """
        if log_path is None:
            log_path = self.program_path + '.log'

        text = self._format_log()
        with open(log_path, 'w', encoding='utf-8') as f:
            f.write(text)
        return log_path

    def print_stderr(self) -> None:
        """Print a brief one-line-per-error summary to stderr."""
        for entry in self.entries:
            tag = self._entry_tag(entry)
            loc = f"Line {entry.line}: " if entry.line else ""
            print(f"{tag} {loc}{entry.message}", file=sys.stderr)

    def print_log(self, file=None) -> None:
        """Print the full formatted log to the given file (default stdout)."""
        print(self._format_log(), file=(file or sys.stdout))

    # ── Formatting ─────────────────────────────────────────────────────────────

    def _format_log(self) -> str:
        bar  = "═" * 56
        thin = "─" * 56
        lines: List[str] = []

        # Header
        lines.append(bar)
        lines.append("  VERN Error Log")
        lines.append(f"  Program : {self.program_name}")
        lines.append(f"  Run     : {self.run_time.strftime('%Y-%m-%d at %H:%M:%S')}")
        lines.append(bar)
        lines.append("")

        if not self.entries:
            lines.append("  No errors.")
            lines.append("")
        else:
            for entry in self.entries:
                lines.extend(self._format_entry(entry))
                lines.append("")

        # Footer
        lines.append(thin)
        lines.extend(self._format_summary_lines())
        lines.append(thin)

        return "\n".join(lines) + "\n"

    def _format_entry(self, entry: LogEntry) -> List[str]:
        """Format a single log entry as a block of lines."""
        # First line: location + tag
        loc = f"Line {entry.line:>4}  │  " if entry.line else "         │  "
        tag = self._entry_tag(entry)
        head = f"{loc}{tag}"

        # Message — word-wrap at 60 chars for readability
        msg_lines = _wrap(entry.message, 60)
        indent     = " " * len(loc)

        result = [head + "  " + msg_lines[0]]
        for ml in msg_lines[1:]:
            result.append(indent + "  " + ml)

        # Status line
        status = self._entry_status(entry)
        result.append(f"{indent}  └ {status}")
        return result

    @staticmethod
    def _entry_tag(entry: LogEntry) -> str:
        if entry.severity == "WARNING":
            return "WARNING"
        if entry.recovered:
            return "FATAL (recovered)"
        return "FATAL"

    @staticmethod
    def _entry_status(entry: LogEntry) -> str:
        if entry.severity == "WARNING":
            return "Execution continued."
        if entry.recovered:
            return "Caught by attempt block — execution continued."
        return "Execution halted."

    def _format_summary_lines(self) -> List[str]:
        parts = []
        if self.warning_count:
            n = self.warning_count
            parts.append(f"{n} warning{'s' if n > 1 else ''}")
        if self.recovered_count:
            n = self.recovered_count
            parts.append(f"{n} recovered error{'s' if n > 1 else ''}")
        if self.halting_count:
            n = self.halting_count
            parts.append(f"{n} halting error{'s' if n > 1 else ''}")

        if not parts:
            error_line = "  Errors  : None"
        else:
            error_line = "  Errors  : " + ", ".join(parts)

        if self.completed:
            status_line = "  Program : Completed normally"
        elif self.halting_count:
            status_line = "  Program : Halted due to fatal error"
        else:
            status_line = "  Program : Completed (with errors)"

        return [error_line, status_line]


# ── Utilities ──────────────────────────────────────────────────────────────────

def _wrap(text: str, width: int) -> List[str]:
    """Very simple word-wrap."""
    if len(text) <= width:
        return [text]
    words = text.split()
    lines: List[str] = []
    current = ""
    for word in words:
        if current and len(current) + 1 + len(word) > width:
            lines.append(current)
            current = word
        else:
            current = (current + " " + word).strip()
    if current:
        lines.append(current)
    return lines or [""]
