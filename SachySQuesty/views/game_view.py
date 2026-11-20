# -*- coding: utf-8 -*-
"""GameView – obrazovka rozehrané partie (deska, panely hráčů, průběh, tlačítka)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, List, Optional, Tuple

from utils.konstanty import BARVA_POZADI
from views.herni_deska_view import HerniDeskaView
from views.hrac_game_view import HracGameView
from views.obrazovka import Obrazovka

if TYPE_CHECKING:
    from views.hlavni_okno import HlavniOkno

Pozice = Tuple[int, int]


class GameView(Obrazovka):
    def __init__(self, okno: "HlavniOkno", controller: Any, rozmery: Tuple[int, int], vzhled: dict,
                 otoceno: bool = False, lan: bool = False):
        super().__init__(okno, controller)
        self.rozmery = rozmery
        self.vzhled = vzhled
        self.otoceno = otoceno
        self.lan = lan
        self.deska_view: HerniDeskaView
        self.hraci_view: List[HracGameView] = []
        self.vykresli()
        self.navaz_udalosti()

    def vykresli(self) -> None:
        pravy = tk.Frame(self, bg=BARVA_POZADI, width=340)
        pravy.pack(side="right", fill="y", padx=(18, 0))
        levy = tk.Frame(self, bg=BARVA_POZADI)
        levy.pack(side="left", fill="both", expand=True)

        velikost = min(int(self.vzhled.get("velikost_pole", 64)), 740 // max(self.rozmery))
        self.deska_view = HerniDeskaView(levy, velikost, tuple(self.vzhled.get("barvy_poli", ("#f0d9b5", "#b58863"))),
                                         bool(self.vzhled.get("zobrazit_souradnice", True)))
        self.deska_view.otoceno = self.otoceno
        self.deska_view.vykresli_desku(self.rozmery)
        self.deska_view.pack(expand=True)

        bily, cerny = HracGameView(pravy, self.controller), HracGameView(pravy, self.controller)
        self.hraci_view = [bily, cerny]
        horni, dolni = (bily, cerny) if self.otoceno else (cerny, bily)
        horni.pack(fill="x")
        self.lbl_stav = tk.Label(pravy, text="", font=("Helvetica", 13, "bold"), bg=BARVA_POZADI, fg="#2d2a26",
                                 wraplength=320, justify="left", anchor="w")
        self.lbl_stav.pack(fill="x", pady=(10, 4))
        ttk.Label(pravy, text="Průběh partie", style="Maly.TLabel").pack(anchor="w")
        ram_historie = tk.Frame(pravy, bg=BARVA_POZADI)
        ram_historie.pack(fill="both", expand=True)
        self.lb_historie = tk.Listbox(ram_historie, height=10, font=("Courier", 11), activestyle="none",
                                      highlightthickness=0)
        posuvnik = ttk.Scrollbar(ram_historie, orient="vertical", command=self.lb_historie.yview)
        self.lb_historie.configure(yscrollcommand=posuvnik.set)
        self.lb_historie.pack(side="left", fill="both", expand=True)
        posuvnik.pack(side="right", fill="y")
        self.lbl_quest = tk.Label(pravy, text="", font=("Helvetica", 10, "italic"), fg="#8a6500", bg=BARVA_POZADI,
                                  wraplength=320, justify="left", anchor="w")
        self.lbl_quest.pack(fill="x", pady=(6, 0))
        dolni.pack(fill="x", pady=(8, 0))

        tlacitka = tk.Frame(pravy, bg=BARVA_POZADI)
        tlacitka.pack(fill="x", pady=(12, 0))
        self.b_vratit = ttk.Button(tlacitka, text="↶ Vrátit tah")
        self.b_remiza = ttk.Button(tlacitka, text="½ Nabídnout remízu")
        self.b_vzdat = ttk.Button(tlacitka, text="⚑ Vzdát")
        self.b_ulozit = ttk.Button(tlacitka, text="Uložit hru")
        self.b_menu = ttk.Button(tlacitka, text="Odejít do menu")
        for i, tlacitko in enumerate((self.b_vratit, self.b_remiza, self.b_vzdat, self.b_ulozit)):
            tlacitko.grid(row=i // 2, column=i % 2, sticky="ew", padx=2, pady=2)
        self.b_menu.grid(row=2, column=0, columnspan=2, sticky="ew", padx=2, pady=(8, 2))
        tlacitka.columnconfigure(0, weight=1)
        tlacitka.columnconfigure(1, weight=1)

    def navaz_udalosti(self) -> None:
        c = self.controller
        self.deska_view.bind("<Button-1>", c.klik_na_desku)
        self.deska_view.bind("<Button-3>", lambda _e: c.zrus_vyber())
        self.deska_view.bind("<Button-2>", lambda _e: c.zrus_vyber())     # pravé tlačítko na macOS
        self.b_vratit.configure(command=c.vratit_tah)
        self.b_remiza.configure(command=c.nabidnout_remizu)
        self.b_vzdat.configure(command=c.vzdat_partii)
        self.b_ulozit.configure(command=c.uloz_hru)
        self.b_menu.configure(command=c.odejit)

    # ------------------------------------------------------------ aktualizace (volá controller)
    def aktualizuj_desku(self, herni_deska: List[List[Any]], posledni_tah: Any = None,
                         pole_sach: Optional[Pozice] = None) -> None:
        deska = self.deska_view
        deska.zrus_zvyrazneni()
        deska.vykresli_figurky(herni_deska)
        if posledni_tah is not None:
            deska.zvyrazni_pole([posledni_tah.vychozi_pozice, posledni_tah.cilova_pozice], "posledni")
        if pole_sach is not None:
            deska.zvyrazni_pole([pole_sach], "sach")

    def zobraz_mozne_tahy(self, tahy: List[Any], vybrane_pole: Optional[Pozice] = None) -> None:
        self.reset_stavu()
        if vybrane_pole is not None:
            self.deska_view.zvyrazni_pole([vybrane_pole], "vyber")
        if self.vzhled.get("zobrazit_mozne_tahy", True):
            self.deska_view.zvyrazni_pole([t.cilova_pozice for t in tahy if t.vyhozena_figurka is None], "tah")
            self.deska_view.zvyrazni_pole([t.cilova_pozice for t in tahy if t.vyhozena_figurka is not None], "brani")

    def reset_stavu(self) -> None:
        for typ in ("vyber", "tah", "brani"):
            self.deska_view.zrus_zvyrazneni(typ)

    def zobraz_stav(self, text: str, dulezite: bool = False) -> None:
        self.lbl_stav.configure(text=text, fg="#c0392b" if dulezite else "#2d2a26")

    def zobraz_konec_hry(self, vysledek: str) -> None:
        self.lbl_stav.configure(text=f"Konec partie: {vysledek}", fg="#2f5d8a")
        self.reset_stavu()

    def zobraz_kwest_info(self, text: str) -> None:
        self.lbl_quest.configure(text=text)

    def aktualizuj_historii(self, notace: List[str]) -> None:
        self.lb_historie.delete(0, "end")
        for i in range(0, len(notace), 2):
            cerny = notace[i + 1] if i + 1 < len(notace) else ""
            self.lb_historie.insert("end", f"{i // 2 + 1:>3}. {notace[i]:<15}{cerny}")
        self.lb_historie.see("end")

    def nastav_tlacitka(self, vratit: bool, remiza: bool, vzdat: bool, ulozit: bool) -> None:
        for tlacitko, povoleno in ((self.b_vratit, vratit), (self.b_remiza, remiza), (self.b_vzdat, vzdat),
                                   (self.b_ulozit, ulozit)):
            tlacitko.state(["!disabled"] if povoleno else ["disabled"])
