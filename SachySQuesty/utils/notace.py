# -*- coding: utf-8 -*-
"""Převod tahů do čitelné šachové notace (česká písmena figurek)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Tuple

from utils.konstanty import ZKRATKY

if TYPE_CHECKING:
    from models.tah import Tah


def nazev_pole(pozice: Tuple[int, int], rozmery: Tuple[int, int]) -> str:
    """(řádek, sloupec) -> např. 'e4'. Řádek 0 je nahoře, číslování řad je odspodu."""
    r, c = pozice
    return f"{chr(ord('a') + c)}{rozmery[0] - r}"


def notace_tahu(tah: "Tah", rozmery: Tuple[int, int]) -> str:
    """Dlouhá algebraická notace, např. 'Jg1-f3', 'e5xd6 e.p.', 'O-O', 'e7-e8=D+'."""
    if tah.typ_tahu == "rosada":
        dlouha = tah.vez_z is not None and tah.vez_z[1] < tah.vychozi_pozice[1]
        text = "O-O-O" if dlouha else "O-O"
    else:
        figurka = tah.figurka
        zkratka = ZKRATKY.get(figurka.nazev, figurka.zkratka)
        spojka = "x" if tah.vyhozena_figurka is not None else "-"
        text = f"{zkratka}{nazev_pole(tah.vychozi_pozice, rozmery)}{spojka}{nazev_pole(tah.cilova_pozice, rozmery)}"
        if tah.typ_tahu == "en_passant":
            text += " e.p."
        if tah.promena:
            nazev = tah.promena_na or "Dáma"
            text += "=" + ZKRATKY.get(nazev, nazev[:1])
    if tah.mat:
        text += "#"
    elif tah.sach:
        text += "+"
    return text
