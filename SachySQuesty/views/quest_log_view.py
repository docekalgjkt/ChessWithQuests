# -*- coding: utf-8 -*-
"""QuestLogView – úprava logu questů (přidat, upravit, smazat úkol)."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Dict, Iterable, List, Optional

from utils.konstanty import BARVA_POZADI
from views.obrazovka import Obrazovka

if TYPE_CHECKING:
    from views.hlavni_okno import HlavniOkno


class QuestLogView(Obrazovka):
    def __init__(self, okno: "HlavniOkno", controller: Any):
        super().__init__(okno, controller)
        self.nazev = tk.StringVar()
        self.popis = tk.StringVar()
        self.typ = tk.StringVar()
        self.parametr = tk.StringVar()
        self.odmena_xp = tk.StringVar(value="10")
        self.odmena_body = tk.StringVar(value="5")
        self.aktivni = tk.BooleanVar(value=True)
        self._typy: Dict[str, str] = {}
        self._id_v_seznamu: List[str] = []
        self.vykresli()
        self.navaz_udalosti()

    def vykresli(self) -> None:
        self.nadpis("Log questů", "Úkoly a achievementy, za které hráči dostávají XP a body")
        telo = tk.Frame(self, bg=BARVA_POZADI)
        telo.pack(fill="both", expand=True)
        ram = ttk.LabelFrame(telo, text="Questy", padding=8)
        ram.pack(side="left", fill="both", expand=True)
        self.seznam_questu = tk.Listbox(ram, width=46, font=("Helvetica", 11), exportselection=False,
                                        activestyle="none")
        posuvnik = ttk.Scrollbar(ram, orient="vertical", command=self.seznam_questu.yview)
        self.seznam_questu.configure(yscrollcommand=posuvnik.set)
        self.seznam_questu.pack(side="left", fill="both", expand=True)
        posuvnik.pack(side="right", fill="y")

        detail = ttk.LabelFrame(telo, text="Detail questu", padding=12)
        detail.pack(side="left", fill="both", padx=(14, 0))
        polozky = (("Název", ttk.Entry(detail, textvariable=self.nazev, width=40)),
                   ("Popis", ttk.Entry(detail, textvariable=self.popis, width=40)))
        for i, (text, prvek) in enumerate(polozky):
            ttk.Label(detail, text=text).grid(row=i, column=0, sticky="w", pady=3)
            prvek.grid(row=i, column=1, sticky="ew", pady=3)
        ttk.Label(detail, text="Typ").grid(row=2, column=0, sticky="w", pady=3)
        self.cb_typ = ttk.Combobox(detail, textvariable=self.typ, state="readonly", width=38)
        self.cb_typ.grid(row=2, column=1, sticky="ew", pady=3)
        self.lbl_typ = ttk.Label(detail, text="", style="Maly.TLabel", wraplength=330)
        self.lbl_typ.grid(row=3, column=1, sticky="w")
        ttk.Label(detail, text="Parametr (N / P)").grid(row=4, column=0, sticky="w", pady=3)
        ttk.Entry(detail, textvariable=self.parametr, width=14).grid(row=4, column=1, sticky="w", pady=3)
        ttk.Label(detail, text="Odměna XP").grid(row=5, column=0, sticky="w", pady=3)
        ttk.Spinbox(detail, from_=0, to=1000, increment=5, textvariable=self.odmena_xp, width=8).grid(
            row=5, column=1, sticky="w", pady=3)
        ttk.Label(detail, text="Odměna body").grid(row=6, column=0, sticky="w", pady=3)
        ttk.Spinbox(detail, from_=0, to=1000, increment=5, textvariable=self.odmena_body, width=8).grid(
            row=6, column=1, sticky="w", pady=3)
        ttk.Checkbutton(detail, text="Quest je aktivní", variable=self.aktivni).grid(row=7, column=1, sticky="w",
                                                                                    pady=3)
        tlacitka = ttk.Frame(detail)
        tlacitka.grid(row=8, column=0, columnspan=2, sticky="w", pady=(12, 0))
        self.b_novy = ttk.Button(tlacitka, text="Nový quest")
        self.b_novy.pack(side="left")
        self.b_ulozit = ttk.Button(tlacitka, text="Uložit", style="Akcni.TButton")
        self.b_ulozit.pack(side="left", padx=6)
        self.b_smazat = ttk.Button(tlacitka, text="Smazat")
        self.b_smazat.pack(side="left")
        self.b_zpet = ttk.Button(self, text="Zpět do menu")
        self.b_zpet.pack(anchor="w", pady=(12, 0))

    def navaz_udalosti(self) -> None:
        c = self.controller
        self.seznam_questu.bind("<<ListboxSelect>>", self._vyber)
        self.cb_typ.bind("<<ComboboxSelected>>", lambda _e: self._ukaz_popis_typu())
        self.b_novy.configure(command=c.novy_quest)
        self.b_ulozit.configure(command=c.uprav_quest)
        self.b_smazat.configure(command=c.smaz_quest)
        self.b_zpet.configure(command=c.zpet)

    def _vyber(self, _udalost: Any = None) -> None:
        id_questu = self.vrat_vybrany_quest()
        if id_questu is not None:
            self.controller.vyber_quest(id_questu)

    def _ukaz_popis_typu(self) -> None:
        self.lbl_typ.configure(text=self._typy.get(self.typ.get(), ""))

    # ------------------------------------------------------------ data
    def nastav_typy(self, typy: Dict[str, str]) -> None:
        self._typy = dict(typy)
        self.cb_typ.configure(values=list(typy))

    def zobraz_log(self, questy: Iterable[Any], vybrany_id: Optional[str] = None) -> None:
        self.seznam_questu.delete(0, "end")
        self._id_v_seznamu = []
        for q in questy:
            stav = "" if q.aktivni else "  (neaktivní)"
            self.seznam_questu.insert("end", f"{q.nazev} – {q.odmena_xp} XP{stav}")
            self._id_v_seznamu.append(q.id)
        if vybrany_id in self._id_v_seznamu:
            self.seznam_questu.selection_set(self._id_v_seznamu.index(vybrany_id))

    def zobraz_detail(self, quest: Any) -> None:
        if quest is None:
            for promenna in (self.nazev, self.popis, self.parametr):
                promenna.set("")
            self.typ.set(next(iter(self._typy), ""))
            self.odmena_xp.set("10")
            self.odmena_body.set("5")
            self.aktivni.set(True)
            self.seznam_questu.selection_clear(0, "end")
        else:
            self.nazev.set(quest.nazev)
            self.popis.set(quest.popis)
            self.typ.set(quest.typ)
            self.parametr.set(quest.parametr)
            self.odmena_xp.set(str(quest.odmena_xp))
            self.odmena_body.set(str(quest.odmena_body))
            self.aktivni.set(quest.aktivni)
        self._ukaz_popis_typu()

    def vrat_formular(self) -> dict:
        def cislo(promenna: tk.StringVar) -> int:
            try:
                return max(0, int(float(promenna.get())))
            except ValueError:
                return 0
        return {"nazev": self.nazev.get(), "popis": self.popis.get(), "typ": self.typ.get(),
                "parametr": self.parametr.get(), "odmena_xp": cislo(self.odmena_xp),
                "odmena_body": cislo(self.odmena_body), "aktivni": bool(self.aktivni.get())}

    def vrat_vybrany_quest(self) -> Optional[str]:
        """ID vybraného questu v seznamu."""
        vyber = self.seznam_questu.curselection()
        return self._id_v_seznamu[vyber[0]] if vyber else None
