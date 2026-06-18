from uzivatel import Uzivatel

class Hrac:
    def __init__(self, barva, uzivatel):
        self.barva = barva
        self.uzivatel = uzivatel

    def getEloRating(self):
        return self.uzivatel.elo

    def __str__(self):
        barva_text = "Bílý" if self.barva == 0 else "Černý"
        return f"Hráč: {self.uzivatel.uzivatelske_jmeno} ({barva_text})"