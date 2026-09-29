import tkinter as tk
from tkinter import ttk
import ctypes
import sys
from pathlib import Path
from database import init_db
from screens.dashboard import DashboardScreen
from screens.users import UsersScreen
from screens.books import BooksScreen
from screens.loans import LoansScreen
from screens.reservations import ReservationsScreen
from screens.overdue import OverdueScreen

class LibraryApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("📚 ניהול ספרייה קהילתית")
        self.geometry("1200x760")
        self.minsize(1000,650)
        self.option_add("*Label.anchor","e")
        self.option_add("*Label.justify","right")
        self.option_add("*Entry.justify","right")
        self.option_add("*Labelframe.labelanchor","ne")
        ttk.Style(self).configure("TButton",anchor="e")
        init_db()
        self.selected_book_id=None
        self.selected_user_id=None
        self.build_navigation()
        self.show("dashboard")

    def build_navigation(self):
        self.nav=tk.Frame(self,bg="#1f2937",width=220)
        self.nav.pack(side="right",fill="y")
#        logo_path = Path(__file__).resolve().parent / "logoYuvalim.png"
        resource_dir = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
        logo_path = resource_dir / "logoYuvalim.png"
        self.logo_image = tk.PhotoImage(file=logo_path).subsample(2, 2)
        tk.Label(self.nav,image=self.logo_image,bg="#1f2937").pack(pady=(18, 4))
        tk.Label(self.nav,text="\nהספרייה\nהקהילתית\nיובלים",bg="#1f2937",
             fg="white",font=("Arial",19,"bold"),justify="right").pack(pady=(4, 25))
        items=[
            ("🏠  מסך פתיחה","dashboard"),
            ("👥  משתמשים","users"),
            ("📚  ספרים","books"),
            ("📖  השאלות","loans"),
            ("⚠  איחורים","overdue"),
            ("📌  הזמנות","reservations")]
        for text,key in items:
            ttk.Button(self.nav,text=text,command=lambda k=key:self.show(k)).pack(
                fill="x",padx=15,pady=6)
        self.console_visible = True
        self.console_button = ttk.Button(
            self.nav, text="🖥 הסתר מסוף", command=self.toggle_console)
        self.console_button.pack(side="bottom", fill="x", padx=15, pady=15)
        self.content=tk.Frame(self,bg="#f3f4f6")
        self.content.pack(side="left",fill="both",expand=True)

    def toggle_console(self):
        console_window = ctypes.windll.kernel32.GetConsoleWindow()
        if not console_window:
            return

        self.console_visible = not self.console_visible
        ctypes.windll.user32.ShowWindow(console_window, 5 if self.console_visible else 0)
        self.console_button.configure(
            text="🖥 הסתר מסוף" if self.console_visible else "🖥 הצג מסוף")

    def show(self,key):
        current_screens=self.content.winfo_children()
        if current_screens and isinstance(current_screens[0],BooksScreen):
            self.selected_book_id=current_screens[0].selected
        elif current_screens and isinstance(current_screens[0],UsersScreen):
            self.selected_user_id=current_screens[0].selected
        for w in self.content.winfo_children():w.destroy()
        classes={
            "dashboard":DashboardScreen,"users":UsersScreen,"books":BooksScreen,
            "loans":LoansScreen,"reservations":ReservationsScreen}
        classes["overdue"] = OverdueScreen
        if key=="loans":
            LoansScreen(self.content,self.show,selected_book_id=self.selected_book_id,
                        selected_user_id=self.selected_user_id).pack(fill="both",expand=True)
        else:
            classes[key](self.content,self.show).pack(fill="both",expand=True)

if __name__=="__main__":
    LibraryApp().mainloop()
