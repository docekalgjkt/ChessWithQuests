class Figurka:
    def __init__(self, nazev, barva, vektory_utoku, vektory):
        self.nazev = nazev
        self.vektory_utoku = vektory_utoku
        self.barva = barva
        self.vektory = vektory
        self.pozice = None

    def get_pozice(self, seznam):
        # Vrátí aktuální pozici figurky
        return self.pozice

    def posun_figurky(self, seznam):

        if seznam and len(seznam) == 2:
            if self.pozice is not None:
                novy_radek = self.pozice[0] + seznam[0]
                novy_sloupec = self.pozice[1] + seznam[1]
                self.pozice = [novy_radek, novy_sloupec]
        return self.pozice

    def __str__(self):
        barva_text = "bílá" if self.barva == 0 else "černá"
        return f"{self.nazev} ({barva_text}) na {self.pozice}"


class Pesak(Figurka):
    def __init__(self, barva):
        if barva == 0:
            vektory = [[-1, 0]]
            vektory_utoku = [[-1, -1], [-1, 1]]
        else:
            vektory = [[1, 0]]
            vektory_utoku = [[1, -1], [1, 1]]
        super().__init__("Pěšák", barva, vektory_utoku, vektory)
        self.skok = False


class Kun(Figurka):
    def __init__(self, barva):
        vektory = [
            [-2, -1], [-2, 1],
            [-1, -2], [-1, 2],
            [1, -2],  [1, 2],
            [2, -1],  [2, 1]
        ]
        vektory_utoku = vektory
        super().__init__("Kůň", barva, vektory_utoku, vektory)
        self.skok = True


class Strelec(Figurka):
    def __init__(self, barva):
        vektory = [
            [-1, -1], [-1, 1],
            [1, -1],  [1, 1]
        ]
        vektory_utoku = vektory
        super().__init__("Střelec", barva, vektory_utoku, vektory)
        self.skok = False


class Vez(Figurka):
    def __init__(self, barva):
        vektory = [
            [-1, 0], [1, 0],
            [0, -1], [0, 1]
        ]
        vektory_utoku = vektory
        super().__init__("Věž", barva, vektory_utoku, vektory)
        self.skok = False


class Dama(Figurka):
    def __init__(self, barva):
        vektory = [
            [-1, 0], [1, 0], [0, -1], [0, 1],
            [-1, -1], [-1, 1], [1, -1], [1, 1]  # syntéza pohybů střelce a věže
        ]
        vektory_utoku = vektory
        super().__init__("Dáma", barva, vektory_utoku, vektory)
        self.skok = False


class Kral(Figurka):
    def __init__(self, barva):
        vektory = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1],           [0, 1],
            [1, -1],  [1, 0],  [1, 1]
        ]
        vektory_utoku = vektory
        super().__init__("Král", barva, vektory_utoku, vektory)
        self.skok = False