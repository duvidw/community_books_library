import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from repositories.reservations_repository import ReservationsRepository
from csv_utils import export_rows,import_rows
from .base_screen import BaseScreen

FIELDS=[("book_id","ID ספר"),("user_id","ID משתמש"),("reservation_date","תאריך הזמנה"),
("status","סטטוס"),("notes","הערות")]

class ReservationsScreen(BaseScreen):
    title="ניהול הזמנות ספרים"
    def __init__(self,parent,navigate=None):
        super().__init__(parent,navigate);self.repo=ReservationsRepository();self.selected=None;self.e={}
        self.build();self.refresh()

    def build(self):
        bar=tk.Frame(self,bg="#f3f4f6");bar.pack(fill="x",padx=20,pady=5)
        tk.Label(bar,text="חיפוש:",bg="#f3f4f6").pack(side="right")
        self.search=tk.Entry(bar,width=30);self.search.pack(side="right",padx=7)
        self.search.bind("<KeyRelease>",lambda e:self.refresh())
        for t,c in [("הזמנה חדשה",self.clear),("Import CSV",self.imp),("Export CSV",self.exp)]:
            ttk.Button(bar,text=t,command=c).pack(side="right",padx=4)
        form=tk.LabelFrame(self,text="פרטי הזמנה",bg="#f3f4f6",labelanchor="ne");form.pack(fill="x",padx=20,pady=8)
        form.grid_anchor("e")
        for i,(k,l) in enumerate(FIELDS):
            r,c=divmod(i,2)
            tk.Label(form,text=l,bg="#f3f4f6").grid(row=r,column=c*2+1,padx=5,pady=4,sticky="e")
            e=tk.Entry(form,width=34);e.grid(row=r,column=c*2,padx=5,pady=4,sticky="e");self.e[k]=e
        b=tk.Frame(form,bg="#f3f4f6");b.grid(row=3,column=0,columnspan=4)
        ttk.Button(b,text="שמור",command=self.save).pack(side="right",padx=4)
        ttk.Button(b,text="מחק",command=self.delete).pack(side="right",padx=4)
        cols=["book_title","member_no","user_name"]+[x[0] for x in FIELDS]
        self.tree=ttk.Treeview(self,columns=cols,show="headings")
        heads={"book_title":"ספר","member_no":"מספר חבר","user_name":"משתמש",**dict(FIELDS)}
        for c in cols:
            self.tree.heading(c,text=heads[c],anchor="e");self.tree.column(c,width=100,anchor="e")
        self.tree.pack(fill="both",expand=True,padx=20,pady=8);self.tree.bind("<<TreeviewSelect>>",self.select)

    def refresh(self):
        if not hasattr(self,"tree"):return
        self.tree.delete(*self.tree.get_children())
        for r in self.repo.list(self.search.get()):
            vals=[r["book_title"],r["member_no"],f'{r["first_name"]} {r["last_name"]}']+[r[k] for k,_ in FIELDS]
            self.tree.insert("", "end",iid=str(r["id"]),values=vals)

    def select(self,e=None):
        s=self.tree.selection()
        if not s:return
        v=self.tree.item(s[0],"values");self.selected=int(s[0])
        for i,(k,_) in enumerate(FIELDS,3):
            self.e[k].delete(0,"end");self.e[k].insert(0,v[i] if v[i] is not None else "")

    def clear(self):
        self.selected=None
        for e in self.e.values():e.delete(0,"end")
        from datetime import date
        self.e["reservation_date"].insert(0,date.today().isoformat());self.e["status"].insert(0,"waiting")

    def save(self):
        d=[self.e[k].get().strip() for k,_ in FIELDS]
        try:self.repo.save(d,self.selected);self.refresh();self.clear()
        except Exception as e:messagebox.showerror("שגיאה",str(e))

    def delete(self):
        if self.selected and messagebox.askyesno("מחיקה","למחוק את ההזמנה?"):
            try:self.repo.delete(self.selected);self.refresh();self.clear()
            except Exception as e:messagebox.showerror("שגיאה",str(e))

    def exp(self):
        p=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if p:export_rows(p,self.repo.list(self.search.get()),["id","book_title","member_no","first_name","last_name"]+[x[0] for x in FIELDS])

    def imp(self):
        p=filedialog.askopenfilename(initialdir="../repos",filetypes=[("CSV","*.csv")])
        if not p:return
        try:
            records=import_rows(p)
            with self.import_progress(len(records)) as update_progress:
                for index,r in enumerate(records,1):
                    self.repo.save([r.get(k,"") for k,_ in FIELDS])
                    update_progress(index)
            self.refresh()
        except Exception as e:messagebox.showerror("Import",str(e))
