"""Computer Laboratory Issue Reporting System - Tkinter desktop interface."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk

from store import ReportError, ReportStore

DATA_FILE = Path(__file__).resolve().parent / "reports.json"


class IssueTrackerApp:
    def __init__(self, root: tk.Tk, store: ReportStore):
        self.root = root
        self.store = store
        self.root.title("Computer Laboratory Issue Reporting System")
        self.root.geometry("1050x680")
        self.root.minsize(830, 560)

        self.computer_var = tk.StringVar()
        self.search_var = tk.StringVar()
        self.filter_var = tk.StringVar(value="All")
        self.total_var = tk.StringVar(value="0")
        self.pending_var = tk.StringVar(value="0")
        self.resolved_var = tk.StringVar(value="0")

        self._build()
        self.refresh()
        self.search_var.trace_add("write", lambda *_: self.refresh())

    def _build(self) -> None:
        outer = ttk.Frame(self.root, padding=18)
        outer.pack(fill="both", expand=True)

        ttk.Label(
            outer, text="Computer Laboratory Issue Reporting System",
            font=("Segoe UI", 17, "bold")
        ).pack(anchor="w")
        ttk.Label(
            outer, text="Record issues, monitor pending reports, and update repair status."
        ).pack(anchor="w", pady=(2, 16))

        summary = ttk.Frame(outer)
        summary.pack(fill="x", pady=(0, 14))
        for title, var in (
            ("Total Reports", self.total_var),
            ("Pending", self.pending_var),
            ("Resolved", self.resolved_var),
        ):
            section = ttk.LabelFrame(summary, text=title, padding=(14, 8))
            section.pack(side="left", fill="x", expand=True, padx=(0, 10))
            ttk.Label(section, textvariable=var, font=("Segoe UI", 18, "bold")).pack(anchor="w")

        add_box = ttk.LabelFrame(outer, text="New Issue Report", padding=12)
        add_box.pack(fill="x", pady=(0, 14))
        ttk.Label(add_box, text="Computer Number (e.g., PC-01)").grid(
            row=0, column=0, sticky="w", padx=(0, 12)
        )
        ttk.Label(add_box, text="Issue Description").grid(
            row=0, column=1, sticky="w"
        )

        self.computer_entry = ttk.Entry(add_box, textvariable=self.computer_var, width=20)
        self.computer_entry.grid(row=1, column=0, sticky="ew", padx=(0, 12), pady=(4, 0))
        self.issue_entry = ttk.Entry(add_box)
        self.issue_entry.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(4, 0))
        ttk.Button(add_box, text="Add Report", command=self.add_report).grid(
            row=1, column=2, sticky="ew", pady=(4, 0)
        )
        add_box.columnconfigure(1, weight=1)
        self.issue_entry.bind("<Return>", lambda _: self.add_report())

        table_box = ttk.LabelFrame(outer, text="Issue Records", padding=12)
        table_box.pack(fill="both", expand=True)

        toolbar = ttk.Frame(table_box)
        toolbar.pack(fill="x", pady=(0, 10))
        ttk.Label(toolbar, text="Search:").pack(side="left")
        ttk.Entry(toolbar, textvariable=self.search_var, width=32).pack(
            side="left", padx=(8, 16)
        )
        ttk.Label(toolbar, text="Status:").pack(side="left")
        filter_menu = ttk.Combobox(
            toolbar, textvariable=self.filter_var,
            values=("All", "Pending", "Resolved"), width=13, state="readonly"
        )
        filter_menu.pack(side="left", padx=(8, 10))
        filter_menu.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        ttk.Button(toolbar, text="Clear Search", command=self.clear_search).pack(side="left")

        area = ttk.Frame(table_box)
        area.pack(fill="both", expand=True)
        columns = ("id", "computer", "issue", "date", "status")
        self.tree = ttk.Treeview(area, columns=columns, show="headings", selectmode="browse")
        for key, label, width, stretch in (
            ("id", "Report ID", 90, False),
            ("computer", "Computer", 110, False),
            ("issue", "Issue Description", 350, True),
            ("date", "Date Reported", 130, False),
            ("status", "Status", 100, False),
        ):
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, minwidth=70, stretch=stretch, anchor="w")
        scrollbar = ttk.Scrollbar(area, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        actions = ttk.Frame(table_box)
        actions.pack(fill="x", pady=(12, 0))
        ttk.Button(
            actions, text="Mark as Resolved", command=lambda: self.change_status("Resolved")
        ).pack(side="left", padx=(0, 8))
        ttk.Button(
            actions, text="Mark as Pending", command=lambda: self.change_status("Pending")
        ).pack(side="left", padx=(0, 8))
        ttk.Button(actions, text="Delete Selected", command=self.delete_report).pack(side="left")
        ttk.Label(
            actions, text="Select a report in the table before updating or deleting."
        ).pack(side="right")

    def refresh(self) -> None:
        selected = self.tree.selection()
        selected_id = selected[0] if selected else None
        for row in self.tree.get_children():
            self.tree.delete(row)
        for report_id, report in self.store.search(
            self.search_var.get(), self.filter_var.get()
        ):
            self.tree.insert(
                "", "end", iid=report_id,
                values=(
                    report_id, report["computer"], report["issue"],
                    report["date"], report["status"],
                ),
            )
        if selected_id and self.tree.exists(selected_id):
            self.tree.selection_set(selected_id)
            self.tree.focus(selected_id)
        total, pending, resolved = self.store.summary()
        self.total_var.set(str(total))
        self.pending_var.set(str(pending))
        self.resolved_var.set(str(resolved))

    def add_report(self) -> None:
        try:
            report_id = self.store.add(
                self.computer_var.get(), self.issue_entry.get()
            )
        except ReportError as exc:
            messagebox.showerror("Unable to Add Report", str(exc), parent=self.root)
            return
        self.computer_var.set("")
        self.issue_entry.delete(0, tk.END)
        self.clear_search()
        self.computer_entry.focus_set()
        messagebox.showinfo("Report Added", f"Report {report_id} was saved.", parent=self.root)

    def selected_report(self) -> str | None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning(
                "No Report Selected", "Please select a report in the table.",
                parent=self.root
            )
            return None
        return selected[0]

    def change_status(self, status: str) -> None:
        report_id = self.selected_report()
        if report_id is None:
            return
        try:
            self.store.update_status(report_id, status)
        except ReportError as exc:
            messagebox.showerror("Unable to Update", str(exc), parent=self.root)
            return
        self.refresh()
        messagebox.showinfo(
            "Status Updated", f"{report_id} is now {status}.", parent=self.root
        )

    def delete_report(self) -> None:
        report_id = self.selected_report()
        if report_id is None:
            return
        if not messagebox.askyesno(
            "Confirm Deletion", f"Delete report {report_id}? This cannot be undone.",
            parent=self.root
        ):
            return
        try:
            self.store.delete(report_id)
        except ReportError as exc:
            messagebox.showerror("Unable to Delete", str(exc), parent=self.root)
            return
        self.refresh()

    def clear_search(self) -> None:
        self.search_var.set("")
        self.filter_var.set("All")
        self.refresh()


def main() -> None:
    root = tk.Tk()
    try:
        store = ReportStore(DATA_FILE)
    except ReportError as exc:
        messagebox.showerror("Unable to Start", str(exc), parent=root)
        root.destroy()
        return
    IssueTrackerApp(root, store)
    root.mainloop()


if __name__ == "__main__":
    main()
