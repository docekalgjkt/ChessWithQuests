# -*- coding: utf-8 -*-
"""AppController – spouští aplikaci, vytváří modely a views, řídí menu, nastavení partie,
LAN připojení a ukládání/načítání her."""
from __future__ import annotations

import json
from pathlib import Path
from typing import List, Optional, Sequence

from controllers.game_manager_controller import GameManagerController
from controllers.nastaveni_controller import NastaveniController
from controllers.profil_controller import ProfilController
from custom_pieces.spravce_setu import SpravceSetu
from models.figurky import STANDARDNI, VlastniFigurka, Král, Pěšák, vytvor_figurku
from models.game_manager import GameManager
from models.herni_plocha import HerniPlocha
from models.hrac import Hrac
from models.quest import QuestManager
from models.timer import Timer
from users.user_manager import UserManager
from users.uzivatel import Uzivatel
from utils.export_writers import ChessNotationWriter, MetadataWriter
from utils.game_logger import GameLogger
from utils.konfigurace import Konfigurace
from utils.konstanty import (BILA, CERNA, MAX_ROZMER, MIN_ROZMER, SLOZKA_ULOZENE, STANDARDNI_FIGURKY, SYMBOLY,
                             zajisti_slozky)
from utils.lan import LanSpojeni
from views.dialog_view import DialogView
from views.hlavni_menu_view import HlavniMenuView
from views.hlavni_okno import HlavniOkno
from views.nastaveni_hry_view import NastaveniHryView


