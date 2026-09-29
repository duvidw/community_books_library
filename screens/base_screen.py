import tkinter as tk
from tkinter import ttk
from contextlib import contextmanager

class BaseScreen(tk.Frame):
    title = ""

    def __init__(self,parent,navigate=None):
        super().__init__(parent,bg="#f3f4f6")
        self.navigate=navigate
        self.build_header()

    def build_header(self):
        top=tk.Frame(self,bg="#f3f4f6")
        top.pack(fill="x",padx=20,pady=(18,8))
        tk.Label(top,text=self.title,bg="#f3f4f6",
                 font=("Arial",22,"bold")).pack(side="right")
        if self.navigate:
            ttk.Button(top,text="🏠 ראשי",
                       command=lambda:self.navigate("dashboard")).pack(side="left")

    @contextmanager
    def import_progress(self,total):
        window=tk.Toplevel(self)
        window.title("Import CSV")
        window.transient(self.winfo_toplevel())
        window.resizable(False,False)
        window.protocol("WM_DELETE_WINDOW",lambda:None)
        label=ttk.Label(window,text=f"רשומה 0 מתוך {total}")
        label.pack(padx=20,pady=(16,8))
        progress=ttk.Progressbar(window,mode="determinate",maximum=max(total,1),length=320)
        progress.pack(padx=20,pady=(0,16))
        window.update_idletasks()

        def update(current):
            progress["value"]=current
            label.config(text=f"רשומה {current} מתוך {total}")
            window.update_idletasks()

        try:
            yield update
        finally:
            if window.winfo_exists():
                window.destroy()
