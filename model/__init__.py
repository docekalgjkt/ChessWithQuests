from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any


# ==========================================
# 1. MODEL (Data a pravidla)
# ==========================================

class Uzivatel:
    def __init__(self, jmeno: str, elo: int = 1000):
        self.jmeno = jmeno
        self.elo = elo


class Hrac:
    def __init__(self, barva: str, uzivatel: Uzivatel):
        self.barva = barva
        self.uzivatel = uzivatel


class Figurka(ABC):
    def __init__(self, barva: str, symbol_bily: str, symbol_cerny: str):
        self.barva = barva
        self.symbol = symbol_bily if barva == "Bílá" else symbol_cerny

    def __str__(self):
        return self.symbol


class Kral(Figurka):
    def __init__(self, barva): super().__init__(barva, "♔", "♚")


class Dama(Figurka):
    def __init__(self, barva): super().__init__(barva, "♕", "♛")


class Vez(Figurka):
    def __init__(self, barva): super().__init__(barva, "♖", "♜")


class Strelec(Figurka):
    def __init__(self, barva): super().__init__(barva, "♗", "♝")


class Kun(Figurka):
    def __init__(self, barva): super().__init__(barva, "♘", "♞")


class Pesec(Figurka):
    def __init__(self, barva): super().__init__(barva, "♙", "♟")


class HernaPlocha:
    def __init__(self):
        self.rozmery = (8, 8)
        self.deska: List[List[Optional[Figurka]]] = [[None for _ in range(8)] for _ in range(8)]
        self.inicializuj_hru()

    def inicializuj_hru(self):
        # Rozestavení černých figurek (horní část)
        hlavni_rada = [Vez, Kun, Strelec, Dama, Kral, Strelec, Kun, Vez]
        for i, trida in enumerate(hlavni_rada):
            self.deska[0][i] = trida("Černá")
            self.deska[1][i] = Pesec("Černá")

        # Rozestavení bílých figurek (spodní část)
        for i, trida in enumerate(hlavni_rada):
            self.deska[6][i] = Pesec("Bílá")
            self.deska[7][i] = trida("Bílá")

    def vrat_obsah(self, r: int, c: int) -> Optional[Figurka]:
        return self.deska[r][c]

    def posun_figurku(self, odkud: Tuple[int, int], kam: Tuple[int, int]):
        r1, c1 = odkud
        r2, c2 = kam
        figurka = self.deska[r1][c1]
        self.deska[r2][c2] = figurka
        self.deska[r1][c1] = None