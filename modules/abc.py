from modules.isolation import get_name

__name__ = get_name()

class Component:
    def __init__(self, name, brand, uuid):
       self.name = name
       self.brand = brand
       self.uuid = uuid
    def str(self): return f"{self.name} - {self.brand}"
    def __str__(self): return self.str()
