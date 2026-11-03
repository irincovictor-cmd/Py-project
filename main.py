"""Offline Computer Laboratory Issue Reporting System."""
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, simpledialog, ttk

from auth import AccountError, AccountStore
from store import ReportError, ReportStore

BASE = Path(__file__).resolve().parent


class Application:
    def __init__(self, root):
        self.root = root
        root.title("Computer Laboratory Issue Reporting System")
        root.geometry("1080x710")
        root.minsize(860, 590)
        self.accounts = AccountStore(BASE / "users.json")
        self.reports = ReportStore(BASE / "reports.json")
        self.username = None
        self.role = None
        self.show_login()

    def clear(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_login(self):
        self.username = None
        self.role = None
        self.clear()
        frame = ttk.Frame(self.root, padding=35)
        frame.pack(expand=True)
        ttk.Label(frame, text="Computer Laboratory Issue Reporting System",
                  font=("Segoe UI", 17, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 25))
        first = not self.accounts.users
        ttk.Label(frame, text="Create the first administrator account" if first
                  else "Log in to continue").grid(row=1, column=0, columnspan=2, pady=(0, 16))
        ttk.Label(frame, text="Username").grid(row=2, column=0, sticky="w", pady=6)
        user = ttk.Entry(frame, width=32)
        user.grid(row=2, column=1, pady=6)
        ttk.Label(frame, text="Password").grid(row=3, column=0, sticky="w", pady=6)
        password = ttk.Entry(frame, width=32, show="*")
        password.grid(row=3, column=1, pady=6)
        if first:
            ttk.Label(frame, text="Confirm password").grid(row=4, column=0, sticky="w", pady=6)
            confirm = ttk.Entry(frame, width=32, show="*")
            confirm.grid(row=4, column=1, pady=6)

            def submit():
                if password.get() != confirm.get():
                    messagebox.showerror("Error", "Passwords do not match.", parent=self.root)
                    return
                try:
                    self.accounts.create(user.get(), password.get(), "admin")
                except AccountError as exc:
                    messagebox.showerror("Error", str(exc), parent=self.root)
                    return
                messagebox.showinfo("Account Created", "Administrator account created. Please log in.",
                                    parent=self.root)
                self.show_login()
            action = "Create Administrator"
        else:
            def submit():
                role = self.accounts.authenticate(user.get(), password.get())
                if not role:
                    messagebox.showerror("Login Failed", "Invalid username or password.",
                                         parent=self.root)
                    return
                self.username = user.get().strip().lower()
                self.role = role
                self.show_dashboard()
            action = "Log In"
        ttk.Button(frame, text=action, command=submit).grid(
            row=5, column=0, columnspan=2, sticky="ew", pady=(18, 0))
        password.bind("<Return>", lambda _: submit())
        user.focus_set()

    def show_dashboard(self):
        self.clear()
        outer = ttk.Frame(self.root, padding=16)
        outer.pack(fill="both", expand=True)
        bar = ttk.Frame(outer)
        bar.pack(fill="x", pady=(0, 14))
        ttk.Label(bar, text="Computer Laboratory Issue Reporting System",
                  font=("Segoe UI", 16, "bold")).pack(side="left")
        ttk.Button(bar, text="Log Out", command=self.show_login).pack(side="right")
        ttk.Label(bar, text=f"{self.username} ({self.role.title()})").pack(
            side="right", padx=15)

        summary = ttk.Frame(outer)
        summary.pack(fill="x", pady=(0, 12))
        self.counts = {}
        for title in ("Total Reports", "Unresolved", "Resolved"):
            group = ttk.LabelFrame(summary, text=title, padding=9)
            group.pack(side="left", fill="x", expand=True, padx=(0, 8))
            variable = tk.StringVar()
            ttk.Label(group, textvariable=variable, font=("Segoe UI", 17, "bold")).pack()
            self.counts[title] = variable

        if self.role == "staff":
            form = ttk.LabelFrame(outer, text="Submit an Issue", padding=12)
            form.pack(fill="x", pady=(0, 12))
            self.pc = tk.StringVar()
            ttk.Label(form, text="Computer Number (e.g. PC-01)").grid(
                row=0, column=0, sticky="w")
            ttk.Label(form, text="Problem Description").grid(row=0, column=1, sticky="w")
            ttk.Entry(form, textvariable=self.pc, width=18).grid(
                row=1, column=0, sticky="ew", padx=(0, 12), pady=(5, 0))
            self.issue = ttk.Entry(form)
            self.issue.grid(row=1, column=1, sticky="ew", padx=(0, 12), pady=(5, 0))
            ttk.Button(form, text="Submit Report", command=self.submit_report).grid(
                row=1, column=2, padx=(12, 0), pady=(5, 0))
            form.columnconfigure(1, weight=1)
        else:
            tools = ttk.Frame(outer)
            tools.pack(fill="x", pady=(0, 12))
            ttk.Button(tools, text="Create Staff Account", command=self.create_staff).pack(side="left")
            ttk.Label(tools, text="Admin manages repairs and report statuses.").pack(
                side="left", padx=15)

        records = ttk.LabelFrame(outer, text="Issue Reports", padding=10)
        records.pack(fill="both", expand=True)
        filters = ttk.Frame(records)
        filters.pack(fill="x", pady=(0, 8))
        self.query = tk.StringVar()
        self.status = tk.StringVar(value="All")
        ttk.Label(filters, text="Search").pack(side="left")
        ttk.Entry(filters, textvariable=self.query, width=33).pack(
            side="left", padx=(7, 18))
        ttk.Label(filters, text="Status").pack(side="left")
        combo = ttk.Combobox(filters, textvariable=self.status, state="readonly",
                             values=("All", "Pending", "In Progress", "Resolved"), width=14)
        combo.pack(side="left", padx=7)
        combo.bind("<<ComboboxSelected>>", lambda _: self.refresh())
        ttk.Button(filters, text="Clear Filters", command=self.clear_filters).pack(
            side="left", padx=8)

        frame = ttk.Frame(records)
        frame.pack(fill="both", expand=True)
        cols = ("id", "pc", "issue", "reported_by", "date", "status", "resolution")
        self.tree = ttk.Treeview(frame, columns=cols, show="headings", selectmode="browse")
        for key, label, width, stretch in (
            ("id", "ID", 65, False), ("pc", "Computer", 90, False),
            ("issue", "Issue Description", 270, True),
            ("reported_by", "Reported By", 100, False),
            ("date", "Date", 105, False),
            ("status", "Status", 100, False),
            ("resolution", "Resolution Notes", 220, True),
        ):
            self.tree.heading(key, text=label)
            self.tree.column(key, width=width, minwidth=55, stretch=stretch)
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        if self.role == "admin":
            actions = ttk.Frame(records)
            actions.pack(fill="x", pady=(10, 0))
            ttk.Button(actions, text="Mark In Progress",
                       command=lambda: self.change_status("In Progress")).pack(
                side="left", padx=(0, 8))
            ttk.Button(actions, text="Mark Resolved",
                       command=lambda: self.change_status("Resolved")).pack(
                side="left", padx=(0, 8))
            ttk.Button(actions, text="Reopen as Pending",
                       command=lambda: self.change_status("Pending")).pack(
                side="left", padx=(0, 8))
            ttk.Button(actions, text="Delete Selected",
                       command=self.delete_report).pack(side="left")
        else:
            ttk.Label(records, text="Staff can submit and view their reports. "
                      "Only the administrator can update or delete them.").pack(
                anchor="w", pady=(10, 0))

        self.query.trace_add("write", lambda *_: self.refresh())
        self.refresh()

    def clear_filters(self):
        self.query.set("")
        self.status.set("All")
        self.refresh()

    def visible(self):
        results = self.reports.search(self.query.get(), self.status.get())
        if self.role == "staff":
            results = [(key, item) for key, item in results
                       if item.get("reporter") == self.username]
        return results

    def refresh(self):
        for key in self.tree.get_children():
            self.tree.delete(key)
        for report_id, item in self.visible():
            self.tree.insert("", "end", iid=report_id, values=(
                report_id, item["computer"], item["issue"],
                item.get("reporter", "Unknown"), item["date"],
                item["status"], item.get("resolution", "")))
        visible_records = [item for _, item in self.visible()]
        self.counts["Total Reports"].set(str(len(visible_records)))
        self.counts["Unresolved"].set(str(sum(x["status"] != "Resolved"
                                               for x in visible_records)))
        self.counts["Resolved"].set(str(sum(x["status"] == "Resolved"
                                             for x in visible_records)))

    def submit_report(self):
        if self.role != "staff":
            return
        try:
            report_id = self.reports.add(self.pc.get(), self.issue.get(), self.username)
        except ReportError as exc:
            messagebox.showerror("Invalid Report", str(exc), parent=self.root)
            return
        self.pc.set("")
        self.issue.delete(0, tk.END)
        self.clear_filters()
        messagebox.showinfo("Submitted", f"Report {report_id} submitted.", parent=self.root)

    def selected(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Select Report", "Select a report first.", parent=self.root)
            return None
        return selected[0]

    def change_status(self, status):
        if self.role != "admin":
            return
        key = self.selected()
        if key is None:
            return
        notes = ""
        if status == "Resolved":
            notes = simpledialog.askstring("Resolution Notes",
                "What was done to fix the issue? (Required)", parent=self.root)
            if notes is None:
                return
            if not notes.strip():
                messagebox.showerror("Required", "Enter resolution notes.", parent=self.root)
                return
        try:
            self.reports.update_status(key, status, notes)
        except ReportError as exc:
            messagebox.showerror("Update Failed", str(exc), parent=self.root)
            return
        self.refresh()

    def delete_report(self):
        if self.role != "admin":
            return
        key = self.selected()
        if key is None or not messagebox.askyesno(
            "Confirm Delete", f"Delete {key} permanently?", parent=self.root):
            return
        try:
            self.reports.delete(key)
        except ReportError as exc:
            messagebox.showerror("Delete Failed", str(exc), parent=self.root)
            return
        self.refresh()

    def create_staff(self):
        if self.role != "admin":
            return
        username = simpledialog.askstring("New Staff", "Staff username:", parent=self.root)
        if username is None:
            return
        password = simpledialog.askstring("New Staff", "Temporary staff password (8+ characters):",
                                          show="*", parent=self.root)
        if password is None:
            return
        try:
            self.accounts.create(username, password, "staff", actor_role=self.role)
        except AccountError as exc:
            messagebox.showerror("Cannot Create Account", str(exc), parent=self.root)
            return
        messagebox.showinfo("Account Created", "Staff account created.", parent=self.root)


def main():
    root = tk.Tk()
    try:
        Application(root)
    except (AccountError, ReportError) as exc:
        messagebox.showerror("Startup Error", str(exc), parent=root)
        root.destroy()
        return
    root.mainloop()


if __name__ == "__main__":
    main()
