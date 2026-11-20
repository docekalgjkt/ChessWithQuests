# -*- coding: utf-8 -*-
"""DialogView – modální okna (zpráva, potvrzení, proměna pěšáka, odměna za quest)."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk
from typing import Any, List, Optional, Sequence, Tuple

from utils.konstanty import BARVA_POZADI, BILA, PISMO_FIGUREK, SYMBOLY


class DialogView(tk.Toplevel):
    """Jedno modální okno. Použití: DialogView(okno, "Titulek").potvrd("Otázka?")."""

    def __init__(self, master: Any, titulek: str = "ŠachySQuesty"):
        super().__init__(master)
        self.withdraw()
        self.title(titulek)
        self.transient(master)
        self.resizable(False, False)
        self.configure(bg=BARVA_POZADI)
        self._vysledek: Any = None
        self.obsah = tk.Frame(self, bg=BARVA_POZADI, padx=24, pady=18)
        self.obsah.pack(fill="both", expand=True)
        self.protocol("WM_DELETE_WINDOW", lambda: self._zavri(None))
        self.bind("<Escape>", lambda _e: self._zavri(None))

    # ------------------------------------------------------------ pomocné
    def _ukaz(self) -> Any:
        self.update_idletasks()
        rodic = self.master
        x = rodic.winfo_rootx() + (rodic.winfo_width() - self.winfo_reqwidth()) // 2
        y = rodic.winfo_rooty() + (rodic.winfo_height() - self.winfo_reqheight()) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")
        self.deiconify()
        try:
            self.wait_visibility()      # grab_set jde až na zobrazené okno (jinak chyba na Linuxu)
            self.grab_set()
        except tk.TclError:
            pass
        self.focus_set()
        self.wait_window()
        return self._vysledek

    def _zavri(self, vysledek: Any) -> None:
        self._vysledek = vysledek
        try:
            self.grab_release()
        except tk.TclError:
            pass
        self.destroy()

    def _text(self, nadpis: Optional[str], text: str) -> None:
        if nadpis:
            tk.Label(self.obsah, text=nadpis, font=("Helvetica", 14, "bold"), bg=BARVA_POZADI,
                     anchor="w").pack(fill="x", pady=(0, 6))
        tk.Label(self.obsah, text=text, font=("Helvetica", 11), bg=BARVA_POZADI, justify="left",
                 wraplength=440, anchor="w").pack(fill="x")

    def _tlacitka(self, polozky: Sequence[Tuple[str, Any]]) -> None:
        ram = tk.Frame(self.obsah, bg=BARVA_POZADI)
        ram.pack(fill="x", pady=(16, 0))
        for i, (text, vysledek) in enumerate(polozky):
            tlacitko = ttk.Button(ram, text=text, command=lambda v=vysledek: self._zavri(v))
            tlacitko.pack(side="right", padx=(8, 0))
            if i == 0:
                tlacitko.focus_set()
                self.bind("<Return>", lambda _e, v=vysledek: self._zavri(v))

    # ------------------------------------------------------------ typy dialogů
    def zobraz_zpravu(self, titulek: str, text: str) -> None:
        self.title(titulek)
        self._text(titulek, text)
        self._tlacitka([("OK", True)])
        self._ukaz()

    def potvrd(self, otazka: str, ano: str = "Ano", ne: str = "Ne") -> bool:
        self._text(None, otazka)
        self._tlacitka([(ano, True), (ne, False)])
        return bool(self._ukaz())

    def vyber_figurku(self, moznosti: List[Any]) -> Any:
        """Výběr figurky pro proměnu pěšáka. Vrací vybranou figurku (zavření = první možnost)."""
        self.title("Proměna pěšáka")
        self._text("Proměna pěšáka", "Na jakou figurku se má pěšák proměnit?")
        ram = tk.Frame(self.obsah, bg=BARVA_POZADI)
        ram.pack(pady=(12, 0))
        for figurka in moznosti:
            if figurka.nazev in SYMBOLY:
                znak = SYMBOLY[figurka.nazev][0 if figurka.barva == BILA else 1]
            else:
                znak = figurka.symbol
            tk.Button(ram, text=f"{znak}\n{figurka.nazev}", font=(PISMO_FIGUREK, 14), width=7,
                      command=lambda f=figurka: self._zavri(f)).pack(side="left", padx=4)
        vysledek = self._ukaz()
        return vysledek if vysledek is not None else moznosti[0]

    def zobraz_odmenu(self, questy: List[Any], jmeno_hrace: str = "", odmeny: Optional[dict] = None) -> None:
        self.title("Quest splněn!")
        radky = [f"★ {q.nazev} – {q.popis}  (+{q.odmena_xp} XP, +{q.odmena_body} b.)" for q in questy]
        if odmeny:
            radky.append(f"\nCelkem: +{odmeny.get('xp', 0)} XP, +{odmeny.get('body', 0)} bodů")
        self._text(f"{jmeno_hrace} splnil(a) úkol!" if jmeno_hrace else "Úkol splněn!", "\n".join(radky))
        self._tlacitka([("Super!", True)])
        self._ukaz()

    @staticmethod
    def vyber_soubor(master: Any, ulozit: bool, slozka: Path) -> str:
        typy = [("Uložená hra ŠachySQuesty", "*.json"), ("Všechny soubory", "*.*")]
        if ulozit:
            return filedialog.asksaveasfilename(parent=master, initialdir=str(slozka), defaultextension=".json",
                                                filetypes=typy, title="Uložit hru") or ""
        return filedialog.askopenfilename(parent=master, initialdir=str(slozka), filetypes=typy,
                                          title="Načíst hru") or ""
