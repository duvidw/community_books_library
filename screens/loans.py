import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from calendar import monthrange
from datetime import date
from database import fetchall
from repositories.loans_repository import LoansRepository
from csv_utils import export_rows, import_rows
from .base_screen import BaseScreen

class LoansScreen(BaseScreen):
    title="ניהול השאלות"

    def __init__(self,parent,navigate=None,selected_book_id=None,selected_user_id=None):
        super().__init__(parent,navigate)
        self.repo=LoansRepository()
        self.selected=None
        self.books=[]
        self.users=[]
        self.book_map={}
        self.user_map={}
        self.build()
        self.load_lists()
        self.clear()
        if selected_book_id is not None:
            self.set_book(selected_book_id)
            self.book_selected()
        if selected_user_id is not None:
            self.set_user(selected_user_id)
        self.refresh()

    def build(self):
        bar=tk.Frame(self,bg="#f3f4f6"); bar.pack(fill="x",padx=20,pady=5)
        tk.Label(bar,text="חיפוש לפי שם משתמש:",bg="#f3f4f6").pack(side="right")
        self.user_search=tk.Entry(bar,width=16,font=("Arial",11))
        self.user_search.pack(side="right",padx=7)
        self.user_search.bind("<KeyRelease>",lambda e:self.refresh())
        tk.Label(bar,text="חיפוש לפי שם ספר:",bg="#f3f4f6").pack(side="right")
        self.book_search=tk.Entry(bar,width=16,font=("Arial",11))
        self.book_search.pack(side="right",padx=7)
        self.book_search.bind("<KeyRelease>",lambda e:self.refresh())

        for text,cmd in [
            ("השאלה חדשה",self.clear),("החזרת ספר",self.return_book),
            ("Import CSV",self.imp),("Export CSV",self.exp)]:
            ttk.Button(bar,text=text,command=cmd).pack(side="right",padx=4)

        form=tk.LabelFrame(self,text="פרטי השאלה",bg="#f3f4f6",
                           font=("Arial",11,"bold"),labelanchor="ne")
        form.pack(fill="x",padx=20,pady=8)
        form.grid_anchor("e")

        tk.Label(form,text="ספר:",bg="#f3f4f6").grid(row=0,column=3,padx=6,pady=6,sticky="e")
        self.book_var=tk.StringVar()
        self.book_combo=ttk.Combobox(form,textvariable=self.book_var,width=52,state="readonly",justify="right")
        self.book_combo.grid(row=0,column=2,padx=6,pady=6,sticky="e")
        self.book_combo.bind("<<ComboboxSelected>>",self.book_selected)

        self.available_label=tk.Label(form,text="זמינים: -",bg="#f3f4f6",
                                      font=("Arial",11,"bold"))
        self.available_label.grid(row=0,column=0,padx=12,sticky="w")

        tk.Label(form,text="משתמש:",bg="#f3f4f6").grid(row=1,column=3,padx=6,pady=6,sticky="e")
        self.user_var=tk.StringVar()
        self.user_combo=ttk.Combobox(form,textvariable=self.user_var,width=52,state="readonly",justify="right")
        self.user_combo.grid(row=1,column=2,padx=6,pady=6,sticky="e")

        labels=[
            ("loan_date","תאריך השאלה:",2),
            ("due_date","להחזיר עד:",3),
            ("return_date","תאריך החזרה:",4)]
        for key,label,row in labels:
            tk.Label(form,text=label,bg="#f3f4f6").grid(row=row,column=3,padx=6,pady=6,sticky="e")
            e=tk.Entry(form,width=20,justify="right")
            e.grid(row=row,column=2,padx=6,pady=6,sticky="e")
            setattr(self,key,e)

        tk.Label(form,text="סטטוס:",bg="#f3f4f6").grid(row=5,column=3,padx=6,pady=6,sticky="e")
        self.status_var=tk.StringVar(value="borrowed")
        ttk.Combobox(form,textvariable=self.status_var,
                     values=("borrowed","returned","late"),
                     width=18,state="readonly",justify="right").grid(row=5,column=2,padx=6,pady=6,sticky="e")

        tk.Label(form,text="הערות:",bg="#f3f4f6").grid(row=6,column=3,padx=6,pady=6,sticky="e")
        self.notes=tk.Entry(form,width=52,justify="right")
        self.notes.grid(row=6,column=2,padx=6,pady=6,sticky="e")

        buttons=tk.Frame(form,bg="#f3f4f6"); buttons.grid(row=7,column=0,columnspan=4,pady=8)
        ttk.Button(buttons,text="שמור / עדכן",command=self.save).pack(side="right",padx=5)
        ttk.Button(buttons,text="נקה",command=self.clear).pack(side="right",padx=5)
        ttk.Button(buttons,text="מחק",command=self.delete).pack(side="right",padx=5)

        cols=["id","book_title","member_no","user_name","loan_date","due_date",
              "return_date","status","notes"]
        table=tk.Frame(self); table.pack(fill="both",expand=True,padx=20,pady=8)
        self.tree=ttk.Treeview(table,columns=cols,show="headings")
        heads={"id":"ID","book_title":"ספר","member_no":"מספר חבר","user_name":"משתמש",
               "loan_date":"תאריך השאלה","due_date":"להחזיר עד",
               "return_date":"הוחזר","status":"סטטוס","notes":"הערות"}
        widths={"id":50,"book_title":220,"member_no":100,"user_name":170,
                "loan_date":105,"due_date":105,"return_date":105,"status":90,"notes":180}
        for c in cols:
            self.tree.heading(c,text=heads[c],anchor="e"); self.tree.column(c,width=widths[c],anchor="e")
        self.tree.pack(side="left",fill="both",expand=True)
        sb=ttk.Scrollbar(table,orient="vertical",command=self.tree.yview)
        sb.pack(side="right",fill="y"); self.tree.configure(yscrollcommand=sb.set)
        self.tree.bind("<<TreeviewSelect>>",self.select)

    def load_lists(self):
        self.books=fetchall("SELECT id,title,isbn,available_copies,copies FROM books ORDER BY title")
        self.users=fetchall("""SELECT id,member_no,first_name,last_name,active
                               FROM users WHERE active=1 ORDER BY last_name,first_name""")

        self.book_map={}
        values=[]
        for b in self.books:
            text=f'{b["title"]} | ISBN: {b["isbn"] or "-"} | זמינים: {b["available_copies"]}'
            self.book_map[text]=b["id"]; values.append(text)
        self.book_combo["values"]=values

        self.user_map={}
        values=[]
        for u in self.users:
            text=f'{u["member_no"] or "-"} | {u["first_name"]} {u["last_name"]}'
            self.user_map[text]=u["id"]; values.append(text)
        self.user_combo["values"]=values

    def book_selected(self,event=None):
        book_id=self.book_map.get(self.book_var.get())
        row=next((b for b in self.books if b["id"]==book_id),None)
        self.available_label.config(
            text=f'זמינים: {row["available_copies"]} מתוך {row["copies"]}' if row else "זמינים: -")

    def refresh(self):
        if not hasattr(self,"tree"): return
        self.tree.delete(*self.tree.get_children())
        for r in self.repo.list(self.user_search.get(),self.book_search.get()):
            self.tree.insert("", "end",values=[
                r["id"],r["book_title"],r["member_no"],
                f'{r["first_name"]} {r["last_name"]}',
                r["loan_date"],r["due_date"],r["return_date"],
                r["status"],r["notes"]])

    def select(self,event=None):
        s=self.tree.selection()
        if not s:return
        self.selected=int(self.tree.item(s[0],"values")[0])
        r=self.repo.get(self.selected)
        if not r:return
        self.set_book(r["book_id"]); self.set_user(r["user_id"])
        for widget,key in [
            (self.loan_date,"loan_date"),(self.due_date,"due_date"),
            (self.return_date,"return_date"),(self.notes,"notes")]:
            widget.delete(0,"end"); widget.insert(0,r[key] or "")
        self.status_var.set(r["status"] or "borrowed")
        self.book_selected()

    def set_book(self,book_id):
        for text,bid in self.book_map.items():
            if bid==book_id:self.book_var.set(text);return

    def set_user(self,user_id):
        for text,uid in self.user_map.items():
            if uid==user_id:self.user_var.set(text);return

    def clear(self):
        self.selected=None
        self.load_lists()
        self.book_var.set(""); self.user_var.set("")
        self.available_label.config(text="זמינים: -")
        today=date.today()
        next_month=today.month % 12 + 1
        next_year=today.year + (today.month == 12)
        due_day=min(today.day,monthrange(next_year,next_month)[1])
        due_date=date(next_year,next_month,due_day)
        self.loan_date.delete(0,"end"); self.loan_date.insert(0,today.isoformat())
        self.due_date.delete(0,"end"); self.due_date.insert(0,due_date.isoformat())
        self.return_date.delete(0,"end"); self.status_var.set("borrowed")
        self.notes.delete(0,"end")

    def save(self):
        book_id=self.book_map.get(self.book_var.get())
        user_id=self.user_map.get(self.user_var.get())
        if not book_id:
            messagebox.showwarning("חסר ספר","בחר ספר."); return
        if not user_id:
            messagebox.showwarning("חסר משתמש","בחר משתמש."); return

        data=[book_id,user_id,self.loan_date.get().strip(),self.due_date.get().strip(),
              self.return_date.get().strip() or None,self.status_var.get(),
              self.notes.get().strip()]
        if not data[2]:
            messagebox.showwarning("חסר תאריך","יש להזין תאריך השאלה."); return
        try:
            self.repo.save(data,self.selected)
            self.refresh(); self.clear(); self.set_user(user_id)
            messagebox.showinfo("השאלה","השאלה נשמרה בהצלחה.")
        except Exception as e: messagebox.showerror("שגיאה",str(e))

    def return_book(self):
        if not self.selected:
            messagebox.showwarning("החזרה","בחר השאלה מהרשימה."); return
        try:
            self.repo.return_book(self.selected)
            self.load_lists(); self.refresh(); self.clear()
            messagebox.showinfo("החזרה","הספר הוחזר בהצלחה.")
        except Exception as e: messagebox.showerror("שגיאה",str(e))

    def delete(self):
        if not self.selected:return
        if not messagebox.askyesno("מחיקה","למחוק את רשומת ההשאלה?"):return
        try:
            self.repo.delete(self.selected)
            self.load_lists(); self.refresh(); self.clear()
        except Exception as e:messagebox.showerror("שגיאה",str(e))

    def exp(self):
        p=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if not p:return
        export_rows(p,self.repo.list(self.user_search.get(),self.book_search.get()),
                    ["id","book_title","member_no","first_name","last_name",
                     "loan_date","due_date","return_date","status","notes"])
        messagebox.showinfo("Export","הייצוא הסתיים בהצלחה.")

    def imp(self):
        p=filedialog.askopenfilename(initialdir="../repos",filetypes=[("CSV","*.csv")])
        if not p:return
        try:
            count=0
            records=import_rows(p)
            with self.import_progress(len(records)) as update_progress:
                for index,r in enumerate(records,1):
                    data=[r.get("book_id",""),r.get("user_id",""),r.get("loan_date",""),
                          r.get("due_date",""),r.get("return_date","") or None,
                          r.get("status","borrowed") or "borrowed",r.get("notes","")]
                    if data[0] and data[1] and data[2]:
                        self.repo.save(data); count+=1
                    update_progress(index)
            self.load_lists(); self.refresh()
            messagebox.showinfo("Import",f"יובאו {count} רשומות.")
        except Exception as e:messagebox.showerror("Import",str(e))
