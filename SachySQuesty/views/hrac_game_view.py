# -*- coding: utf-8 -*-
"""HracGameView – panel hráče vedle desky (jméno, ELO, čas, vyhozené figurky)."""
from __future__ import annotations

import tkinter as tk
from typing import Any, List, Optional

from utils.konstanty import BILA, PISMO_FIGUREK, SYMBOLY

BARVA_NORMAL = "#ffffff"
BARVA_AKTIVNI = "#fff4cc"


def formatuj_cas(sekundy: Optional[int]) -> str:
    if sekundy is None:
        return "∞"
    return f"{sekundy // 60:02d}:{sekundy % 60:02d}"


class HracGameView(tk.Frame):
    def __init__(self, master: Any, controller: Any):
        super().__init__(master, bg=BARVA_NORMAL, bd=1, relief="solid", padx=12, pady=8)
        self.controller = controller
        self.lbl_jmeno = tk.Label(self, text="", font=("Helvetica", 13, "bold"), anchor="w")
        self.lbl_info = tk.Label(self, text="", font=("Helvetica", 9), fg="#5f5a52", anchor="w")
        self.lbl_cas = tk.Label(self, text="∞", font=("Courier", 22, "bold"))
        self.lbl_cas_tahu = tk.Label(self, text="", font=("Helvetica", 9), fg="#5f5a52")
        self.lbl_vyhozene = tk.Label(self, text="", font=(PISMO_FIGUREK, 15), anchor="w")
        self.lbl_jmeno.grid(row=0, column=0, sticky="w")
        self.lbl_info.grid(row=1, column=0, sticky="w")
        self.lbl_vyhozene.grid(row=2, column=0, sticky="w")
        self.lbl_cas.grid(row=0, column=1, rowspan=2, sticky="e", padx=(10, 0))
        self.lbl_cas_tahu.grid(row=2, column=1, sticky="e")
        self.columnconfigure(0, weight=1)
        self._stitky = [self.lbl_jmeno, self.lbl_info, self.lbl_cas, self.lbl_cas_tahu, self.lbl_vyhozene]
        self.nastav_aktivni(False)

    def aktualizuj_hrace(self, hrac: Any) -> None:
        znak = "♔" if hrac.barva == BILA else "♚"
        self.lbl_jmeno.configure(text=f"{znak} {hrac.jmeno}")
        u = hrac.uzivatel
        info = f"{hrac.nazev_barvy} • ELO {hrac.getEloRating()}"
        if not u.je_host:
            info += f" • úroveň {u.uroven} • {u.xp} XP • {u.body} b."
        self.lbl_info.configure(text=info)

    def aktualizuj_cas(self, cas: Optional[int], cas_tahu: Optional[int] = None) -> None:
        self.lbl_cas.configure(text=formatuj_cas(cas), fg="#c0392b" if cas is not None and cas <= 30 else "#2d2a26")
        self.lbl_cas_tahu.configure(text=f"tah: {formatuj_cas(cas_tahu)}" if cas_tahu is not None else "")

    def zobraz_vyhozene(self, figurky: List[Any]) -> None:
        """Figurky soupeře, které tento hráč vyhodil."""
        znaky = []
        for f in figurky:
            if f.nazev in SYMBOLY:
                znaky.append(SYMBOLY[f.nazev][0 if f.barva == BILA else 1])
            else:
                znaky.append(f.symbol)
        self.lbl_vyhozene.configure(text=" ".join(znaky) if znaky else "–")

    def nastav_aktivni(self, aktivni: bool) -> None:
        barva = BARVA_AKTIVNI if aktivni else BARVA_NORMAL
        self.configure(bg=barva, bd=2 if aktivni else 1)
        for stitek in self._stitky:
            stitek.configure(bg=barva)
