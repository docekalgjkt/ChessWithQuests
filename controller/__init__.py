from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any


# ==========================================
# 3. CONTROLLER (Řídící logika)
# ==========================================

class GameManager:
    def __init__(self, u1: Uzivatel, u2: Uzivatel):
        self.plocha = HernaPlocha()
        self.view = KonzoleView()
        self.hraci = [Hrac("Bílá", u1), Hrac("Černá", u2)]
        self.aktualni_index = 0
        self.bezi = True

    def start_game(self):
        self.view.zobraz_zpravu("ŠACHOVÁ PARTIE ZAČÍNÁ")
        while self.bezi:
            self.view.vykresli_plochu(self.plocha)
            aktualni_hrac = self.hraci[self.aktualni_index]

            odkud, kam = self.view.ziskej_tah(aktualni_hrac.uzivatel.jmeno, aktualni_hrac.barva)

            if odkud is None:
                self.view.zobraz_zpravu("Hra byla ukončena uživatelem.")
                break

            figurka = self.plocha.vrat_obsah(*odkud)
            if figurka is None:
                self.view.zobraz_zpravu("Chyba: Na zadané výchozí pozici není žádná figurka.")
                continue

            if figurka.barva != aktualni_hrac.barva:
                self.view.zobraz_zpravu("Chyba: Můžete táhnout pouze svými figurkami!")
                continue

            # Vykonání tahu
            cileva_fig = self.plocha.vrat_obsah(*kam)
            if cileva_fig and cileva_fig.barva == aktualni_hrac.barva:
                self.view.zobraz_zpravu("Chyba: Nemůžete vyhodit vlastní figurku!")
                continue

            self.plocha.posun_figurku(odkud, kam)
            if cileva_fig:
                self.view.zobraz_zpravu(f"Vyhozen {cileva_fig.barva} {cileva_fig.__class__.__name__}!")

            # Přepnutí hráče
            self.aktualni_index = 1 - self.aktualni_index