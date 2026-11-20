# -*- coding: utf-8 -*-
"""Hrac – uživatel v roli bílého nebo černého v jedné partii."""
from __future__ import annotations

from users.uzivatel import Uzivatel
from utils.konstanty import NAZEV_BARVY


class Hrac:
    def __init__(self, barva: int, uzivatel: Uzivatel):
        self.barva = barva          # 1 = bílý, -1 = černý
        self.uzivatel = uzivatel

    def getEloRating(self) -> int:
        return self.uzivatel.elo

    @property
    def jmeno(self) -> str:
        return self.uzivatel.zobrazovane_jmeno

    @property
    def je_host(self) -> bool:
        return self.uzivatel.je_host

    @property
    def nazev_barvy(self) -> str:
        return NAZEV_BARVY[self.barva]

    def __repr__(self) -> str:
        return f"Hrac({self.nazev_barvy}, {self.jmeno})"
