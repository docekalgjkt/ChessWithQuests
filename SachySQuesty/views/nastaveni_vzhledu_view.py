# -*- coding: utf-8 -*-
"""NastaveniVzhleduView – motiv desky, velikost polí, souřadnice, nápověda tahů (s náhledem)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Dict, List, Tuple

from utils.konstanty import BARVA_POZADI
from views.herni_deska_view import HerniDeskaView
from views.obrazovka import Obrazovka

if TYPE_CHECKING:
    from views.hlavni_okno import HlavniOkno


class NastaveniVzhleduView(Obrazovka):
    def __init__(self, okno: "HlavniOkno", controller: Any):
        super().__init__(okno, controller)
        self.motiv = tk.StringVar()
        self.velikost_pole = tk.IntVar(value=64)
        self.zobrazit_souradnice = tk.BooleanVar(value=True)
        self.zobrazit_mozne_tahy = tk.BooleanVar(value=True)
        self._nastavuji = False
        self.vykresli()
        self.navaz_udalosti()

    def vykresli(self) -> None:
        self.nadpis("Nastavení vzhledu", "Změny se ukládají hned a projeví se v další partii")
        telo = tk.Frame(self, bg=BARVA_POZADI)
        telo.pack(fill="both", expand=True)
        levy = ttk.Frame(telo)
        levy.pack(side="left", fill="y", padx=(0, 20))
        self.ram_motivy = ttk.LabelFrame(levy, text="Motiv desky", padding=10)
        self.ram_motivy.pack(fill="x")
        ram = ttk.LabelFrame(levy, text="Další", padding=10)
        ram.pack(fill="x", pady=(10, 0))
        ttk.Label(ram, text="Velikost pole (px):").pack(anchor="w")
        self.sc_velikost = tk.Scale(ram, from_=32, to=96, orient="horizontal", resolution=4, length=240,
                                    variable=self.velikost_pole, bg=BARVA_POZADI, highlightthickness=0)
        self.sc_velikost.pack(anchor="w")
        self.cb_souradnice = ttk.Checkbutton(ram, text="Zobrazit souřadnice (a–h, 1–8)",
                                             variable=self.zobrazit_souradnice)
        self.cb_souradnice.pack(anchor="w", pady=(6, 0))
        self.cb_tahy = ttk.Checkbutton(ram, text="Ukazovat možné tahy vybrané figurky",
                                       variable=self.zobrazit_mozne_tahy)
        self.cb_tahy.pack(anchor="w")
        self.b_zpet = ttk.Button(levy, text="Zpět do menu")
        self.b_zpet.pack(anchor="w", pady=(14, 0))
        nahled = ttk.LabelFrame(telo, text="Náhled", padding=10)
        nahled.pack(side="left", fill="both", expand=True)
        self.deska_view = HerniDeskaView(nahled)
        self.deska_view.pack(anchor="nw")

    def navaz_udalosti(self) -> None:
        c = self.controller
        self.motiv.trace_add("write", lambda *_: None if self._nastavuji else c.zmen_motiv(self.motiv.get()))
        for promenna in (self.velikost_pole, self.zobrazit_souradnice, self.zobrazit_mozne_tahy):
            promenna.trace_add("write", lambda *_: None if self._nastavuji else c.zmen_vzhled())
        self.b_zpet.configure(command=c.zpet)

    def zobraz_motivy(self, motivy: Dict[str, Tuple[str, str]]) -> None:
        for potomek in self.ram_motivy.winfo_children():
            potomek.destroy()
        for i, (nazev, (svetla, tmava)) in enumerate(motivy.items()):
            vzorek = tk.Canvas(self.ram_motivy, width=36, height=18, highlightthickness=0, bg=BARVA_POZADI)
            for j, barva in enumerate((svetla, tmava, svetla, tmava)):
                vzorek.create_rectangle(j * 9, 0, j * 9 + 9, 18, fill=barva, outline=barva)
            vzorek.grid(row=i, column=0, pady=2, padx=(0, 6))
            ttk.Radiobutton(self.ram_motivy, text=nazev, value=nazev, variable=self.motiv).grid(
                row=i, column=1, sticky="w")

    def nastav_hodnoty(self, motiv: str, velikost_pole: int, zobrazit_souradnice: bool,
                       zobrazit_mozne_tahy: bool) -> None:
        self._nastavuji = True
        self.motiv.set(motiv)
        self.velikost_pole.set(velikost_pole)
        self.zobrazit_souradnice.set(zobrazit_souradnice)
        self.zobrazit_mozne_tahy.set(zobrazit_mozne_tahy)
        self._nastavuji = False

    def vrat_nastaveni(self) -> dict:
        try:
            velikost = int(self.velikost_pole.get())
        except (tk.TclError, ValueError):
            velikost = 64
        return {"motiv": self.motiv.get(), "velikost_pole": velikost,
                "zobrazit_souradnice": bool(self.zobrazit_souradnice.get()),
                "zobrazit_mozne_tahy": bool(self.zobrazit_mozne_tahy.get())}

    def zobraz_nahled(self, herni_deska: List[List[Any]], rozmery: Tuple[int, int], vzhled: dict,
                      ukazkove_tahy: List[Any]) -> None:
        self.deska_view.nastav_vzhled(min(vzhled["velikost_pole"], 64), tuple(vzhled["barvy_poli"]),
                                      vzhled["zobrazit_souradnice"])
        self.deska_view.vykresli_desku(rozmery)
        self.deska_view.vykresli_figurky(herni_deska)
        if ukazkove_tahy:
            self.deska_view.zvyrazni_pole([ukazkove_tahy[0].vychozi_pozice], "vyber")
            if vzhled["zobrazit_mozne_tahy"]:
                self.deska_view.zvyrazni_pole([t.cilova_pozice for t in ukazkove_tahy], "tah")
