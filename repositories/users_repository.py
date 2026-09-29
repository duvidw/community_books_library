from database import get_connection

class UsersRepository:
    fields = ("member_no","first_name","last_name","phone","email",
              "address","join_date","active","notes")

    def list(self, search=""):
        s=f"%{search}%"
        with get_connection() as c:
            return c.execute("""
            SELECT * FROM users
            WHERE member_no LIKE ? OR first_name LIKE ? OR last_name LIKE ?
               OR phone LIKE ? OR email LIKE ?
            ORDER BY last_name, first_name
            """,(s,s,s,s,s)).fetchall()

    def get(self, user_id):
        with get_connection() as c:
            return c.execute("SELECT * FROM users WHERE id=?",(user_id,)).fetchone()

    def exists(self, member_no="", first_name="", last_name=""):
        """Return True when an imported user already exists.

        Member number is the primary duplicate key. If no member number is
        supplied, first name + last name are used. This method is read-only
        and never changes an existing user.
        """
        with get_connection() as c:
            if member_no:
                row=c.execute(
                    "SELECT id FROM users WHERE member_no=? LIMIT 1",
                    (member_no,)
                ).fetchone()
                if row:
                    return True
            if first_name and last_name:
                row=c.execute(
                    "SELECT id FROM users WHERE first_name=? AND last_name=? LIMIT 1",
                    (first_name,last_name)
                ).fetchone()
                if row:
                    return True
        return False

    def save(self, data, user_id=None):
        with get_connection() as c:
            if user_id:
                c.execute("""UPDATE users SET member_no=?,first_name=?,last_name=?,
                    phone=?,email=?,address=?,join_date=?,active=?,notes=? WHERE id=?""",
                    (*data,user_id))
            else:
                c.execute("""INSERT INTO users
                    (member_no,first_name,last_name,phone,email,address,join_date,active,notes)
                    VALUES (?,?,?,?,?,?,?,?,?)""",data)

    def delete(self,user_id):
        with get_connection() as c:
            loans=c.execute("SELECT COUNT(*) AS n FROM loans WHERE user_id=?",(user_id,)).fetchone()["n"]
            reservations=c.execute("SELECT COUNT(*) AS n FROM reservations WHERE user_id=?",(user_id,)).fetchone()["n"]
            if loans or reservations:
                raise ValueError(
                    f"לא ניתן למחוק את המשתמש כי קיימות רשומות מקושרות: {loans} השאלות ו-{reservations} הזמנות.\n"
                    "במקום מחיקה, יש להפוך את המשתמש ל'לא פעיל'."
                )
            c.execute("DELETE FROM users WHERE id=?",(user_id,))

    def deactivate(self,user_id):
        with get_connection() as c:
            c.execute("UPDATE users SET active=0 WHERE id=?",(user_id,))
