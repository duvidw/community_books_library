from .base_model import Model

class User(Model):
    table = "users"
    fields = ("id","member_no","first_name","last_name","phone","email",
              "address","join_date","active","notes")

    @property
    def full_name(self):
        return f"{self.first_name or ''} {self.last_name or ''}".strip()
