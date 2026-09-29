from .base_model import Model

class Loan(Model):
    table = "loans"
    fields = ("id","book_id","user_id","loan_date","due_date",
              "return_date","status","notes")