class AppController:
    def __init__(self) -> None:
        zajisti_slozky()
        # --- model
        self.konfigurace = Konfigurace()
        self.user_manager = UserManager()
        self.quest_manager = QuestManager()
        self.spravce_setu = SpravceSetu(nazev_setu=self.konfigurace.aktivni_set)
        self.rozestaveni = HerniPlocha((8, 8))
        self.rozestaveni.standardni_rozestaveni()
        self._seznam_hracu: List[Uzivatel] = []
        # --- view
        self.okno = HlavniOkno()
        self.okno.protocol("WM_DELETE_WINDOW", self.ukonci)
        self.menu_view = HlavniMenuView(self.okno, self)
        self.nastaveni_hry_view = NastaveniHryView(self.okno, self, self.konfigurace.vzhled())
        self.okno.pridej_obrazovku("menu", self.menu_view)
        self.okno.pridej_obrazovku("nastaveni_hry", self.nastaveni_hry_view)
        # --- dílčí controllery
        self.game_controller: Optional[GameManagerController] = None        # existuje jen během partie
        self.profil_controller = ProfilController(self, self.user_manager, self.quest_manager)
        self.nastaveni_controller = NastaveniController(self, self.konfigurace, self.spravce_setu)
        # --- LAN (jen během čekání na soupeře; pak spojení převezme GameManagerController)
        self.lan: Optional[LanSpojeni] = None
        self._lan_nastaveni: dict = {}
        self._lan_mistni: Optional[Uzivatel] = None
        self._id_lan: Optional[str] = None

    def spust_aplikaci(self) -> None:
        self.prepni_obrazovku("menu")
        self.okno.spust()

    def prepni_obrazovku(self, nazev: str) -> None:
        obnova = {
            "menu": self._obnov_menu,
            "nastaveni_hry": self.obnov_nastaveni_hry,
            "profil": self.profil_controller.obnov_profil,
            "quest_log": self.profil_controller.obnov_quest_log,
            "vzhled": self.nastaveni_controller.obnov_vzhled,
            "editor": self.nastaveni_controller.obnov_editor,
        }
        if nazev in obnova:
            obnova[nazev]()
        self.okno.zobraz_obrazovku(nazev)

    def _obnov_menu(self) -> None:
        pocet = len(self.user_manager.vrat_uzivatele())
        self.menu_view.zobraz_info(f"Profilů: {pocet} • questů: {len(self.quest_manager.questy)} • "
                                   f"vlastních figurek v setu '{self.spravce_setu.nazev_setu}': "
                                   f"{len(self.spravce_setu.definice)}")

    def _zprava(self, titulek: str, text: str) -> None:
        DialogView(self.okno, titulek).zobraz_zpravu(titulek, text)

    # ------------------------------------------------------------ nastavení partie
    def obnov_nastaveni_hry(self) -> None:
        view = self.nastaveni_hry_view
        self._seznam_hracu = self.user_manager.vrat_uzivatele()
        view.nastav_hrace(["Host (bez profilu)"] + [f"{u.zobrazovane_jmeno} (@{u.uzivatelske_jmeno}, ELO {u.elo})"
                                                    for u in self._seznam_hracu])
        paleta = [(n, SYMBOLY[n][1]) for n in STANDARDNI_FIGURKY]
        paleta += [(n, d["symbol"]) for n, d in sorted(self.spravce_setu.definice.items())]
        view.nastav_paletu(paleta)
        view.nastav_vzhled(self.konfigurace.vzhled())
        view.nastav_moje_ip(LanSpojeni.mistni_ip())
        self._zobraz_rozestaveni()

    def _zobraz_rozestaveni(self) -> None:
        self.nastaveni_hry_view.zobraz_rozestaveni(self.rozestaveni.herni_deska, self.rozestaveni.rozmery)

    def zmen_rozmery(self, radky: int, sloupce: int) -> None:
        if not (MIN_ROZMER <= radky <= MAX_ROZMER and MIN_ROZMER <= sloupce <= MAX_ROZMER):
            self._zprava("Rozměry plochy", f"Řádky i sloupce musí být v rozsahu {MIN_ROZMER}–{MAX_ROZMER}.")
            self._zobraz_rozestaveni()
            return
        self.rozestaveni = HerniPlocha((radky, sloupce))
        self.rozestaveni.standardni_rozestaveni()
        self._zobraz_rozestaveni()

    def standardni_rozestaveni(self) -> None:
        self.rozestaveni.standardni_rozestaveni()
        self._zobraz_rozestaveni()

    def prazdna_deska(self) -> None:
        """Prázdná deska, jen králové na výchozích polích."""
        self.rozestaveni.vycisti()
        radky, sloupce = self.rozestaveni.rozmery
        self.rozestaveni.nastav_obsah((0, sloupce // 2), Král(CERNA))
        self.rozestaveni.nastav_obsah((radky - 1, sloupce // 2), Král(BILA))
        self._zobraz_rozestaveni()

    def uprav_rozestaveni(self, souradnice, odebrat: bool, nazev: str, barva: int) -> None:
        """Vytvoření herní plochy – položení nebo odebrání figurky před začátkem partie."""
        if odebrat:
            self.rozestaveni.nastav_obsah(souradnice, None)
        else:
            if nazev in STANDARDNI:
                figurka = vytvor_figurku(nazev, barva)
            else:
                definice = self.spravce_setu.vrat_definici(nazev)
                if definice is None:
                    return
                figurka = VlastniFigurka(definice, barva)
            if isinstance(figurka, Král):          # každá strana má jen jednoho krále -> přesun
                stary = self.rozestaveni.najdi_krale(barva)
                if stary is not None:
                    self.rozestaveni.nastav_obsah(stary, None)
            if isinstance(figurka, Pěšák):         # dvojkrok jen z výchozí řady
                vychozi = self.rozestaveni.rozmery[0] - 2 if barva == BILA else 1
                figurka.pohnuto = souradnice[0] != vychozi
            self.rozestaveni.nastav_obsah(souradnice, figurka)
        self._zobraz_rozestaveni()

    def _uzivatel(self, index: int) -> Uzivatel:
        if 1 <= index <= len(self._seznam_hracu):
            return self._seznam_hracu[index - 1]
        return UserManager.vytvor_hosta("Host")

    def zahaj_partii(self, nastaveni: Optional[dict] = None) -> None:
        if self.lan is not None:
            return
        n = nastaveni or self.nastaveni_hry_view.vrat_nastaveni()
        rezim = n["rezim"]
        if rezim != "lan_klient":
            chyba = self.rozestaveni.over_rozestaveni()
            if chyba:
                self._zprava("Rozestavení figurek", chyba)
                return
        bily, cerny = self._uzivatel(n["bily"]), self._uzivatel(n["cerny"])
        if rezim == "hotseat":
            if not bily.je_host and bily is cerny:
                self._zprava("Hráči", "Jeden profil nemůže hrát sám proti sobě. Vyber jiného soupeře nebo Hosta.")
                return
            self._spust_partii(self.rozestaveni.kopie(), [Hrac(BILA, bily), Hrac(CERNA, cerny)],
                               n["cas_na_hru"], n["cas_na_tah"])
            return
        # --- LAN
        self._lan_nastaveni = n
        self._lan_mistni = bily
        self.lan = LanSpojeni(n["port"])
        if rezim == "lan_host":
            self.lan.hostuj()
            self.nastaveni_hry_view.zobraz_lan_stav(
                f"Čekám na soupeře… Řekni mu svou IP: {LanSpojeni.mistni_ip()} (port {n['port']}).", True)
        else:
            if not n["ip"]:
                self.lan = None
                self._zprava("LAN", "Zadej IP adresu počítače, který hru založil.")
                return
            self.lan.pripoj(n["ip"])
            self.nastaveni_hry_view.zobraz_lan_stav(f"Připojuji se k {n['ip']}:{n['port']}…", True)
        self._id_lan = self.okno.after(100, self._zpracuj_lan_cekani)

    def _spust_partii(self, plocha: HerniPlocha, hraci: List[Hrac], cas_na_hru: int, cas_na_tah: int,
                      lan: Optional[LanSpojeni] = None, mistni_barvy: Sequence[int] = (BILA, CERNA),
                      otoceno: bool = False, ulozena: Optional[dict] = None) -> None:
        casovac = Timer.ze_slovniku(ulozena["casovac"]) if ulozena else Timer(cas_na_hru, cas_na_tah)
        logger = GameLogger()
        logger.vytvor_soubor(f"{hraci[0].jmeno} vs {hraci[1].jmeno}")
        definice = {f.nazev: f.definice for _, f in plocha.figurky() if isinstance(f, VlastniFigurka)}
        if ulozena:
            definice.update(ulozena.get("definice_figurek", {}))
        game_manager = GameManager(plocha, hraci, casovac, logger, self.quest_manager, definice)
        if ulozena:
            game_manager.obnov_stav(ulozena)
        self.game_controller = GameManagerController(self, game_manager, lan, mistni_barvy, otoceno)

    def konec_partie(self) -> None:
        """Volá GameManagerController, když se z partie odchází do menu."""
        self.game_controller = None
        self.prepni_obrazovku("menu")

    # ------------------------------------------------------------ LAN – čekání na soupeře
    @staticmethod
    def _popis_hrace(uzivatel: Uzivatel) -> dict:
        return {"jmeno": uzivatel.zobrazovane_jmeno, "elo": uzivatel.elo}

    @staticmethod
    def _vzdaleny_uzivatel(data: dict) -> Uzivatel:
        uzivatel = UserManager.vytvor_hosta(str(data.get("jmeno", "Soupeř"))[:30] or "Soupeř",
                                            int(data.get("elo", 1200)))
        uzivatel.uzivatelske_jmeno = "lan"
        return uzivatel

    def _zpracuj_lan_cekani(self) -> None:
        self._id_lan = None
        if self.lan is None or self._lan_mistni is None:
            return
        n = self._lan_nastaveni
        for zprava in self.lan.vrat_zpravy():
            typ = zprava.get("typ")
            if typ in ("_chyba", "_odpojeno"):
                self.zrus_cekani()
                self._zprava("LAN", zprava.get("text", "Spojení se soupeřem bylo přerušeno."))
                return
            if typ == "_pripojeno":
                if self.lan.role == "klient":
                    self.lan.posli({"typ": "ahoj", "hrac": self._popis_hrace(self._lan_mistni)})
                    self.nastaveni_hry_view.zobraz_lan_stav("Připojeno – čekám, až hostitel spustí partii…", True)
                else:
                    self.nastaveni_hry_view.zobraz_lan_stav("Soupeř se připojuje…", True)
            elif typ == "ahoj" and self.lan.role == "host":
                souper = self._vzdaleny_uzivatel(zprava.get("hrac", {}))
                plocha = self.rozestaveni.kopie()
                self.lan.posli({"typ": "start", "plocha": plocha.do_slovniku(), "cas_na_hru": n["cas_na_hru"],
                                "cas_na_tah": n["cas_na_tah"], "hrac": self._popis_hrace(self._lan_mistni)})
                self._predej_lan_partii(plocha, [Hrac(BILA, self._lan_mistni), Hrac(CERNA, souper)],
                                        n["cas_na_hru"], n["cas_na_tah"], (BILA,), False)
                return
            elif typ == "start" and self.lan.role == "klient":
                try:
                    plocha = HerniPlocha.ze_slovniku(zprava["plocha"])
                except (KeyError, ValueError, TypeError):
                    self.zrus_cekani()
                    self._zprava("LAN", "Hostitel poslal neplatné nastavení hry.")
                    return
                souper = self._vzdaleny_uzivatel(zprava.get("hrac", {}))
                self._predej_lan_partii(plocha, [Hrac(BILA, souper), Hrac(CERNA, self._lan_mistni)],
                                        int(zprava.get("cas_na_hru", 0)), int(zprava.get("cas_na_tah", 0)),
                                        (CERNA,), True)
                return
        self._id_lan = self.okno.after(100, self._zpracuj_lan_cekani)

    def _predej_lan_partii(self, plocha: HerniPlocha, hraci: List[Hrac], cas_na_hru: int, cas_na_tah: int,
                           mistni_barvy: Sequence[int], otoceno: bool) -> None:
        lan = self.lan
        self.lan = None
        self.nastaveni_hry_view.zobraz_lan_stav("", False)
        self._spust_partii(plocha, hraci, cas_na_hru, cas_na_tah, lan, mistni_barvy, otoceno)

    def zrus_cekani(self) -> None:
        if self._id_lan is not None:
            self.okno.after_cancel(self._id_lan)
            self._id_lan = None
        if self.lan is not None:
            self.lan.zavri()
            self.lan = None
        self.nastaveni_hry_view.zobraz_lan_stav("", False)

    # ------------------------------------------------------------ uložení / načtení hry
    def uloz_hru(self) -> None:
        gc = self.game_controller
        if gc is None:
            self._zprava("Uložit hru", "Právě neprobíhá žádná partie.")
            return
        if gc.lan is not None:
            self._zprava("Uložit hru", "Partii po síti nelze uložit.")
            return
        cesta = DialogView.vyber_soubor(self.okno, True, SLOZKA_ULOZENE)
        if not cesta:
            return
        cesta_json = Path(cesta).with_suffix(".json")
        gm = gc.game_manager
        try:
            cesta_json.write_text(json.dumps(gm.do_slovniku(), ensure_ascii=False, indent=2), encoding="utf-8")
            pgn = ChessNotationWriter("PGN").zapis(gm, cesta_json)
            meta = MetadataWriter().zapis(gm, cesta_json)
        except OSError as chyba:
            self._zprava("Uložit hru", f"Hru se nepodařilo uložit: {chyba}")
            return
        self._zprava("Hra uložena", f"Uloženo do:\n{cesta_json.name}\n{pgn.name} (zápis tahů)\n{meta.name} (údaje)")

    def nacti_hru(self) -> None:
        cesta = DialogView.vyber_soubor(self.okno, False, SLOZKA_ULOZENE)
        if not cesta:
            return
        try:
            data = json.loads(Path(cesta).read_text(encoding="utf-8"))
            plocha = HerniPlocha.ze_slovniku(data["plocha"])
            hraci = []
            for h in data["hraci"]:
                uzivatel = None if h.get("host") else self.user_manager.najdi_uzivatele(int(h["id"]))
                if uzivatel is None:
                    uzivatel = UserManager.vytvor_hosta(h.get("jmeno", "Host"), int(h.get("elo", 1200)))
                hraci.append(Hrac(int(h["barva"]), uzivatel))
            self._spust_partii(plocha, hraci, 0, 0, ulozena=data)
        except (OSError, ValueError, KeyError, TypeError) as chyba:
            self._zprava("Načíst hru", f"Soubor se nepodařilo načíst: {chyba}")

    # ------------------------------------------------------------ konec aplikace
    def ukonci(self) -> None:
        gc = self.game_controller
        if gc is not None and not gc.game_manager.je_konec():
            if not DialogView(self.okno, "Konec").potvrd("Partie ještě běží. Opravdu ukončit aplikaci?"):
                return
            gc.ukonci()
        self.zrus_cekani()
        self.okno.destroy()
