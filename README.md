# Community Library Manager – Python + SQLite

דוד וינשטיין מנחה את ChatGPT ו Copilot לבנית המערכת
מערכת זו היא קוד חופשי לשימוש לא מסחרי.



מערכת מודולרית לניהול ספרייה קהילתית.

## דרישות
Python 3.10+.
Tkinter ו-SQLite מגיעים עם Python ב-Windows.

## הפעלה
הרץ:
    python main.py
או Windows:
    run_library.bat

אין צורך בשרת או בחבילת Python חיצונית.

## מבנה
main.py                 – הפעלת האפליקציה וניווט
database.py             – חיבור SQLite ואתחול
csv_utils.py            – Import / Export
models/base_model.py    – בסיס למודלי נתונים
models/user.py          – User
models/book.py          – Book
models/loan.py          – Loan
models/reservation.py   – Reservation
repositories/*.py       – פעולות CRUD ונתונים
screens/base_screen.py  – בסיס למסכים
screens/dashboard.py    – מסך פתיחה
screens/users.py        – משתמשים
screens/books.py        – ספרים
screens/loans.py        – השאלות
screens/reservations.py – הזמנות

2026-09-28 David:
* לטבלת ספרים הוסף קוד_ספר לפני ISBN
כמו כן הוסף את קוד_ספר לפרטי הספר

