import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from datetime import date
from repositories.users_repository import UsersRepository
from csv_utils import export_rows,import_rows
from .base_screen import BaseScreen

FIELDS=[
("member_no","מספר חבר"),("first_name","שם פרטי"),("last_name","שם משפחה"),
("phone","טלפון"),("email","דוא״ל"),("address","כתובת"),
("join_date","תאריך הצטרפות"),("active","פעיל"),("notes","הערות")]

class UsersScreen(BaseScreen):
    title="ניהול משתמשים"
    def __init__(self,parent,navigate=None):
        super().__init__(parent,navigate); self.repo=UsersRepository()
        self.selected=None; self.entries={}; self.build(); self.clear(); self.refresh()

    def build(self):
        bar=tk.Frame(self,bg="#f3f4f6"); bar.pack(fill="x",padx=20,pady=5)
        tk.Label(bar,text="חיפוש:",bg="#f3f4f6").pack(side="right")
        self.search=tk.Entry(bar,width=28); self.search.pack(side="right",padx=7)
        self.search.bind("<KeyRelease>",lambda e:self.refresh())
        for text,cmd in [("משתמש חדש",self.clear),("Import CSV",self.do_import),("Export CSV",self.do_export)]:
            ttk.Button(bar,text=text,command=cmd).pack(side="right",padx=4)

        form=tk.LabelFrame(self,text="פרטי משתמש",bg="#f3f4f6",labelanchor="ne")
        form.pack(fill="x",padx=20,pady=8)
        form.grid_anchor("e")
        for i,(key,label) in enumerate(FIELDS):
            r,c=divmod(i,2)
            tk.Label(form,text=label,bg="#f3f4f6").grid(row=r,column=c*2+1,padx=5,pady=4,sticky="e")
            e=tk.Entry(form,width=34); e.grid(row=r,column=c*2,padx=5,pady=4,sticky="e")
            self.entries[key]=e
        b=tk.Frame(form,bg="#f3f4f6"); b.grid(row=5,column=0,columnspan=4,pady=6)
        ttk.Button(b,text="שמור",command=self.save).pack(side="right",padx=4)
        ttk.Button(b,text="מחק",command=self.delete).pack(side="right",padx=4)
        self.selected_label=tk.Label(b,text="לא נבחר משתמש",bg="#f3f4f6")
        self.selected_label.pack(side="left",padx=12)

        cols=[x[0] for x in FIELDS]
        self.tree=ttk.Treeview(self,columns=cols,show="headings")
        for col in cols:
            self.tree.heading(col,text=dict(FIELDS)[col],anchor="e")
            self.tree.column(col,width=100,anchor="e")
        self.tree.pack(fill="both",expand=True,padx=20,pady=8)
        self.tree.bind("<<TreeviewSelect>>",self.select)
        self.tree.bind("<Double-1>",self.open_loans)

    def refresh(self):
        if not hasattr(self,"tree"): return
        self.tree.delete(*self.tree.get_children())
        for row in self.repo.list(self.search.get()):
            self.tree.insert("", "end",iid=str(row["id"]),values=[row[x[0]] for x in FIELDS])

    def select(self,e=None):
        s=self.tree.selection()
        if not s:return
        v=self.tree.item(s[0],"values"); self.selected=int(s[0])
        self.selected_label.config(text=f"משתמש נבחר: {self.selected} | {v[1]} {v[2]}")
        for i,(k,_) in enumerate(FIELDS):
            self.entries[k].delete(0,"end"); self.entries[k].insert(0,"" if v[i] is None else v[i])

    def open_loans(self,event=None):
        s=self.tree.selection()
        if not s:return
        self.selected=int(s[0])
        if self.navigate:self.navigate("loans")

    def clear(self):
        self.selected=None
        self.selected_label.config(text="לא נבחר משתמש")
        for e in self.entries.values():e.delete(0,"end")
        self.entries["join_date"].insert(0,date.today().isoformat())
        self.entries["active"].insert(0,"1")

    def save(self):
        d=[self.entries[k].get().strip() for k,_ in FIELDS]
        d[7]=0 if d[7].lower() in ("0","false","לא") else 1
        if not d[1] or not d[2]:
            messagebox.showwarning("חסר מידע","יש להזין שם פרטי ושם משפחה."); return
        try:
            self.repo.save(d,self.selected); self.refresh(); self.clear()
        except Exception as e: messagebox.showerror("שגיאה",str(e))

    def delete(self):
        if not self.selected:
            messagebox.showwarning("מחיקה","בחר משתמש מהרשימה.")
            return
        if not messagebox.askyesno("מחיקה","למחוק את המשתמש?\n\nאם יש למשתמש השאלות או הזמנות פעילות, לא ניתן למחוק אותו."):
            return
        try:
            self.repo.delete(self.selected)
            self.refresh(); self.clear()
        except Exception as e:
            # A user referenced by loans/reservations cannot be physically deleted.
            if "לא ניתן למחוק" in str(e):
                if messagebox.askyesno("המשתמש מקושר לרשומות",
                    str(e)+"\n\nהאם להפוך את המשתמש ללא פעיל?"):
                    try:
                        self.repo.deactivate(self.selected)
                        self.refresh(); self.clear()
                        messagebox.showinfo("משתמש", "המשתמש סומן כלא פעיל.")
                    except Exception as e2:
                        messagebox.showerror("שגיאה",str(e2))
            else:
                messagebox.showerror("שגיאה",str(e))

    def do_export(self):
        # p=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        p=filedialog.asksaveasfilename(initialdir="../repos", defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if p:export_rows(p,self.repo.list(self.search.get()),["id"]+[x[0] for x in FIELDS])

    def do_import(self):
        p=filedialog.askopenfilename(initialdir="../repos",filetypes=[("CSV","*.csv")])
        if not p:return
        try:
            imported=0
            skipped=0
            records=import_rows(p)
            with self.import_progress(len(records)) as update_progress:
                for index,r in enumerate(records,1):
                    # CSV import NEVER uses the database primary-key "id".
                    # SQLite creates a new ID automatically.
                    member_no=str(r.get("member_no","")).strip()
                    first_name=str(r.get("first_name","")).strip()
                    last_name=str(r.get("last_name","")).strip()

                    if not first_name or not last_name:
                        skipped += 1
                    # Do not import a user that already exists.
                    # A match is made by member number, or by first+last name
                    # when no member number is available. Existing users are
                    # never updated by Import.
                    elif self.repo.exists(member_no, first_name, last_name):
                        skipped += 1
                    else:
                        d=[r.get(k,"") for k,_ in FIELDS]
                        d[7]=0 if str(d[7]).lower() in ("0","false","לא") else 1
                        # Ignore any CSV "id" column and insert as a new user.
                        self.repo.save(d)
                        imported += 1
                    update_progress(index)

            self.refresh()
            messagebox.showinfo(
                "Import",
                f"הייבוא הסתיים.\n\nנוספו: {imported}\nדולגו משתמשים שכבר קיימים: {skipped}"
            )
        except Exception as e:
            messagebox.showerror("Import",str(e))
