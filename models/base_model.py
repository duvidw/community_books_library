class Model:
    table = ""
    fields = ()

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    def to_dict(self):
        return {field: getattr(self, field, None) for field in self.fields}
