"""Dictionary-based report management with optional JSON persistence."""
from __future__ import annotations

import json
import os
import tempfile
from datetime import date
from pathlib import Path


class ReportError(ValueError):
    """Invalid report data or action."""


class ReportStore:
    def __init__(self, path: str | Path = "reports.json"):
        self.path = Path(path)
        self.reports: dict[str, dict[str, str]] = {}
        self.load()

    def load(self) -> None:
        if not self.path.exists():
            self.reports = {}
            return
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if not isinstance(raw, dict):
                raise ValueError("Root must be a dictionary.")
            clean = {}
            for report_id, record in raw.items():
                if not isinstance(report_id, str) or not isinstance(record, dict):
                    raise ValueError("Invalid report entry.")
                if not report_id.startswith("R") or not report_id[1:].isdigit():
                    raise ValueError("Invalid report ID.")
                if not all(isinstance(record.get(k), str) for k in
                           ("computer", "issue", "date", "status")):
                    raise ValueError("Incomplete report entry.")
                if not record["computer"].strip() or not record["issue"].strip():
                    raise ValueError("Empty report field.")
                if record["status"] not in ("Pending", "Resolved"):
                    raise ValueError("Invalid status.")
                clean[report_id] = {
                    "computer": record["computer"],
                    "issue": record["issue"],
                    "date": record["date"],
                    "status": record["status"],
                }
            self.reports = clean
        except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as exc:
            raise ReportError(
                f"Unable to load {self.path.name}: {exc}\n"
                "Check the JSON file before reopening the application."
            ) from exc

    def _save(self, updated: dict[str, dict[str, str]]) -> None:
        """Write a temporary JSON file, then replace the original."""
        temp_path = None
        try:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="w", encoding="utf-8", dir=self.path.parent,
                prefix=".reports-", suffix=".tmp", delete=False
            ) as handle:
                temp_path = Path(handle.name)
                json.dump(updated, handle, indent=4, ensure_ascii=False)
                handle.write("\n")
            os.replace(temp_path, self.path)
        except OSError as exc:
            raise ReportError(f"Could not save records: {exc}") from exc
        finally:
            if temp_path is not None and temp_path.exists():
                temp_path.unlink(missing_ok=True)
        self.reports = updated

    def add(self, computer: str, issue: str) -> str:
        computer, issue = computer.strip().upper(), issue.strip()
        if not computer or not issue:
            raise ReportError("Computer number and issue description are required.")
        if len(computer) > 25 or len(issue) > 250:
            raise ReportError("Computer number must be at most 25 characters and issue at most 250.")
        if not computer.startswith("PC-") or not computer[3:].isdigit():
            raise ReportError("Use a computer number such as PC-01.")
        number = max((int(k[1:]) for k in self.reports), default=0) + 1
        report_id = f"R{number:03d}"
        updated = dict(self.reports)
        updated[report_id] = {
            "computer": computer,
            "issue": issue,
            "date": date.today().isoformat(),
            "status": "Pending",
        }
        self._save(updated)
        return report_id

    def update_status(self, report_id: str, status: str) -> None:
        if report_id not in self.reports:
            raise ReportError("Select an existing report.")
        if status not in ("Pending", "Resolved"):
            raise ReportError("Invalid report status.")
        updated = {key: dict(value) for key, value in self.reports.items()}
        updated[report_id]["status"] = status
        self._save(updated)

    def delete(self, report_id: str) -> None:
        if report_id not in self.reports:
            raise ReportError("Select an existing report.")
        updated = dict(self.reports)
        del updated[report_id]
        self._save(updated)

    def search(self, term: str = "", status: str = "All") -> list[tuple[str, dict[str, str]]]:
        term = term.strip().casefold()
        if status not in ("All", "Pending", "Resolved"):
            raise ReportError("Invalid filter.")
        matches = [
            (key, record) for key, record in self.reports.items()
            if (status == "All" or record["status"] == status)
            and (not term or any(term in value.casefold()
                 for value in (key, record["computer"], record["issue"], record["status"])))
        ]
        return sorted(matches, key=lambda item: int(item[0][1:]), reverse=True)

    def summary(self) -> tuple[int, int, int]:
        total = len(self.reports)
        pending = sum(item["status"] == "Pending" for item in self.reports.values())
        return total, pending, total - pending
