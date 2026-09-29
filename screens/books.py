import tkinter as tk
from tkinter import ttk,messagebox,filedialog
from repositories.books_repository import BooksRepository
from csv_utils import export_rows,import_rows
from .base_screen import BaseScreen

FIELDS=[("isbn","ISBN"),("title","שם הספר"),("author","מחבר"),("publisher","הוצאה"),
("year","שנה"),("category","קטגוריה"),("copies","עותקים"),("available_copies","זמינים"),
("notes","הערות"),("summary","תקציר")]
FORM_LAYOUT=[("summary","isbn"),("title","author"),("publisher","year"),
("category","copies"),("available_copies","notes")]
COLUMN_FIELDS=FIELDS[:-1]
CATEGORY_OPTIONS=("נוער","מבוגרים","עיון","אנגלית")
SUMMARY_MAX_LENGTH=1000

class BooksScreen(BaseScreen):
    title="ניהול ספרים"
    def __init__(self,parent,navigate=None):
        super().__init__(parent,navigate); self.repo=BooksRepository(); self.selected=None; self.e={}
        self.build(); self.refresh()

    def build(self):
        bar=tk.Frame(self,bg="#f3f4f6");bar.pack(fill="x",padx=20,pady=5)
        tk.Label(bar,text="חיפוש לפי שם:",bg="#f3f4f6").pack(side="right")
        self.title_search=tk.Entry(bar,width=18);self.title_search.pack(side="right",padx=7)
        self.title_search.bind("<KeyRelease>",lambda e:self.refresh())
        tk.Label(bar,text="חיפוש לפי מחבר:",bg="#f3f4f6").pack(side="right")
        self.author_search=tk.Entry(bar,width=18);self.author_search.pack(side="right",padx=7)
        self.author_search.bind("<KeyRelease>",lambda e:self.refresh())
        for t,c in [("ספר חדש",self.clear),("Import CSV",self.imp),("Export CSV",self.exp)]:
            ttk.Button(bar,text=t,command=c).pack(side="right",padx=4)
        form=tk.LabelFrame(self,text="פרטי ספר",bg="#f3f4f6",labelanchor="ne");form.pack(fill="x",padx=20,pady=8)
        form.grid_anchor("e")
        labels=dict(FIELDS)
        for row,keys in enumerate(FORM_LAYOUT):
            for c,k in enumerate(keys):
                tk.Label(form,text=labels[k],bg="#f3f4f6").grid(
                    row=row,column=c*2+1,padx=5,pady=4,sticky="e")
                if k=="category":
                    e=ttk.Combobox(form,width=32,values=CATEGORY_OPTIONS,state="readonly")
                elif k=="summary":
                    e=tk.Text(form,width=34,height=4,wrap="word")
                    e.bind("<KeyRelease>",self.limit_summary)
                else:
                    e=tk.Entry(form,width=34)
                e.grid(row=row,column=c*2,padx=5,pady=4,sticky="e");self.e[k]=e
        b=tk.Frame(form,bg="#f3f4f6");b.grid(row=6,column=0,columnspan=4)
        ttk.Button(b,text="שמור",command=self.save).pack(side="right",padx=4)
        ttk.Button(b,text="מחק",command=self.delete).pack(side="right",padx=4)
        self.selected_label=tk.Label(b,text="לא נבחר ספר",bg="#f3f4f6")
        self.selected_label.pack(side="left",padx=12)
        cols=["id"]+[x[0] for x in COLUMN_FIELDS];self.tree=ttk.Treeview(self,columns=cols,show="headings")
        for col in cols:
            self.tree.heading(col,text={"id":"ID",**dict(COLUMN_FIELDS)}[col],anchor="e")
            self.tree.column(col,width=100,anchor="e")
        self.tree.pack(fill="both",expand=True,padx=20,pady=8);self.tree.bind("<<TreeviewSelect>>",self.select)

    def refresh(self):
        if not hasattr(self,"tree"):return
        self.tree.delete(*self.tree.get_children())
        for r in self.repo.list(self.title_search.get(),self.author_search.get()):self.tree.insert("", "end",values=[r["id"]]+[r[k] for k,_ in COLUMN_FIELDS])

    def select(self,e=None):
        s=self.tree.selection()
        if not s:return
        v=self.tree.item(s[0],"values");self.selected=int(v[0])
        self.selected_label.config(text=f"ספר נבחר: {self.selected} | {v[2]}")
        book=self.repo.get(self.selected)
        for k,_ in FIELDS:self.set_field(k,book[k] if book[k] is not None else "")

    def clear(self):
        self.selected=None
        self.selected_label.config(text="לא נבחר ספר")
        for k in self.e:self.set_field(k,"")
        self.e["copies"].insert(0,"1");self.e["available_copies"].insert(0,"1")

    def save(self):
        d=[self.get_field(k).strip() for k,_ in FIELDS]
        try:
            d[4]=int(d[4]) if d[4] else None;d[6]=int(d[6] or 1);d[7]=int(d[7] or d[6])
            if not d[1]:raise ValueError("יש להזין שם ספר.")
            self.repo.save(d,self.selected);self.refresh();self.clear()
        except Exception as e:messagebox.showerror("שגיאה",str(e))

    def delete(self):
        if self.selected and messagebox.askyesno("מחיקה","למחוק את הספר?"):
            try:self.repo.delete(self.selected);self.refresh();self.clear()
            except Exception as e:messagebox.showerror("שגיאה",str(e))

    def exp(self):
        p=filedialog.asksaveasfilename(defaultextension=".csv",filetypes=[("CSV","*.csv")])
        if p:export_rows(p,self.repo.list(self.title_search.get(),self.author_search.get()),["id"]+[x[0] for x in FIELDS])

    def imp(self):
        p=filedialog.askopenfilename(initialdir="../repos",filetypes=[("CSV","*.csv")])
        if not p:return
        try:
            records=import_rows(p)
            with self.import_progress(len(records)) as update_progress:
                for index,r in enumerate(records,1):
                    d=[r.get(k,"") for k,_ in FIELDS]
                    d[4]=int(d[4]) if d[4] else None;d[6]=int(d[6] or 1);d[7]=int(d[7] or d[6])
                    if d[1]:self.repo.save(d)
                    update_progress(index)
            self.refresh()
        except Exception as e:messagebox.showerror("Import",str(e))

    def get_field(self,key):
        if key=="summary":
            return self.e[key].get("1.0","end-1c")
        return self.e[key].get()

    def set_field(self,key,value):
        if key=="summary":
            self.e[key].delete("1.0","end")
            self.e[key].insert("1.0",value)
        elif key=="category":
            self.e[key].set(value)
        else:
            self.e[key].delete(0,"end")
            self.e[key].insert(0,value)

    def limit_summary(self,event=None):
        summary=self.e["summary"].get("1.0","end-1c")
        if len(summary)>SUMMARY_MAX_LENGTH:
            self.e["summary"].delete("1.0","end")
            self.e["summary"].insert("1.0",summary[:SUMMARY_MAX_LENGTH])
