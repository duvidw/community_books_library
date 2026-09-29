from .base_model import Model

class Reservation(Model):
    table = "reservations"
    fields = ("id","book_id","user_id","reservation_date","status","notes")
