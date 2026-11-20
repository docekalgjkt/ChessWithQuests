# -*- coding: utf-8 -*-
"""EditorSetuView – grafické upravení setu: tvorba vlastních figurek klikáním do mřížky."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, List, Optional, Set, Tuple

from utils.konstanty import BARVA_POZADI
from views.obrazovka import Obrazovka

if TYPE_CHECKING:
    from views.hlavni_okno import HlavniOkno

Vektor = Tuple[int, int]
MRIZKA = 9                 # 9×9 polí, figurka uprostřed
STRED = MRIZKA // 2
POLE = 44
BARVY = {"pohyb": "#2e8b57", "utok": "#c0392b", "skok": "#2f5d8a"}


class EditorSetuView(Obrazovka):
    def __init__(self, okno: "HlavniOkno", controller: Any):
        super().__init__(okno, controller)
        self.nazev = tk.StringVar()
        self.symbol = tk.StringVar()
        self.skok = tk.BooleanVar(value=False)
        self.max_kroku = tk.IntVar(value=1)
        self.rezim = tk.StringVar(value="pohyb")
        self.utok_jako_pohyb = tk.BooleanVar(value=True)
        self.nazev_setu = tk.StringVar()
        self._vektory: Set[Vektor] = set()
        self._utok: Set[Vektor] = set()
        self._skoky: Set[Vektor] = set()
        self._nazvy: List[str] = []
        self.vykresli()
        self.navaz_udalosti()

    def vykresli(self) -> None:
        self.nadpis("Editor figurek – grafické upravení setu",
                    "Klikáním do mřížky urči, kam se figurka může pohnout. Figurka stojí uprostřed, "
                    "bílý táhne nahoru (černému se pohyb otočí).")
        telo = tk.Frame(self, bg=BARVA_POZADI)
        telo.pack(fill="both", expand=True)

        # --- set a seznam figurek
        levy = ttk.LabelFrame(telo, text="Set figurek", padding=8)
        levy.pack(side="left", fill="y")
        radek = ttk.Frame(levy)
        radek.pack(fill="x")
        self.cb_set = ttk.Combobox(radek, textvariable=self.nazev_setu, width=16)
        self.cb_set.pack(side="left")
        self.b_set = ttk.Button(radek, text="Otevřít / založit")
        self.b_set.pack(side="left", padx=(4, 0))
        self.lb_figurky = tk.Listbox(levy, width=26, height=14, exportselection=False, font=("Helvetica", 11),
                                     activestyle="none")
        self.lb_figurky.pack(fill="both", expand=True, pady=(8, 0))
        self.b_nova = ttk.Button(levy, text="Nová figurka")
        self.b_nova.pack(fill="x", pady=(6, 0))
        self.b_smazat = ttk.Button(levy, text="Smazat figurku")
        self.b_smazat.pack(fill="x", pady=(4, 0))

        # --- vlastnosti figurky
        stred = ttk.LabelFrame(telo, text="Figurka", padding=10)
        stred.pack(side="left", fill="y", padx=14)
        ttk.Label(stred, text="Název:").grid(row=0, column=0, sticky="w")
        ttk.Entry(stred, textvariable=self.nazev, width=20).grid(row=0, column=1, sticky="w", pady=2)
        ttk.Label(stred, text="Symbol (1–2 znaky):").grid(row=1, column=0, sticky="w")
        ttk.Entry(stred, textvariable=self.symbol, width=5).grid(row=1, column=1, sticky="w", pady=2)
        ttk.Label(stred, text="Max. kroků (0 = neomezeně):").grid(row=2, column=0, sticky="w")
        ttk.Spinbox(stred, from_=0, to=12, textvariable=self.max_kroku, width=5).grid(row=2, column=1, sticky="w")
        ttk.Checkbutton(stred, text="Přeskakuje figurky", variable=self.skok).grid(row=3, column=0, columnspan=2,
                                                                                  sticky="w", pady=(4, 0))
        ttk.Separator(stred).grid(row=4, column=0, columnspan=2, sticky="ew", pady=8)
        ttk.Label(stred, text="Kliknutí do mřížky upravuje:").grid(row=5, column=0, columnspan=2, sticky="w")
        for i, (hodnota, text) in enumerate((("pohyb", "● pohyb na prázdné pole"),
                                             ("utok", "✕ braní (útok)"),
                                             ("skok", "◆ skok jako kůň (tah i braní)"))):
            ttk.Radiobutton(stred, text=text, value=hodnota, variable=self.rezim).grid(
                row=6 + i, column=0, columnspan=2, sticky="w")
        ttk.Checkbutton(stred, text="Braní stejné jako pohyb", variable=self.utok_jako_pohyb).grid(
            row=9, column=0, columnspan=2, sticky="w", pady=(4, 0))
        self.b_vycistit = ttk.Button(stred, text="Vymazat vektory")
        self.b_vycistit.grid(row=10, column=0, columnspan=2, sticky="ew", pady=(10, 0))
        self.b_ulozit = ttk.Button(stred, text="Uložit figurku", style="Akcni.TButton")
        self.b_ulozit.grid(row=11, column=0, columnspan=2, sticky="ew", pady=(6, 0))
        self.b_zpet = ttk.Button(stred, text="Zpět do menu")
        self.b_zpet.grid(row=12, column=0, columnspan=2, sticky="ew", pady=(16, 0))

        # --- mřížka (náhled pohybu)
        pravy = ttk.LabelFrame(telo, text="Pohyb figurky", padding=10)
        pravy.pack(side="left", fill="both", expand=True)
        self.nahled = tk.Canvas(pravy, width=MRIZKA * POLE + 1, height=MRIZKA * POLE + 1, bg="#ffffff",
                                highlightthickness=0)
        self.nahled.pack(anchor="nw")
        ttk.Label(pravy, text="● zelená = pohyb   ✕ červená = braní   ◆ modrá = skok   "
                              "slabé tečky = pokračování paprsku", style="Maly.TLabel").pack(anchor="w", pady=(6, 0))
        self._prekresli()

    def navaz_udalosti(self) -> None:
        c = self.controller
        self.nahled.bind("<Button-1>", self._klik_do_mrizky)
        for promenna in (self.skok, self.max_kroku, self.symbol):
            promenna.trace_add("write", lambda *_: self._prekresli())
        self.lb_figurky.bind("<<ListboxSelect>>", self._vyber)
        self.cb_set.bind("<<ComboboxSelected>>", lambda _e: c.nacti_set(self.nazev_setu.get()))
        self.b_set.configure(command=lambda: c.nacti_set(self.nazev_setu.get()))
        self.b_nova.configure(command=c.nova_figurka)
        self.b_smazat.configure(command=c.smaz_figurku)
        self.b_ulozit.configure(command=c.uloz_figurku)
        self.b_vycistit.configure(command=self._vymaz_vektory)
        self.b_zpet.configure(command=c.zpet)

    # ------------------------------------------------------------ interakce s mřížkou (neuložený formulář)
    def _vyber(self, _udalost: Any = None) -> None:
        vyber = self.lb_figurky.curselection()
        if vyber:
            self.controller.vyber_figurku(self._nazvy[vyber[0]])

    def _klik_do_mrizky(self, udalost: Any) -> None:
        sloupec, radek = udalost.x // POLE, udalost.y // POLE
        if not (0 <= radek < MRIZKA and 0 <= sloupec < MRIZKA):
            return
        vektor = (radek - STRED, sloupec - STRED)
        if vektor == (0, 0):
            return
        rezim = self.rezim.get()
        mnozina = {"pohyb": self._vektory, "utok": self._utok, "skok": self._skoky}[rezim]
        pridat = vektor not in mnozina
        for m in ([self._vektory, self._utok] if rezim == "pohyb" and self.utok_jako_pohyb.get() else [mnozina]):
            if pridat:
                m.add(vektor)
            else:
                m.discard(vektor)
        self._prekresli()

    def _vymaz_vektory(self) -> None:
        self._vektory.clear()
        self._utok.clear()
        self._skoky.clear()
        self._prekresli()

    def _max_kroku(self) -> int:
        try:
            return max(0, int(self.max_kroku.get()))
        except (tk.TclError, ValueError):
            return 1

    def _prekresli(self) -> None:
        n = self.nahled
        n.delete("all")
        for r in range(MRIZKA):
            for c in range(MRIZKA):
                barva = "#f0d9b5" if (r + c) % 2 == 0 else "#d9bf98"
                n.create_rectangle(c * POLE, r * POLE, (c + 1) * POLE, (r + 1) * POLE, fill=barva, outline="#c9b08a")
        max_kroku = self._max_kroku()
        # pokračování paprsků (u figurek, které jdou víc polí)
        for vektory, barva in ((self._vektory, BARVY["pohyb"]), (self._utok, BARVY["utok"])):
            for dr, dc in vektory:
                krok = 2
                while max_kroku == 0 or krok <= max_kroku:
                    r, c = STRED + dr * krok, STRED + dc * krok
                    if not (0 <= r < MRIZKA and 0 <= c < MRIZKA):
                        break
                    x, y = c * POLE + POLE / 2, r * POLE + POLE / 2
                    n.create_oval(x - 3, y - 3, x + 3, y + 3, fill=barva, outline="")
                    krok += 1
        for dr, dc in self._vektory:
            x, y = (STRED + dc) * POLE + POLE / 2, (STRED + dr) * POLE + POLE / 2
            n.create_oval(x - 9, y - 9, x + 9, y + 9, fill=BARVY["pohyb"], outline="")
        for dr, dc in self._utok:
            x, y = (STRED + dc) * POLE + POLE / 2, (STRED + dr) * POLE + POLE / 2
            n.create_line(x - 12, y - 12, x + 12, y + 12, fill=BARVY["utok"], width=4)
            n.create_line(x - 12, y + 12, x + 12, y - 12, fill=BARVY["utok"], width=4)
        for dr, dc in self._skoky:
            x, y = (STRED + dc) * POLE + POLE / 2, (STRED + dr) * POLE + POLE / 2
            n.create_polygon(x, y - 13, x + 13, y, x, y + 13, x - 13, y, fill=BARVY["skok"], outline="")
        x = y = STRED * POLE
        n.create_oval(x + 5, y + 5, x + POLE - 5, y + POLE - 5, fill="#ffffff", outline="#141414", width=2)
        n.create_text(x + POLE / 2, y + POLE / 2, text=(self.symbol.get() or "?")[:2],
                      font=("Helvetica", 15, "bold"), fill="#141414")
        n.create_text(x + POLE / 2, 8, text="▲ dopředu", font=("Helvetica", 8), fill="#6b655c")

    # ------------------------------------------------------------ data pro controller
    def zobraz_sety(self, sety: List[str], aktivni: str) -> None:
        self.cb_set.configure(values=sety)
        self.nazev_setu.set(aktivni)

    def zobraz_seznam(self, nazvy: List[str], vybrany: Optional[str] = None) -> None:
        self._nazvy = list(nazvy)
        self.lb_figurky.delete(0, "end")
        for nazev in self._nazvy:
            self.lb_figurky.insert("end", nazev)
        if vybrany in self._nazvy:
            self.lb_figurky.selection_set(self._nazvy.index(vybrany))

    def zobraz_figurku(self, figurka: Any) -> None:
        """Načte figurku (VlastniFigurka) do formuláře; None = prázdný formulář pro novou figurku."""
        if figurka is None:
            self.nazev.set("")
            self.symbol.set("")
            self.skok.set(False)
            self.max_kroku.set(1)
            self._vymaz_vektory()
            self.lb_figurky.selection_clear(0, "end")
            return
        self.nazev.set(figurka.nazev)
        self.symbol.set(figurka.symbol)
        self.skok.set(figurka.skok)
        self.max_kroku.set(figurka.max_kroku)
        self._vektory = {tuple(v) for v in figurka.vektory}
        self._utok = {tuple(v) for v in figurka.vektory_utoku}
        self._skoky = {tuple(v) for v in getattr(figurka, "vektory_skoku", [])}
        self.utok_jako_pohyb.set(self._vektory == self._utok)
        self._prekresli()

    def vrat_vektory(self) -> List[Vektor]:
        return sorted(self._vektory)

    def vrat_data(self) -> dict:
        return {"nazev": self.nazev.get().strip(), "symbol": self.symbol.get().strip()[:2],
                "skok": bool(self.skok.get()), "max_kroku": self._max_kroku(),
                "vektory": [list(v) for v in self.vrat_vektory()],
                "vektory_utoku": [list(v) for v in sorted(self._utok)],
                "vektory_skoku": [list(v) for v in sorted(self._skoky)]}
