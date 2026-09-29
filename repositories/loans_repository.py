from database import get_connection
from datetime import date

class LoansRepository:
    def overdue(self):
        with get_connection() as c:
            return c.execute("""
            SELECT l.id, l.due_date,
                   b.title AS book_title,
                   u.first_name, u.last_name, u.email
            FROM loans l
            JOIN books b ON b.id=l.book_id
            JOIN users u ON u.id=l.user_id
            WHERE l.status='borrowed'
              AND l.return_date IS NULL
              AND l.due_date IS NOT NULL
              AND date(l.due_date) < date('now')
            ORDER BY date(l.due_date), b.title
            """).fetchall()

    def list(self, user_name="", book_title="", user_id=None, book_id=None):
        user_search=f"%{user_name}%"
        book_search=f"%{book_title}%"
        with get_connection() as c:
            conditions=["(u.first_name || ' ' || u.last_name) LIKE ?", "b.title LIKE ?"]
            params=[user_search,book_search]
            if user_id is not None:
                conditions.append("l.user_id=?")
                params.append(user_id)
            if book_id is not None:
                conditions.append("l.book_id=?")
                params.append(book_id)
            return c.execute(f"""
            SELECT l.*, b.title AS book_title, b.isbn AS book_isbn,
                   b.available_copies,
                   u.member_no, u.first_name, u.last_name
            FROM loans l
            JOIN books b ON b.id=l.book_id
            JOIN users u ON u.id=l.user_id
            WHERE {' AND '.join(conditions)}
            ORDER BY l.id DESC
            """,params).fetchall()

    def get(self, loan_id):
        with get_connection() as c:
            return c.execute("SELECT * FROM loans WHERE id=?", (loan_id,)).fetchone()

    def save(self, data, loan_id=None):
        with get_connection() as c:
            if loan_id:
                old=c.execute("SELECT * FROM loans WHERE id=?", (loan_id,)).fetchone()
                if not old:
                    raise ValueError("ההשאלה לא נמצאה.")
                old_active=old["status"]=="borrowed" and not old["return_date"]
                new_active=data[5]=="borrowed" and not data[4]
                new_book_id=int(data[0])

                if old["book_id"] != new_book_id:
                    if old_active:
                        c.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?",
                                  (old["book_id"],))
                    if new_active:
                        b=c.execute("SELECT available_copies FROM books WHERE id=?",
                                    (new_book_id,)).fetchone()
                        if not b or b["available_copies"] <= 0:
                            raise ValueError("אין עותק זמין של הספר החדש.")
                        c.execute("UPDATE books SET available_copies=available_copies-1 WHERE id=?",
                                  (new_book_id,))
                elif old_active and not new_active:
                    c.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?",
                              (new_book_id,))
                elif not old_active and new_active:
                    b=c.execute("SELECT available_copies FROM books WHERE id=?",
                                (new_book_id,)).fetchone()
                    if not b or b["available_copies"] <= 0:
                        raise ValueError("אין עותק זמין של הספר.")
                    c.execute("UPDATE books SET available_copies=available_copies-1 WHERE id=?",
                              (new_book_id,))

                c.execute("""UPDATE loans SET book_id=?,user_id=?,loan_date=?,due_date=?,
                    return_date=?,status=?,notes=? WHERE id=?""",(*data,loan_id))
            else:
                book_id=int(data[0])
                active=data[5]=="borrowed" and not data[4]
                if active:
                    b=c.execute("SELECT available_copies FROM books WHERE id=?",
                                (book_id,)).fetchone()
                    if not b or b["available_copies"] <= 0:
                        raise ValueError("אין עותק זמין של הספר.")
                    c.execute("UPDATE books SET available_copies=available_copies-1 WHERE id=?",
                              (book_id,))
                c.execute("""INSERT INTO loans
                    (book_id,user_id,loan_date,due_date,return_date,status,notes)
                    VALUES (?,?,?,?,?,?,?)""",data)

    def delete(self, loan_id):
        with get_connection() as c:
            loan=c.execute("SELECT * FROM loans WHERE id=?", (loan_id,)).fetchone()
            if loan and loan["status"]=="borrowed" and not loan["return_date"]:
                c.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?",
                          (loan["book_id"],))
            c.execute("DELETE FROM loans WHERE id=?", (loan_id,))

    def return_book(self, loan_id):
        with get_connection() as c:
            loan=c.execute("SELECT * FROM loans WHERE id=?", (loan_id,)).fetchone()
            if not loan:
                raise ValueError("ההשאלה לא נמצאה.")
            if loan["return_date"] or loan["status"]=="returned":
                return
            c.execute("""UPDATE loans SET return_date=?,status='returned' WHERE id=?""",
                      (date.today().isoformat(),loan_id))
            c.execute("UPDATE books SET available_copies=available_copies+1 WHERE id=?",
                      (loan["book_id"],))
