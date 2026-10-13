class Vez(Figurka):
    def __init__(self, barva: int, pozice: Pozice):
        super().__init__("Věž", barva, pozice)
        self.hodnota = 5
        self.symbol = "♖" if barva == 0 else "♜"
        self.skok = False
        self.vektory = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        self.vektory_utoku = self.vektory