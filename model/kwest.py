class Kwest:
    def __init__(self, nazev, popis):
        self.nazev = nazev
        self.popis = popis

    def validate(self):
        if self.nazev and self.popis:
            return True
        return False

    def __str__(self):
        return f"Kwest: {self.nazev}"