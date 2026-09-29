import tkinter as tk
from pathlib import Path
from database import fetchone
from .base_screen import BaseScreen

class DashboardScreen(BaseScreen):
    title="מסך פתיחה"

    def __init__(self,parent,navigate=None):
        super().__init__(parent,navigate)
        # logo_path = Path(__file__).resolve().parent.parent / "logoYuvalim.png"
        # self.logo_image = tk.PhotoImage(file=logo_path)
        # tk.Label(self, image=self.logo_image, bg="#f3f4f6").pack(
        #     anchor="e", padx=35, pady=(0, 10))
        values=self.counts()
        cards=[("📚","מספר הספרים",values[0]),
               ("👥","כמות משתמשים",values[1]),
                   ("📖","ספרים בהשאלה",values[2]),
                   ("⚠","כמות איחורים",values[3])]
        row=tk.Frame(self,bg="#f3f4f6")
        row.pack(fill="x",padx=35,pady=35)
        for icon,label,value in cards:
            card=tk.Frame(row,bg="white",bd=1,relief="solid")
            card.pack(side="right",expand=True,fill="both",padx=10,ipady=25)
            tk.Label(card,text=icon,bg="white",font=("Arial",30)).pack()
            tk.Label(card,text=label,bg="white",font=("Arial",13),
                     anchor="e",justify="right").pack(fill="x",padx=12,pady=5)
            tk.Label(card,text=str(value),bg="white",
                     font=("Arial",28,"bold"),anchor="e",justify="right").pack(fill="x",padx=12)
    def counts(self):
        books=fetchone("SELECT COALESCE(SUM(copies),0) n FROM books")["n"]
        users=fetchone("SELECT COUNT(*) n FROM users WHERE active=1")["n"]
        loans=fetchone("""SELECT COUNT(*) n FROM loans
                          WHERE status='borrowed' AND return_date IS NULL""")["n"]
        overdue=fetchone("""SELECT COUNT(*) n FROM loans
                           WHERE status='borrowed' AND return_date IS NULL
                             AND due_date IS NOT NULL
                             AND date(due_date) < date('now')""")["n"]
        return books,users,loans,overdue
