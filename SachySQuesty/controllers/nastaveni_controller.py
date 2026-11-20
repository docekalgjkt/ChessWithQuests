# -*- coding: utf-8 -*-
"""NastaveniController – nastavení vzhledu a editor vlastních figurek (grafické upravení setu)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from custom_pieces.spravce_setu import SpravceSetu
from models.herni_plocha import HerniPlocha
from models.revizor_tahu import RevizorTahu
from utils.konfigurace import Konfigurace
from utils.konstanty import BILA, MOTIVY
from views.dialog_view import DialogView
from views.editor_setu_view import EditorSetuView
from views.nastaveni_vzhledu_view import NastaveniVzhleduView

if TYPE_CHECKING:
    from controllers.app_controller import AppController


class NastaveniController:
    def __init__(self, app: "AppController", konfigurace: Konfigurace, spravce_setu: SpravceSetu):
        self.app = app
        self.konfigurace = konfigurace
        self.spravce_setu = spravce_setu
        self.nastaveni_view = NastaveniVzhleduView(app.okno, self)
        self.editor_view = EditorSetuView(app.okno, self)
        app.okno.pridej_obrazovku("vzhled", self.nastaveni_view)
        app.okno.pridej_obrazovku("editor", self.editor_view)
        self._vybrana: Optional[str] = None       # název figurky v editoru

    def _zprava(self, titulek: str, text: str) -> None:
        DialogView(self.app.okno, titulek).zobraz_zpravu(titulek, text)

    def zpet(self) -> None:
        self.app.prepni_obrazovku("menu")

    # ------------------------------------------------------------ vzhled
    def obnov_vzhled(self) -> None:
        k = self.konfigurace
        self.nastaveni_view.zobraz_motivy(MOTIVY)
        self.nastaveni_view.nastav_hodnoty(k.motiv, k.velikost_pole, k.zobrazit_souradnice, k.zobrazit_mozne_tahy)
        self._nahled()

    def zmen_motiv(self, motiv: str) -> None:
        if motiv in MOTIVY:
            self.konfigurace.motiv = motiv
            self.konfigurace.uloz()
            self._nahled()

    def zmen_vzhled(self) -> None:
        data = self.nastaveni_view.vrat_nastaveni()
        k = self.konfigurace
        k.velikost_pole = min(96, max(32, data["velikost_pole"]))
        k.zobrazit_souradnice = data["zobrazit_souradnice"]
        k.zobrazit_mozne_tahy = data["zobrazit_mozne_tahy"]
        k.uloz()
        self._nahled()

    def _nahled(self) -> None:
        plocha = HerniPlocha((8, 8))
        plocha.standardni_rozestaveni()
        kun = plocha.vrat_obsah((7, 6))
        tahy = RevizorTahu(plocha).mozne_tahy(kun, (7, 6)) if kun else []
        self.nastaveni_view.zobraz_nahled(plocha.herni_deska, plocha.rozmery, self.konfigurace.vzhled(), tahy)

    # ------------------------------------------------------------ editor setu
    def obnov_editor(self) -> None:
        self.editor_view.zobraz_sety(self.spravce_setu.vrat_sety(), self.spravce_setu.nazev_setu)
        self.editor_view.zobraz_seznam(self.spravce_setu.vrat_nazvy(), self._vybrana)
        if self._vybrana and self.spravce_setu.vrat_definici(self._vybrana):
            self.editor_view.zobraz_figurku(self.spravce_setu.vytvor_figurku(self._vybrana, BILA))
        else:
            self._vybrana = None
            self.editor_view.zobraz_figurku(None)

    def nacti_set(self, nazev: str) -> None:
        nazev = nazev.strip()
        if not nazev:
            return
        novy = nazev not in self.spravce_setu.vrat_sety()
        self.spravce_setu.nacti_set(nazev)
        if novy:
            self.spravce_setu.uloz_set()
        self.konfigurace.aktivni_set = self.spravce_setu.nazev_setu
        self.konfigurace.uloz()
        self._vybrana = None
        self.obnov_editor()

    def vyber_figurku(self, nazev: str) -> None:
        if self.spravce_setu.vrat_definici(nazev) is None:
            return
        self._vybrana = nazev
        self.editor_view.zobraz_figurku(self.spravce_setu.vytvor_figurku(nazev, BILA))

    def nova_figurka(self) -> None:
        self._vybrana = None
        self.editor_view.zobraz_figurku(None)

    def uloz_figurku(self) -> None:
        data = self.editor_view.vrat_data()
        try:
            self.spravce_setu.uloz_figurku(data, self._vybrana)
        except ValueError as chyba:
            self._zprava("Uložit figurku", str(chyba))
            return
        self._vybrana = data["nazev"]
        self.obnov_editor()
        self._zprava("Figurka uložena", f"Figurka '{data['nazev']}' je v setu '{self.spravce_setu.nazev_setu}'. "
                                        "Najdeš ji v rozestavení figurek u nové partie.")

    def smaz_figurku(self) -> None:
        if not self._vybrana:
            return
        if not DialogView(self.app.okno, "Smazat figurku").potvrd(f"Smazat figurku '{self._vybrana}' ze setu?"):
            return
        self.spravce_setu.smaz_figurku(self._vybrana)
        self._vybrana = None
        self.obnov_editor()
