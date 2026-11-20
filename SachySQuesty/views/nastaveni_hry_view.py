# -*- coding: utf-8 -*-
"""NastaveniHryView – nastavení nové partie: režim (hotseat/LAN), hráči, plocha, čas, rozestavení."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk
from typing import TYPE_CHECKING, Any, List, Tuple

from utils.konstanty import BARVA_POZADI, BILA, CERNA, LAN_PORT, MAX_ROZMER, MIN_ROZMER, PISMO_FIGUREK
from views.herni_deska_view import HerniDeskaView
from views.obrazovka import Obrazovka

if TYPE_CHECKING:
    from views.hlavni_okno import HlavniOkno

REZIMY = [
    ("hotseat", "Hotseat – oba hráči u jednoho počítače"),
    ("lan_host", "LAN – založit hru (hraju za bílé)"),
    ("lan_klient", "LAN – připojit se ke hře (hraju za černé)"),
]


def _cislo(promenna: tk.Variable, vychozi: int) -> int:
    try:
        return int(promenna.get())
    except (tk.TclError, ValueError):
        return vychozi


class NastaveniHryView(Obrazovka):
    def __init__(self, okno: "HlavniOkno", controller: Any, vzhled: dict):
        super().__init__(okno, controller)
        self.vzhled = vzhled
        self.herni_rezim = tk.StringVar(value="hotseat")
        self.ip = tk.StringVar(value="127.0.0.1")
        self.port = tk.IntVar(value=LAN_PORT)
        self.radky = tk.IntVar(value=8)
        self.sloupce = tk.IntVar(value=8)
        self.rozmery_plochy: Tuple[int, int] = (8, 8)
        self.cas_na_hru = tk.IntVar(value=10)      # minuty
        self.cas_na_tah = tk.IntVar(value=0)       # sekundy
        self.barva_palety = tk.IntVar(value=BILA)
        self.figurka_palety = tk.StringVar(value="Pěšák")
        self.vykresli()
        self.navaz_udalosti()

    # ------------------------------------------------------------ vykreslení
    def vykresli(self) -> None:
        self.nadpis("Nová partie", "Zvol režim, hráče, velikost plochy, čas a rozestavení figurek")
        telo = tk.Frame(self, bg=BARVA_POZADI)
        telo.pack(fill="both", expand=True)
        levy = ttk.Frame(telo)
        levy.pack(side="left", fill="y", padx=(0, 20))
        pravy = ttk.LabelFrame(telo, text="Rozestavení figurek", padding=10)
        pravy.pack(side="left", fill="both", expand=True)

        # --- režim
        ram = ttk.LabelFrame(levy, text="Herní režim", padding=10)
        ram.pack(fill="x")
        for hodnota, text in REZIMY:
            ttk.Radiobutton(ram, text=text, value=hodnota, variable=self.herni_rezim).pack(anchor="w")
        radek = ttk.Frame(ram)
        radek.pack(fill="x", pady=(6, 0))
        ttk.Label(radek, text="IP hostitele:").pack(side="left")
        self.e_ip = ttk.Entry(radek, textvariable=self.ip, width=16)
        self.e_ip.pack(side="left", padx=(4, 10))
        ttk.Label(radek, text="Port:").pack(side="left")
        self.e_port = ttk.Entry(radek, textvariable=self.port, width=7)
        self.e_port.pack(side="left", padx=(4, 0))
        self.lbl_moje_ip = ttk.Label(ram, text="", style="Maly.TLabel")
        self.lbl_moje_ip.pack(anchor="w", pady=(4, 0))

        # --- hráči
        ram = ttk.LabelFrame(levy, text="Hráči", padding=10)
        ram.pack(fill="x", pady=(10, 0))
        self.lbl_bily = ttk.Label(ram, text="Bílý:")
        self.lbl_bily.grid(row=0, column=0, sticky="w")
        self.cb_bily = ttk.Combobox(ram, state="readonly", width=34)
        self.cb_bily.grid(row=0, column=1, pady=2, padx=(6, 0))
        self.lbl_cerny = ttk.Label(ram, text="Černý:")
        self.lbl_cerny.grid(row=1, column=0, sticky="w")
        self.cb_cerny = ttk.Combobox(ram, state="readonly", width=34)
        self.cb_cerny.grid(row=1, column=1, pady=2, padx=(6, 0))
        ttk.Label(ram, text="Host = hráč bez profilu (nezískává ELO ani XP).", style="Maly.TLabel").grid(
            row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

        # --- plocha a čas
        ram = ttk.LabelFrame(levy, text="Herní plocha a čas", padding=10)
        ram.pack(fill="x", pady=(10, 0))
        ttk.Label(ram, text="Řádky:").grid(row=0, column=0, sticky="w")
        self.sb_radky = ttk.Spinbox(ram, from_=MIN_ROZMER, to=MAX_ROZMER, textvariable=self.radky, width=5)
        self.sb_radky.grid(row=0, column=1, sticky="w", padx=4)
        ttk.Label(ram, text="Sloupce:").grid(row=0, column=2, sticky="w")
        self.sb_sloupce = ttk.Spinbox(ram, from_=MIN_ROZMER, to=MAX_ROZMER, textvariable=self.sloupce, width=5)
        self.sb_sloupce.grid(row=0, column=3, sticky="w", padx=4)
        self.b_rozmery = ttk.Button(ram, text="Použít")
        self.b_rozmery.grid(row=0, column=4, padx=(6, 0))
        ttk.Label(ram, text="Čas na hru (min, 0 = bez limitu):").grid(row=1, column=0, columnspan=3, sticky="w",
                                                                     pady=(8, 0))
        self.sb_cas_hra = ttk.Spinbox(ram, from_=0, to=180, textvariable=self.cas_na_hru, width=5)
        self.sb_cas_hra.grid(row=1, column=3, sticky="w", padx=4, pady=(8, 0))
        ttk.Label(ram, text="Čas na tah (s, 0 = bez limitu):").grid(row=2, column=0, columnspan=3, sticky="w")
        self.sb_cas_tah = ttk.Spinbox(ram, from_=0, to=600, increment=5, textvariable=self.cas_na_tah, width=5)
        self.sb_cas_tah.grid(row=2, column=3, sticky="w", padx=4)

        # --- akce
        akce = ttk.Frame(levy)
        akce.pack(fill="x", pady=(14, 0))
        self.b_zahajit = ttk.Button(akce, text="Zahájit partii ▶", style="Akcni.TButton")
        self.b_zahajit.pack(side="left")
        self.b_zpet = ttk.Button(akce, text="Zpět do menu")
        self.b_zpet.pack(side="left", padx=(8, 0))
        self.lbl_lan = ttk.Label(levy, text="", style="Info.TLabel", wraplength=380)
        self.lbl_lan.pack(anchor="w", pady=(10, 0))
        self.b_zrusit = ttk.Button(levy, text="Zrušit čekání")

        # --- rozestavení (paleta + deska)
        paleta = ttk.Frame(pravy)
        paleta.pack(fill="x")
        ttk.Label(paleta, text="Barva figurky:").pack(side="left")
        ttk.Radiobutton(paleta, text="bílá", value=BILA, variable=self.barva_palety).pack(side="left", padx=4)
        ttk.Radiobutton(paleta, text="černá", value=CERNA, variable=self.barva_palety).pack(side="left", padx=4)
        self.ram_figurek = tk.Frame(pravy, bg=BARVA_POZADI)
        self.ram_figurek.pack(fill="x", pady=(6, 6))
        self.deska_view = HerniDeskaView(pravy, 44, tuple(self.vzhled["barvy_poli"]), True)
        self.deska_view.pack(anchor="w")
        ttk.Label(pravy, text="Levé tlačítko = položit vybranou figurku • pravé tlačítko = odebrat figurku",
                  style="Maly.TLabel").pack(anchor="w", pady=(4, 0))
        tlacitka = ttk.Frame(pravy)
        tlacitka.pack(anchor="w", pady=(6, 0))
        self.b_standard = ttk.Button(tlacitka, text="Standardní rozestavení")
        self.b_standard.pack(side="left")
        self.b_prazdna = ttk.Button(tlacitka, text="Jen králové")
        self.b_prazdna.pack(side="left", padx=(8, 0))
        self._prepni_rezim()

    def navaz_udalosti(self) -> None:
        c = self.controller
        self.herni_rezim.trace_add("write", lambda *_: self._prepni_rezim())
        self.b_rozmery.configure(command=lambda: c.zmen_rozmery(_cislo(self.radky, 8), _cislo(self.sloupce, 8)))
        self.b_zahajit.configure(command=c.zahaj_partii)
        self.b_zpet.configure(command=lambda: c.prepni_obrazovku("menu"))
        self.b_zrusit.configure(command=c.zrus_cekani)
        self.b_standard.configure(command=c.standardni_rozestaveni)
        self.b_prazdna.configure(command=c.prazdna_deska)
        self.deska_view.bind("<Button-1>", lambda e: self._klik_na_desku(e, False))
        self.deska_view.bind("<Button-3>", lambda e: self._klik_na_desku(e, True))
        self.deska_view.bind("<Button-2>", lambda e: self._klik_na_desku(e, True))   # pravé tlačítko na macOS

    def _klik_na_desku(self, udalost: Any, odebrat: bool) -> None:
        pole = self.deska_view.na_souradnice(udalost.x, udalost.y)
        if pole is not None:
            self.controller.uprav_rozestaveni(pole, odebrat, self.figurka_palety.get(), self.barva_palety.get())

    def _prepni_rezim(self) -> None:
        """Povolí jen ta pole, která daný režim potřebuje."""
        rezim = self.herni_rezim.get()
        lan = rezim != "hotseat"
        self.e_ip.state(["!disabled"] if rezim == "lan_klient" else ["disabled"])
        self.e_port.state(["!disabled"] if lan else ["disabled"])
        self.lbl_bily.configure(text="Já:" if lan else "Bílý:")
        self.cb_cerny.configure(state="disabled" if lan else "readonly")
        stav = ["disabled"] if rezim == "lan_klient" else ["!disabled"]
        for prvek in (self.sb_radky, self.sb_sloupce, self.b_rozmery, self.sb_cas_hra, self.sb_cas_tah,
                      self.b_standard, self.b_prazdna):
            prvek.state(stav)

    # ------------------------------------------------------------ data pro controller
    def vrat_nastaveni(self) -> dict:
        return {
            "rezim": self.herni_rezim.get(),
            "ip": self.ip.get().strip(),
            "port": _cislo(self.port, LAN_PORT),
            "bily": max(0, self.cb_bily.current()),
            "cerny": max(0, self.cb_cerny.current()),
            "cas_na_hru": max(0, _cislo(self.cas_na_hru, 0)) * 60,
            "cas_na_tah": max(0, _cislo(self.cas_na_tah, 0)),
        }

    def nastav_hrace(self, jmena: List[str]) -> None:
        for cb in (self.cb_bily, self.cb_cerny):
            vybrany = cb.current()
            cb.configure(values=jmena)
            cb.current(vybrany if 0 <= vybrany < len(jmena) else 0)

    def nastav_paletu(self, figurky: List[Tuple[str, str]]) -> None:
        """figurky = [(název, symbol), ...] – standardní i vlastní."""
        for potomek in self.ram_figurek.winfo_children():
            potomek.destroy()
        nazvy = [n for n, _ in figurky]
        if self.figurka_palety.get() not in nazvy and nazvy:
            self.figurka_palety.set(nazvy[-1] if "Pěšák" not in nazvy else "Pěšák")
        for i, (nazev, symbol) in enumerate(figurky):
            tk.Radiobutton(self.ram_figurek, text=f"{symbol}\n{nazev}", value=nazev, variable=self.figurka_palety,
                           indicatoron=False, width=7, font=(PISMO_FIGUREK, 10), selectcolor="#ffe9a8",
                           bg="#ffffff").grid(row=i // 8, column=i % 8, padx=1, pady=1)

    def nastav_vzhled(self, vzhled: dict) -> None:
        self.vzhled = vzhled
        self.deska_view.nastav_vzhled(barvy_poli=tuple(vzhled["barvy_poli"]))

    def nastav_moje_ip(self, ip: str) -> None:
        self.lbl_moje_ip.configure(text=f"IP tohoto počítače: {ip}")

    def zobraz_rozestaveni(self, herni_deska: List[List[Any]], rozmery: Tuple[int, int]) -> None:
        self.rozmery_plochy = (int(rozmery[0]), int(rozmery[1]))
        self.radky.set(rozmery[0])
        self.sloupce.set(rozmery[1])
        self.deska_view.nastav_vzhled(velikost_pole=max(28, min(48, 470 // max(rozmery))))
        self.deska_view.vykresli_desku(rozmery)
        self.deska_view.vykresli_figurky(herni_deska)

    def zobraz_lan_stav(self, text: str, cekani: bool = False) -> None:
        self.lbl_lan.configure(text=text)
        if cekani:
            self.b_zrusit.pack(anchor="w", pady=(6, 0))
            self.b_zahajit.state(["disabled"])
        else:
            self.b_zrusit.pack_forget()
            self.b_zahajit.state(["!disabled"])
