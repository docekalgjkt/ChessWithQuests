class Kun(Figurka):
    def __init__(self, barva: int, pozice: Pozice):
        super().__init__("Kůň", barva, pozice)
        self.hodnota = 3
        self.symbol = "♘" if barva == 0 else "♞"
        self.skok = True
        self.vektory = [
            [-2, -1], [-2, 1], [-1, -2], [-1, 2],
            [1, -2], [1, 2], [2, -1], [2, 1]
        ]
        self.vektory_utoku = self.vektory