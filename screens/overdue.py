import tkinter as tk
from tkinter import ttk, messagebox
from datetime import date
from urllib.parse import quote
import webbrowser

from repositories.loans_repository import LoansRepository
from .base_screen import BaseScreen


class OverdueScreen(BaseScreen):
    title = "איחורים בהחזרת ספרים"

    def __init__(self, parent, navigate=None):
        super().__init__(parent, navigate)
        self.repo = LoansRepository()
        self.rows = []
        self.build()
        self.refresh()

    def build(self):
        toolbar = tk.Frame(self, bg="#f3f4f6")
        toolbar.pack(fill="x", padx=20, pady=5)
        ttk.Button(
            toolbar,
            text="שליחת מייל תזכורת",
            command=self.send_reminder,
        ).pack(side="right", padx=4)
        ttk.Button(toolbar, text="רענן", command=self.refresh).pack(side="right", padx=4)

        form = tk.LabelFrame(
            self,
            text="ספרים שטרם הוחזרו",
            bg="#f3f4f6",
            labelanchor="ne",
        )
        form.pack(fill="both", expand=True, padx=20, pady=8)
        form.grid_anchor("e")

        columns = ["book_title", "user_name", "email", "due_date", "days"]
        self.tree = ttk.Treeview(form, columns=columns, show="headings", selectmode="browse")
        headings = {
            "book_title": "שם הספר",
            "user_name": "המשתמש",
            "email": "דוא״ל",
            "due_date": "מועד ההחזרה",
            "days": "ימי איחור",
        }
        widths = {"book_title": 220, "user_name": 180, "email": 220, "due_date": 120, "days": 90}
        for column in columns:
            self.tree.heading(column, text=headings[column], anchor="e")
            self.tree.column(column, width=widths[column], anchor="e")
        self.tree.pack(fill="both", expand=True, padx=8, pady=8)
        self.tree.bind("<Double-1>", lambda event: self.send_reminder())

        self.status = tk.Label(form, text="", bg="#f3f4f6", anchor="e", justify="right")
        self.status.pack(fill="x", padx=8, pady=(0, 8))

    def refresh(self):
        self.rows = list(self.repo.overdue())
        if not hasattr(self, "tree"):
            return
        self.tree.delete(*self.tree.get_children())
        today = date.today()
        for row in self.rows:
            due_date = date.fromisoformat(row["due_date"])
            user_name = f'{row["first_name"]} {row["last_name"]}'
            self.tree.insert(
                "",
                "end",
                iid=str(row["id"]),
                values=[
                    row["book_title"],
                    user_name,
                    row["email"] or "",
                    row["due_date"],
                    (today - due_date).days,
                ],
            )
        self.status.config(text=f"נמצאו {len(self.rows)} השאלות באיחור")

    def send_reminder(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("תזכורת", "בחר השאלה באיחור מהרשימה.")
            return

        loan_id = int(selection[0])
        row = next((item for item in self.rows if item["id"] == loan_id), None)
        if not row:
            return
        if not row["email"]:
            messagebox.showwarning(
                "אין כתובת דוא״ל",
                "למשתמש שנבחר לא הוגדרה כתובת דוא״ל.",
            )
            return

        user_name = f'{row["first_name"]} {row["last_name"]}'
        subject = "תזכורת להחזרת ספר"
        body = (
            f"שלום {user_name},\n\n"
            f"זוהי תזכורת להחזיר את הספר \"{row['book_title']}\".\n"
            f"מועד ההחזרה היה: {row['due_date']}.\n\n"
            "נשמח לקבל את הספר בהקדם.\n"
            "תודה,\nהספרייה הקהילתית"
        )
        gmail_url = (
            "https://mail.google.com/mail/?view=cm&fs=1"
            f"&to={quote(row['email'])}"
            f"&su={quote(subject)}"
            f"&body={quote(body)}"
        )
        try:
            webbrowser.open(gmail_url)
        except Exception as error:
            messagebox.showerror("שליחת תזכורת", f"לא ניתן לפתוח את Gmail: {error}")
