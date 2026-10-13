class Dama(Figurka):
    def __init__(self, barva: int, pozice: Pozice):
        super().__init__("Dáma", barva, pozice)
        self.hodnota = 9
        self.symbol = "♕" if barva == 0 else "♛"
        self.skok = False
        self.vektory = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1],           [0, 1],
            [1, -1],  [1, 0],  [1, 1]
        ]
        self.vektory_utoku = self.vektory