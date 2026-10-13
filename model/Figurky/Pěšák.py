class Pesak(Figurka):
    def __init__(self, barva: int, pozice: Pozice):
        super().__init__("Pěšák", barva, pozice)
        self.hodnota = 1
        self.symbol = "♙" if barva == 0 else "♟"
        self.skok = False
        self.smer = -1 if barva == 0 else 1
        self.vektory = [[self.smer, 0]]
        self.vektory_utoku = [[self.smer, -1], [self.smer, 1]]