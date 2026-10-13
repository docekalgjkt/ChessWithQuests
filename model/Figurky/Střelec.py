class Strelec(Figurka):
    def __init__(self, barva: int, pozice: Pozice):
        super().__init__("Střelec", barva, pozice)
        self.hodnota = 3
        self.symbol = "♗" if barva == 0 else "♝"
        self.skok = False
        self.vektory = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
        self.vektory_utoku = self.vektory