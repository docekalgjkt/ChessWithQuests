# -*- coding: utf-8 -*-
"""ProfilView – profily hráčů, statistiky, historie partií a úkoly/achievementy."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional

from utils.konstanty import BARVA_POZADI
from views.obrazovka import Obrazovka

if TYPE_CHECKING:
    from views.hlavni_okno import HlavniOkno


def pocet_tahu(n: int) -> str:
    """1 tah, 2–4 tahy, 5 tahů (české skloňování)."""
    if n == 1:
        return "1 tah"
    if 2 <= n <= 4:
        return f"{n} tahy"
    return f"{n} tahů"


class ProfilView(Obrazovka):
    def __init__(self, okno: "HlavniOkno", controller: Any):
        super().__init__(okno, controller)
        self.uzivatelske_jmeno = tk.StringVar()
        self.jmeno = tk.StringVar()
        self.email = tk.StringVar()
        self._id_v_seznamu: List[int] = []
        self._popisy: Dict[str, str] = {}          # id řádku v tabulce -> popis úkolu
        self.vykresli()
        self.navaz_udalosti()

    def vykresli(self) -> None:
        self.nadpis("Profily hráčů", "ELO, XP, body, statistiky a splněné úkoly / achievementy")
        telo = tk.Frame(self, bg=BARVA_POZADI)
        telo.pack(fill="both", expand=True)

        # --- seznam hráčů + nový hráč
        levy = ttk.Frame(telo)
        levy.pack(side="left", fill="y")
        ram = ttk.LabelFrame(levy, text="Hráči", padding=8)
        ram.pack(fill="both", expand=True)
        self.lb_hraci = tk.Listbox(ram, width=30, height=14, exportselection=False, font=("Helvetica", 11),
                                   activestyle="none")
        self.lb_hraci.pack(fill="both", expand=True)
        self.b_smazat = ttk.Button(ram, text="Smazat vybraného hráče")
        self.b_smazat.pack(fill="x", pady=(6, 0))
        ram = ttk.LabelFrame(levy, text="Nový hráč", padding=8)
        ram.pack(fill="x", pady=(10, 0))
        for i, (popis, promenna) in enumerate((("Uživatelské jméno*", self.uzivatelske_jmeno),
                                               ("Jméno", self.jmeno), ("E-mail", self.email))):
            ttk.Label(ram, text=popis).grid(row=i, column=0, sticky="w")
            ttk.Entry(ram, textvariable=promenna, width=22).grid(row=i, column=1, pady=2, padx=(6, 0))
        self.b_vytvorit = ttk.Button(ram, text="Vytvořit profil")
        self.b_vytvorit.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        # --- detail profilu + historie
        stred = ttk.Frame(telo)
        stred.pack(side="left", fill="both", expand=True, padx=14)
        ram = ttk.LabelFrame(stred, text="Profil", padding=10)
        ram.pack(fill="x")
        self.lbl_detail = tk.Label(ram, text="Vyber hráče vlevo.", font=("Helvetica", 11), bg=BARVA_POZADI,
                                   justify="left", anchor="w")
        self.lbl_detail.pack(fill="x")
        ram = ttk.LabelFrame(stred, text="Historie partií", padding=8)
        ram.pack(fill="both", expand=True, pady=(10, 0))
        self.lb_historie = tk.Listbox(ram, font=("Courier", 10), activestyle="none")
        self.lb_historie.pack(fill="both", expand=True)

        # --- achievementy
        pravy = ttk.LabelFrame(telo, text="Úkoly / Achievementy", padding=8)
        pravy.pack(side="left", fill="both", expand=True)
        self.tv_achievementy = ttk.Treeview(pravy, columns=("stav", "nazev", "odmena"), show="headings", height=16)
        for sloupec, nadpis, sirka in (("stav", "", 30), ("nazev", "Úkol", 230), ("odmena", "Odměna", 110)):
            self.tv_achievementy.heading(sloupec, text=nadpis)
            self.tv_achievementy.column(sloupec, width=sirka, anchor="w")
        self.tv_achievementy.pack(fill="both", expand=True)
        self.lbl_popis = ttk.Label(pravy, text="", style="Maly.TLabel", wraplength=360)
        self.lbl_popis.pack(fill="x", pady=(6, 0))

        self.b_zpet = ttk.Button(self, text="Zpět do menu")
        self.b_zpet.pack(anchor="w", pady=(12, 0))

    def navaz_udalosti(self) -> None:
        c = self.controller
        self.lb_hraci.bind("<<ListboxSelect>>", self._vyber_hrace)
        self.tv_achievementy.bind("<<TreeviewSelect>>", self._vyber_achievement)
        self.b_vytvorit.configure(command=c.vytvor_uzivatele)
        self.b_smazat.configure(command=c.smaz_uzivatele)
        self.b_zpet.configure(command=c.zpet)

    def _vyber_hrace(self, _udalost: Any = None) -> None:
        id_uzivatele = self.vybrany_id()
        if id_uzivatele is not None:
            self.controller.zobraz_profil(id_uzivatele)

    def _vyber_achievement(self, _udalost: Any = None) -> None:
        vyber = self.tv_achievementy.selection()
        if vyber:
            self.lbl_popis.configure(text=self._popisy.get(vyber[0], ""))

    # ------------------------------------------------------------ zobrazení dat
    def vybrany_id(self) -> Optional[int]:
        vyber = self.lb_hraci.curselection()
        return self._id_v_seznamu[vyber[0]] if vyber else None

    def zobraz_seznam(self, uzivatele: Iterable[Any], vybrany_id: Optional[int] = None) -> None:
        self.lb_hraci.delete(0, "end")
        self._id_v_seznamu = []
        for u in uzivatele:
            self.lb_hraci.insert("end", f"{u.uzivatelske_jmeno}  (ELO {u.elo})")
            self._id_v_seznamu.append(u.id)
        if vybrany_id in self._id_v_seznamu:
            index = self._id_v_seznamu.index(vybrany_id)
            self.lb_hraci.selection_set(index)
            self.lb_hraci.see(index)

    def zobraz_profil(self, uzivatel: Any, historie: Optional[List[dict]] = None) -> None:
        self.lb_historie.delete(0, "end")
        if uzivatel is None:
            self.lbl_detail.configure(text="Vyber hráče vlevo nebo vytvoř nový profil.")
            return
        u = uzivatel
        self.lbl_detail.configure(text=(
            f"{u.zobrazovane_jmeno}  (@{u.uzivatelske_jmeno})\n"
            f"E-mail: {u.email or '–'}\n\n"
            f"ELO: {u.elo}      Úroveň: {u.uroven}      XP: {u.xp}      Body: {u.body}\n"
            f"Partie: {u.odehrane_partie}  (výhry {u.vyhry} / remízy {u.remizy} / prohry {u.prohry})\n"
            f"Úspěšnost: {u.uspesnost:.0f} %      Splněné úkoly: {len(u.splnene_kwesty)}"))
        for p in reversed(historie or []):
            self.lb_historie.insert("end", f"{p['datum']}  {p['bily']['jmeno']} – {p['cerny']['jmeno']}  "
                                           f"{p['vysledek']}  ({pocet_tahu(p['tahu'])}, {p['rezim']})")

    def zobraz_achievementy(self, questy: Iterable[Any], splnene_id: Iterable[str] = ()) -> None:
        splnene = set(splnene_id)
        self.tv_achievementy.delete(*self.tv_achievementy.get_children())
        self._popisy = {}
        for q in questy:
            stav = "✔" if q.id in splnene else "·"
            radek = self.tv_achievementy.insert("", "end", values=(stav, q.nazev, f"{q.odmena_xp} XP, {q.odmena_body} b."))
            self._popisy[radek] = q.popis
        self.lbl_popis.configure(text="Klikni na úkol pro zobrazení popisu.")

    def vrat_formular(self) -> dict:
        return {"uzivatelske_jmeno": self.uzivatelske_jmeno.get(), "jmeno": self.jmeno.get(),
                "email": self.email.get()}

    def vycisti_formular(self) -> None:
        for promenna in (self.uzivatelske_jmeno, self.jmeno, self.email):
            promenna.set("")
