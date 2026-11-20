# -*- coding: utf-8 -*-
"""HlavniMenuView – úvodní obrazovka s hlavním menu."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Dict

from utils.konstanty import BARVA_POZADI, PISMO_FIGUREK
from views.obrazovka import Obrazovka

if TYPE_CHECKING:
    from views.hlavni_okno import HlavniOkno

POLOZKY_MENU = [
    ("nova_hra", "Nová hra"),
    ("nacti", "Načíst uloženou hru"),
    ("profil", "Profily hráčů a achievementy"),
    ("questy", "Log questů (úkoly)"),
    ("vzhled", "Nastavení vzhledu"),
    ("editor", "Editor figurek (vlastní set)"),
    ("konec", "Konec"),
]


class HlavniMenuView(Obrazovka):
    def __init__(self, okno: "HlavniOkno", controller: Any):
        super().__init__(okno, controller)
        self.tlacitka: Dict[str, ttk.Button] = {}
        self.vykresli()
        self.navaz_udalosti()

    def vykresli(self) -> None:
        stred = tk.Frame(self, bg=BARVA_POZADI)
        stred.place(relx=0.5, rely=0.46, anchor="center")
        tk.Label(stred, text="♞", font=(PISMO_FIGUREK, 64), bg=BARVA_POZADI, fg="#2d2a26").pack()
        tk.Label(stred, text="ŠachySQuesty", font=("Helvetica", 34, "bold"), bg=BARVA_POZADI,
                 fg="#2d2a26").pack()
        ttk.Label(stred, text="Šachy s úkoly, achievementy a vlastními figurkami",
                  style="Podnadpis.TLabel").pack(pady=(2, 26))
        for klic, text in POLOZKY_MENU:
            tlacitko = ttk.Button(stred, text=text, style="Menu.TButton", width=30)
            tlacitko.pack(pady=4)
            self.tlacitka[klic] = tlacitko
        self.lbl_info = ttk.Label(stred, text="", style="Maly.TLabel")
        self.lbl_info.pack(pady=(18, 0))

    def navaz_udalosti(self) -> None:
        c = self.controller
        prepinace = {"nova_hra": "nastaveni_hry", "profil": "profil", "questy": "quest_log",
                     "vzhled": "vzhled", "editor": "editor"}
        for klic, obrazovka in prepinace.items():
            self.tlacitka[klic].configure(command=lambda o=obrazovka: c.prepni_obrazovku(o))
        self.tlacitka["nacti"].configure(command=c.nacti_hru)
        self.tlacitka["konec"].configure(command=c.ukonci)

    def zobraz_info(self, text: str) -> None:
        self.lbl_info.configure(text=text)
