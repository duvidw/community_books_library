from database import get_connection

class BooksRepository:
    fields=("book_code","isbn","title","author","publisher","year","category","copies",
            "available_copies","notes","summary")

    def list(self,title="",author="",book_code=""):
        title_search=f"%{title}%"
        author_search=f"%{author}%"
        book_code_search=f"%{book_code}%"
        with get_connection() as c:
            return c.execute("""
            SELECT * FROM books
                        WHERE COALESCE(title,'') LIKE ?
                            AND COALESCE(author,'') LIKE ?
                            AND COALESCE(book_code,'') LIKE ?
            ORDER BY title
            """,(title_search,author_search,book_code_search)).fetchall()

    def get(self,book_id):
        with get_connection() as c:
            return c.execute("SELECT * FROM books WHERE id=?",(book_id,)).fetchone()

    def save(self,data,book_id=None):
        with get_connection() as c:
            if book_id:
                c.execute("""UPDATE books SET book_code=?,isbn=?,title=?,author=?,publisher=?,year=?,
                    category=?,copies=?,available_copies=?,notes=?,summary=? WHERE id=?""",
                    (*data,book_id))
            else:
                c.execute("""INSERT INTO books
                    (book_code,isbn,title,author,publisher,year,category,copies,available_copies,notes,summary)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)""",data)

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
