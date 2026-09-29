from database import get_connection

class ReservationsRepository:
    fields=("book_id","user_id","reservation_date","status","notes")

    def list(self,search=""):
        s=f"%{search}%"
        with get_connection() as c:
            return c.execute("""
            SELECT r.*,b.title AS book_title,u.member_no,u.first_name,u.last_name
            FROM reservations r
            JOIN books b ON b.id=r.book_id
            JOIN users u ON u.id=r.user_id
            WHERE b.title LIKE ? OR u.first_name LIKE ? OR u.last_name LIKE ?
               OR u.member_no LIKE ? OR r.status LIKE ?
            ORDER BY r.id DESC
            """,(s,s,s,s,s)).fetchall()

    def save(self,data,reservation_id=None):
        with get_connection() as c:
            if reservation_id:
                c.execute("""UPDATE reservations SET book_id=?,user_id=?,reservation_date=?,
                    status=?,notes=? WHERE id=?""",(*data,reservation_id))
            else:
                c.execute("""INSERT INTO reservations
                    (book_id,user_id,reservation_date,status,notes)
                    VALUES (?,?,?,?,?)""",data)

    def delete(self,reservation_id):
        with get_connection() as c:
            c.execute("DELETE FROM reservations WHERE id=?",(reservation_id,))
