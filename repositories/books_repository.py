from database import get_connection

class BooksRepository:
    fields=("isbn","title","author","publisher","year","category","copies",
            "available_copies","notes","summary")

    def list(self,title="",author=""):
        title_search=f"%{title}%"
        author_search=f"%{author}%"
        with get_connection() as c:
            return c.execute("""
            SELECT * FROM books
            WHERE title LIKE ? AND author LIKE ?
            ORDER BY title
            """,(title_search,author_search)).fetchall()

    def get(self,book_id):
        with get_connection() as c:
            return c.execute("SELECT * FROM books WHERE id=?",(book_id,)).fetchone()

    def save(self,data,book_id=None):
        with get_connection() as c:
            if book_id:
                c.execute("""UPDATE books SET isbn=?,title=?,author=?,publisher=?,year=?,
                    category=?,copies=?,available_copies=?,notes=?,summary=? WHERE id=?""",
                    (*data,book_id))
            else:
                c.execute("""INSERT INTO books
                    (isbn,title,author,publisher,year,category,copies,available_copies,notes,summary)
                    VALUES (?,?,?,?,?,?,?,?,?,?)""",data)

    def delete(self,book_id):
        with get_connection() as c:
            loans=c.execute("SELECT COUNT(*) AS n FROM loans WHERE book_id=?",(book_id,)).fetchone()["n"]
            reservations=c.execute("SELECT COUNT(*) AS n FROM reservations WHERE book_id=?",(book_id,)).fetchone()["n"]
            if loans or reservations:
                raise ValueError(
                    f"לא ניתן למחוק את הספר כי קיימות רשומות מקושרות: {loans} השאלות ו-{reservations} הזמנות.\n"
                    "מומלץ להשאיר את הספר במאגר או לסמן אותו כלא זמין."
                )
            c.execute("DELETE FROM books WHERE id=?",(book_id,))
