# -*- coding: utf-8 -*-
"""ProfilController – profily hráčů, úkoly/achievementy a úprava logu questů."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from models.quest import TYPY_QUESTU, Quest, QuestManager
from users.user_manager import UserManager
from views.dialog_view import DialogView
from views.profil_view import ProfilView
from views.quest_log_view import QuestLogView

if TYPE_CHECKING:
    from controllers.app_controller import AppController


class ProfilController:
    def __init__(self, app: "AppController", user_manager: UserManager, quest_manager: QuestManager):
        self.app = app
        self.user_manager = user_manager
        self.quest_manager = quest_manager
        self.profil_view = ProfilView(app.okno, self)
        self.quest_log_view = QuestLogView(app.okno, self)
        self.quest_log_view.nastav_typy(TYPY_QUESTU)
        app.okno.pridej_obrazovku("profil", self.profil_view)
        app.okno.pridej_obrazovku("quest_log", self.quest_log_view)
        self.vybrany_uzivatel: Optional[int] = None
        self.vybrany_quest: Optional[str] = None

    def _zprava(self, titulek: str, text: str) -> None:
        DialogView(self.app.okno, titulek).zobraz_zpravu(titulek, text)

    def zpet(self) -> None:
        self.app.prepni_obrazovku("menu")

    # ------------------------------------------------------------ profily
    def obnov_profil(self) -> None:
        uzivatele = self.user_manager.vrat_uzivatele()
        if self.vybrany_uzivatel is None and uzivatele:
            self.vybrany_uzivatel = uzivatele[0].id
        self.profil_view.zobraz_seznam(uzivatele, self.vybrany_uzivatel)
        self.zobraz_profil(self.vybrany_uzivatel)

    def zobraz_profil(self, id_uzivatele: Optional[int]) -> None:
        uzivatel = self.user_manager.najdi_uzivatele(id_uzivatele) if id_uzivatele is not None else None
        self.vybrany_uzivatel = uzivatel.id if uzivatel else None
        historie = self.user_manager.vrat_historii(uzivatel.id) if uzivatel else []
        self.profil_view.zobraz_profil(uzivatel, historie)
        self.profil_view.zobraz_achievementy(self.quest_manager.questy, uzivatel.splnene_kwesty if uzivatel else [])

    def vytvor_uzivatele(self) -> None:
        data = self.profil_view.vrat_formular()
        try:
            uzivatel = self.user_manager.vytvor_uzivatele(data["uzivatelske_jmeno"], data["jmeno"], data["email"])
        except ValueError as chyba:
            self._zprava("Nový hráč", str(chyba))
            return
        self.profil_view.vycisti_formular()
        self.vybrany_uzivatel = uzivatel.id
        self.obnov_profil()

    def smaz_uzivatele(self) -> None:
        id_uzivatele = self.profil_view.vybrany_id()
        uzivatel = self.user_manager.najdi_uzivatele(id_uzivatele) if id_uzivatele is not None else None
        if uzivatel is None:
            return
        if not DialogView(self.app.okno, "Smazat hráče").potvrd(
                f"Opravdu smazat profil '{uzivatel.uzivatelske_jmeno}' včetně ELO a achievementů?"):
            return
        self.user_manager.smaz_uzivatele(uzivatel.id)
        self.vybrany_uzivatel = None
        self.obnov_profil()

    # ------------------------------------------------------------ log questů
    def obnov_quest_log(self) -> None:
        self.quest_log_view.zobraz_log(self.quest_manager.questy, self.vybrany_quest)
        self.quest_log_view.zobraz_detail(self.quest_manager.najdi_quest(self.vybrany_quest)
                                          if self.vybrany_quest else None)

    def vyber_quest(self, id_questu: str) -> None:
        self.vybrany_quest = id_questu
        self.quest_log_view.zobraz_detail(self.quest_manager.najdi_quest(id_questu))

    def novy_quest(self) -> None:
        self.vybrany_quest = None
        self.quest_log_view.zobraz_detail(None)

    def uprav_quest(self, quest: Optional[Quest] = None) -> None:
        """Uloží formulář: upraví vybraný quest, nebo vytvoří nový."""
        data = self.quest_log_view.vrat_formular()
        quest = quest or (self.quest_manager.najdi_quest(self.vybrany_quest) if self.vybrany_quest else None)
        try:
            if quest is None:
                quest = self.quest_manager.pridej_quest(**data)
            else:
                self.quest_manager.uprav_quest(quest, **data)
        except ValueError as chyba:
            self._zprava("Quest", str(chyba))
            return
        self.vybrany_quest = quest.id
        self.obnov_quest_log()

    def smaz_quest(self, quest: Optional[Quest] = None) -> None:
        quest = quest or (self.quest_manager.najdi_quest(self.vybrany_quest) if self.vybrany_quest else None)
        if quest is None:
            return
        if not DialogView(self.app.okno, "Smazat quest").potvrd(f"Opravdu smazat quest '{quest.nazev}'?"):
            return
        self.quest_manager.smaz_quest(quest)
        self.vybrany_quest = None
        self.obnov_quest_log()
