import tkinter as tk
from tkinter import ttk
import ctypes
import json
import sys
from pathlib import Path
from database import init_db
from screens.dashboard import DashboardScreen
from screens.users import UsersScreen
from screens.books import BooksScreen
from screens.loans import LoansScreen
from screens.reservations import ReservationsScreen
from screens.overdue import OverdueScreen
from screens.settings import SettingsScreen

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
        self.setup_path=self.get_setup_path()
        self.load_setup()
        self.build_navigation()
        self.set_console_visible(self.console_visible)
        self.show("dashboard")

    def get_setup_path(self):
        if getattr(sys,"frozen",False):
            return Path(sys.executable).with_name("setup.json")
        return Path(__file__).with_name("setup.json")

    def load_setup(self):
        self.reservations_visible=False
        self.console_visible=False
        try:
            with self.setup_path.open("r",encoding="utf-8") as setup_file:
                setup=json.load(setup_file)
            self.reservations_visible=bool(setup.get("reservations_visible",False))
            self.console_visible=bool(setup.get("console_visible",False))
        except (OSError, json.JSONDecodeError):
            pass

    def save_setup(self):
        setup={
            "reservations_visible":self.reservations_visible,
            "console_visible":self.console_visible}
        try:
            with self.setup_path.open("w",encoding="utf-8") as setup_file:
                json.dump(setup,setup_file,ensure_ascii=False,indent=2)
        except OSError:
            pass

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
            ("⚠  איחורים","overdue")]
        for text,key in items:
            ttk.Button(self.nav,text=text,command=lambda k=key:self.show(k)).pack(
                fill="x",padx=15,pady=6)
        self.reservations_button=ttk.Button(
            self.nav,text="📌  הזמנות",command=lambda:self.show("reservations"))
        self.show_reservations_button()
        ttk.Button(self.nav,text="⚙  הגדרות",command=lambda:self.show("settings")).pack(
            side="bottom",fill="x",padx=15,pady=15)
        self.content=tk.Frame(self,bg="#f3f4f6")
        self.content.pack(side="left",fill="both",expand=True)

    def show_reservations_button(self):
        if self.reservations_visible:
            self.reservations_button.pack(fill="x",padx=15,pady=6)
        else:
            self.reservations_button.pack_forget()

    def toggle_reservations(self):
        self.reservations_visible=not self.reservations_visible
        self.show_reservations_button()

    def toggle_console(self):
        self.set_console_visible(not self.console_visible)

    def set_console_visible(self,visible):
        self.console_visible=visible
        console_window = ctypes.windll.kernel32.GetConsoleWindow()
        if not console_window:
            return

        ctypes.windll.user32.ShowWindow(console_window, 5 if self.console_visible else 0)

    def restore_setup(self,reservations_visible,console_visible):
        self.reservations_visible=reservations_visible
        self.show_reservations_button()
        self.set_console_visible(console_visible)

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
        if key=="settings":
            SettingsScreen(
                self.content,self.show,
                get_reservations_visible=lambda:self.reservations_visible,
                toggle_reservations=self.toggle_reservations,
                get_console_visible=lambda:self.console_visible,
                toggle_console=self.toggle_console,
                save_setup=self.save_setup,
                restore_setup=self.restore_setup).pack(fill="both",expand=True)
            return
        if key=="loans":
            LoansScreen(self.content,self.show,selected_book_id=self.selected_book_id,
                        selected_user_id=self.selected_user_id).pack(fill="both",expand=True)
        else:
            classes[key](self.content,self.show).pack(fill="both",expand=True)

if __name__=="__main__":
    LibraryApp().mainloop()
