from .base_model import Model

class Book(Model):
    table = "books"
    fields = ("id","isbn","title","author","publisher","year",
              "category","copies","available_copies","notes","summary")

    @property
    def is_available(self):
        return (self.available_copies or 0) > 0
