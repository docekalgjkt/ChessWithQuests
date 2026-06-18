class Herni_Plocha:
    def __init__(self):
        self.rozmery = (8, 8)
        self.herni_deska = []
        self.vyhozene_figurky_b = []
        self.vyhozene_figurky_c = []

        for radek in range(8):
            self.herni_deska.append([None] * 8)

    def vrat_obsah(self, souradnice):
        radek, sloupec = souradnice
        if 0 <= radek < 8 and 0 <= sloupec < 8:
            return self.herni_deska[radek][sloupec]
        return None

    def poloz_figurku(self, figurka, souradnice):
        radek, sloupec = souradnice
        self.herni_deska[radek][sloupec] = figurka
        figurka.pozice = [radek, sloupec]

    def __str__(self):
        return f"Herni_Plocha {self.rozmery}"