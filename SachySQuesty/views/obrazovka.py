# -*- coding: utf-8 -*-
"""Obrazovka – abstraktní předek všech obrazovek aplikace."""
from __future__ import annotations

import tkinter as tk
from abc import ABCMeta, abstractmethod
from tkinter import ttk
from typing import TYPE_CHECKING, Any, Optional

from utils.konstanty import BARVA_POZADI

if TYPE_CHECKING:
    from views.hlavni_okno import HlavniOkno


class Obrazovka(tk.Frame, metaclass=ABCMeta):
    """Každá obrazovka se umí vykreslit a navázat své události na metody controlleru."""

    def __init__(self, okno: "HlavniOkno", controller: Any = None):
        super().__init__(okno.kontejner, bg=BARVA_POZADI, padx=22, pady=14)
        self.okno = okno
        self.controller = controller

    @abstractmethod
    def vykresli(self) -> None:
        """Vytvoří widgety obrazovky."""

    @abstractmethod
    def navaz_udalosti(self) -> None:
        """Propojí widgety (tlačítka, kliknutí...) s metodami controlleru."""

    def zobraz(self) -> None:
        self.pack(fill="both", expand=True)

    def skryj(self) -> None:
        self.pack_forget()

    # ------------------------------------------------------------ pomocné prvky
    def nadpis(self, text: str, podnadpis: Optional[str] = None) -> None:
        ram = tk.Frame(self, bg=BARVA_POZADI)
        ram.pack(fill="x", pady=(0, 12))
        ttk.Label(ram, text=text, style="Nadpis.TLabel").pack(anchor="w")
        if podnadpis:
            ttk.Label(ram, text=podnadpis, style="Podnadpis.TLabel").pack(anchor="w")
