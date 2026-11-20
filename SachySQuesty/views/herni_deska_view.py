# -*- coding: utf-8 -*-
"""HerniDeskaView – kreslí šachovnici, figurky a zvýraznění (tk.Canvas)."""
from __future__ import annotations

import tkinter as tk
from typing import Any, Dict, Iterable, List, Optional, Tuple

from utils.konstanty import (BARVA_MOZNY_TAH, BARVA_POSLEDNI_TAH, BARVA_POZADI, BARVA_SACH, BARVA_VYBER, BILA,
                             PISMO_FIGUREK, SYMBOLY)

Pozice = Tuple[int, int]
BARVY_ZVYRAZNENI = {"vyber": BARVA_VYBER, "posledni": BARVA_POSLEDNI_TAH, "sach": BARVA_SACH}


class HerniDeskaView(tk.Canvas):
    def __init__(self, master: Any, velikost_pole: int = 64, barvy_poli: Tuple[str, str] = ("#f0d9b5", "#b58863"),
                 zobrazit_souradnice: bool = True):
        super().__init__(master, highlightthickness=0, bd=0, bg=BARVA_POZADI)
        self.velikost_pole = velikost_pole
        self.barvy_poli = barvy_poli
        self.zobrazit_souradnice = zobrazit_souradnice
        self.symboly_figurek: Dict[str, Tuple[str, str]] = dict(SYMBOLY)
        self.rozmery: Tuple[int, int] = (8, 8)
        self.otoceno = False          # True = černý dole (LAN hráč za černé)

    # ------------------------------------------------------------ geometrie
    @property
    def _levy(self) -> int:
        return 22 if self.zobrazit_souradnice else 2

    @property
    def _spodni(self) -> int:
        return 20 if self.zobrazit_souradnice else 2

    def _xy(self, pozice: Pozice) -> Tuple[int, int]:
        """Levý horní roh pole v pixelech."""
        r, c = pozice
        if self.otoceno:
            r, c = self.rozmery[0] - 1 - r, self.rozmery[1] - 1 - c
        return self._levy + c * self.velikost_pole, 2 + r * self.velikost_pole

    def na_souradnice(self, x: int, y: int) -> Optional[Pozice]:
        """Převod kliknutí (pixely) na pole desky (řádek, sloupec)."""
        v = self.velikost_pole
        c = (x - self._levy) // v
        r = (y - 2) // v
        radky, sloupce = self.rozmery
        if not (0 <= r < radky and 0 <= c < sloupce) or x < self._levy or y < 2:
            return None
        if self.otoceno:
            r, c = radky - 1 - r, sloupce - 1 - c
        return int(r), int(c)

    def nastav_vzhled(self, velikost_pole: Optional[int] = None, barvy_poli: Optional[Tuple[str, str]] = None,
                      zobrazit_souradnice: Optional[bool] = None) -> None:
        if velikost_pole is not None:
            self.velikost_pole = int(velikost_pole)
        if barvy_poli is not None:
            self.barvy_poli = (barvy_poli[0], barvy_poli[1])
        if zobrazit_souradnice is not None:
            self.zobrazit_souradnice = bool(zobrazit_souradnice)

    # ------------------------------------------------------------ kreslení
    def vykresli_desku(self, rozmery: Tuple[int, int]) -> None:
        self.rozmery = (int(rozmery[0]), int(rozmery[1]))
        radky, sloupce = self.rozmery
        v = self.velikost_pole
        self.delete("all")
        self.configure(width=self._levy + sloupce * v + 2, height=2 + radky * v + self._spodni)
        for r in range(radky):
            for c in range(sloupce):
                x, y = self._xy((r, c))
                barva = self.barvy_poli[(r + c) % 2]
                self.create_rectangle(x, y, x + v, y + v, fill=barva, outline=barva, tags=("pole",))
        if self.zobrazit_souradnice:
            pismo = ("Helvetica", 9)
            for c in range(sloupce):
                x, _ = self._xy((0, c))
                self.create_text(x + v / 2, 2 + radky * v + 10, text=chr(ord("a") + c), font=pismo,
                                 fill="#6b655c", tags=("souradnice",))
            for r in range(radky):
                _, y = self._xy((r, 0))
                self.create_text(11, y + v / 2, text=str(radky - r), font=pismo, fill="#6b655c",
                                 tags=("souradnice",))

    def vykresli_figurky(self, herni_deska: List[List[Any]]) -> None:
        self.delete("figurka")
        for r, radek in enumerate(herni_deska):
            for c, figurka in enumerate(radek):
                if figurka is not None:
                    self._nakresli_figurku(figurka, (r, c))
        self.tag_raise("tecka")

    def _nakresli_figurku(self, figurka: Any, pozice: Pozice) -> None:
        v = self.velikost_pole
        x, y = self._xy(pozice)
        sx, sy = x + v / 2, y + v / 2 + 1
        if figurka.nazev in self.symboly_figurek:
            obrys, plny = self.symboly_figurek[figurka.nazev]
            pismo = (PISMO_FIGUREK, -int(v * 0.78))
            if figurka.barva == BILA:
                self.create_text(sx, sy, text=plny, fill="#ffffff", font=pismo, tags=("figurka",))
                self.create_text(sx, sy, text=obrys, fill="#1b1b1b", font=pismo, tags=("figurka",))
            else:
                self.create_text(sx, sy, text=plny, fill="#141414", font=pismo, tags=("figurka",))
        else:  # vlastní figurka = kolečko se symbolem
            okraj = v * 0.14
            bila = figurka.barva == BILA
            self.create_oval(x + okraj, y + okraj, x + v - okraj, y + v - okraj, width=2, outline="#141414",
                             fill="#fbfbfb" if bila else "#262626", tags=("figurka",))
            self.create_text(sx, sy - 1, text=figurka.symbol, fill="#141414" if bila else "#fbfbfb",
                             font=("Helvetica", -int(v * 0.4), "bold"), tags=("figurka",))

    def zvyrazni_pole(self, pole: Iterable[Pozice], typ: str = "vyber") -> None:
        """typ: 'vyber' | 'posledni' | 'sach' (podbarvení), 'tah' (tečka), 'brani' (kroužek)."""
        v = self.velikost_pole
        for pozice in pole:
            x, y = self._xy(pozice)
            tagy = ("zvyrazneni", f"zv_{typ}")
            if typ in BARVY_ZVYRAZNENI:
                barva = BARVY_ZVYRAZNENI[typ]
                self.create_rectangle(x, y, x + v, y + v, fill=barva, outline=barva, tags=tagy)
            elif typ == "tah":
                p = v * 0.17
                self.create_oval(x + v / 2 - p, y + v / 2 - p, x + v / 2 + p, y + v / 2 + p,
                                 fill=BARVA_MOZNY_TAH, outline="", tags=tagy + ("tecka",))
            elif typ == "brani":
                self.create_oval(x + 3, y + 3, x + v - 3, y + v - 3, outline=BARVA_MOZNY_TAH, width=4,
                                 tags=tagy + ("tecka",))
        self.tag_raise("figurka")
        self.tag_raise("tecka")

    def zrus_zvyrazneni(self, typ: Optional[str] = None) -> None:
        self.delete("zvyrazneni" if typ is None else f"zv_{typ}")
