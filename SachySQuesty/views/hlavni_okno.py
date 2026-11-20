# -*- coding: utf-8 -*-
"""HlavniOkno – hlavní okno aplikace, přepíná obrazovky."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import Dict, Optional

from utils.konstanty import BARVA_POZADI
from views.obrazovka import Obrazovka


class HlavniOkno(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("ŠachySQuesty")
        self.geometry("1280x840")
        self.minsize(1080, 720)
        self.configure(bg=BARVA_POZADI)
        self._nastav_styly()
        self.kontejner = tk.Frame(self, bg=BARVA_POZADI)
        self.kontejner.pack(fill="both", expand=True)
        self.obrazovky: Dict[str, Obrazovka] = {}
        self.aktualni_obrazovka: Optional[Obrazovka] = None

    def _nastav_styly(self) -> None:
        styl = ttk.Style(self)
        if "clam" in styl.theme_names():
            styl.theme_use("clam")
        for prvek in ("TFrame", "TLabel", "TRadiobutton", "TCheckbutton", "TLabelframe", "TLabelframe.Label"):
            styl.configure(prvek, background=BARVA_POZADI)
        styl.configure("TLabelframe.Label", font=("Helvetica", 11, "bold"))
        styl.configure("Nadpis.TLabel", font=("Helvetica", 22, "bold"), foreground="#2d2a26")
        styl.configure("Podnadpis.TLabel", font=("Helvetica", 11), foreground="#6b655c")
        styl.configure("Maly.TLabel", font=("Helvetica", 9), foreground="#6b655c")
        styl.configure("Info.TLabel", font=("Helvetica", 10, "bold"), foreground="#2f5d8a")
        styl.configure("TButton", padding=(10, 5))
        styl.configure("Menu.TButton", font=("Helvetica", 13), padding=(16, 9))
        styl.configure("Akcni.TButton", font=("Helvetica", 12, "bold"), padding=(14, 8))

    def pridej_obrazovku(self, nazev: str, obrazovka: Obrazovka) -> None:
        stara = self.obrazovky.get(nazev)
        if stara is not None and stara is not obrazovka:
            if stara is self.aktualni_obrazovka:
                self.aktualni_obrazovka = None
            stara.destroy()
        self.obrazovky[nazev] = obrazovka

    def zobraz_obrazovku(self, nazev: str) -> None:
        if self.aktualni_obrazovka is not None:
            self.aktualni_obrazovka.skryj()
        self.aktualni_obrazovka = self.obrazovky[nazev]
        self.aktualni_obrazovka.zobraz()

    def spust(self) -> None:
        self.mainloop()
