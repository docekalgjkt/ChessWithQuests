# -*- coding: utf-8 -*-
"""GameManager – řídí průběh jedné partie (kdo je na tahu, provedení tahu, stav hry).

Odpovídá sekvenčnímu diagramu "výběr tahu":
  je_vlastni_figurka -> vrat_mozne_tahy (nastav_aktivni_figurku, RevizorTahu.mozne_tahy)
  -> proved_tah (RevizorTahu.kontrola_tahu, HerniPlocha.proved_tah, QuestManager.vyhodnot_kwesty)
"""
from __future__ import annotations

import copy
from typing import Dict, List, Optional, Tuple

from models.figurky import Figurka, STANDARDNI, vytvor_figurku
from models.herni_plocha import HerniPlocha
from models.hrac import Hrac
from models.quest import Odmeny, Quest, QuestManager
from models.revizor_tahu import RevizorTahu
from models.tah import Tah
from models.timer import Timer
from users.uzivatel import Uzivatel
from utils.game_logger import GameLogger
from utils.konstanty import BILA, NAZEV_BARVY
from utils.notace import notace_tahu

Pozice = Tuple[int, int]


class GameManager:
    # stavy hry (get_stav)
    PROBIHA, SACH, MAT, PAT, CAS, VZDANO, REMIZA, ODPOJENO = range(8)
    KONCOVE_STAVY = (MAT, PAT, CAS, VZDANO, REMIZA, ODPOJENO)

    def __init__(self, herni_plocha: HerniPlocha, hraci: List[Hrac], casovac: Timer,
                 game_logger: Optional[GameLogger] = None, quest_manager: Optional[QuestManager] = None,
                 definice_figurek: Optional[Dict[str, dict]] = None):
        if len(hraci) != 2 or hraci[0].barva != BILA:
            raise ValueError("Hráči musí být dva a první z nich bílý.")
        self.herni_plocha = herni_plocha
        self.aktivni_hrac = 0                         # index do self.hraci (0 = bílý)
        self.hraci = hraci
        self.aktualni_tah: Optional[Tah] = None       # naposledy provedený tah
        self.casovac = casovac
        self.game_logger = game_logger or GameLogger()
        self.revizor_tahu = RevizorTahu(herni_plocha)
        self.quest_manager = quest_manager
        self.definice_figurek: Dict[str, dict] = dict(definice_figurek or {})  # vlastní figurky ve hře

        self.aktivni_figurka: Optional[Pozice] = None
        self.mozne_tahy_figurky: List[Tah] = []
        self.notace_historie: List[str] = []
        self.statistiky: Dict[int, Dict[str, int]] = {b: {"tahu": 0, "vyhozeno": 0, "sachu": 0} for b in (1, -1)}
        self.posledni_kwesty: List[Tuple[Hrac, List[Quest], Odmeny]] = []
        self.stav = self.PROBIHA
        self.vitez: Optional[int] = None             # barva vítěze, None = remíza / nerozhodnuto
        self._snimky: List[dict] = []                 # pro vrácení tahu
        self._aktualizuj_stav()

    # ------------------------------------------------------------ pomocné vlastnosti
    @property
    def aktivni(self) -> Hrac:
        return self.hraci[self.aktivni_hrac]

    @property
    def barva_na_tahu(self) -> int:
        return self.aktivni.barva

    def hrac_barvy(self, barva: int) -> Hrac:
        return self.hraci[0] if barva == BILA else self.hraci[1]

    def je_konec(self) -> bool:
        return self.stav in self.KONCOVE_STAVY

    def get_stav(self) -> int:
        return self.stav

    def najdi_uzivatele(self, id_uzivatele: int) -> Optional[Uzivatel]:
        return next((h.uzivatel for h in self.hraci if h.uzivatel.id == id_uzivatele), None)

    def pole_v_sachu(self) -> Optional[Pozice]:
        """Pozice krále hráče na tahu, pokud je v šachu (pro zvýraznění)."""
        if self.revizor_tahu.check_Šach(self.barva_na_tahu):
            return self.herni_plocha.najdi_krale(self.barva_na_tahu)
        return None

    # ------------------------------------------------------------ výběr figurky a tahy
    def je_vlastni_figurka(self, souradnice: Pozice) -> bool:
        figurka = self.herni_plocha.vrat_obsah(souradnice)
        return figurka is not None and figurka.barva == self.barva_na_tahu and not self.je_konec()

    def nastav_aktivni_figurku(self, souradnice: Optional[Pozice]) -> None:
        self.aktivni_figurka = souradnice
        self.mozne_tahy_figurky = []

    def vrat_mozne_tahy(self, souradnice: Pozice) -> List[Tah]:
        """Nastaví figurku jako aktivní a vrátí její legální tahy."""
        if not self.je_vlastni_figurka(souradnice):
            self.nastav_aktivni_figurku(None)
            return []
        figurka = self.herni_plocha.vrat_obsah(souradnice)
        assert figurka is not None
        self.nastav_aktivni_figurku(souradnice)
        self.mozne_tahy_figurky = self.revizor_tahu.mozne_tahy(figurka, souradnice)
        return self.mozne_tahy_figurky

    def mozne_tahy(self) -> List[Tah]:
        """Všechny legální tahy hráče na tahu."""
        return self.revizor_tahu.vsechny_tahy(self.barva_na_tahu)

    def moznosti_promeny(self, barva: int) -> List[Figurka]:
        """Figurky, na které se může pěšák proměnit (standardní + vlastní figurky ze hry)."""
        moznosti = [vytvor_figurku(n, barva) for n in ("Dáma", "Věž", "Střelec", "Kůň")]
        moznosti += [vytvor_figurku(n, barva, d) for n, d in self.definice_figurek.items()]
        return moznosti

    def proved_tah(self, souradnice: Pozice, promena_na: Optional[str] = None) -> bool:
        """Provede tah aktivní figurky na zadané pole. Vrací, zda byl tah proveden."""
        if self.je_konec() or self.aktivni_figurka is None:
            return False
        tah = next((t for t in self.mozne_tahy_figurky if t.cilova_pozice == tuple(souradnice)), None)
        if tah is None or not self.revizor_tahu.kontrola_tahu(tah):
            return False
        if tah.promena:
            povolene = [n for n in STANDARDNI if n not in ("Král", "Pěšák")] + list(self.definice_figurek)
            nazev = promena_na if promena_na in povolene else "Dáma"
            tah.promena_na = nazev
            tah.promena_definice = self.definice_figurek.get(nazev)

        self._snimky.append(self._snimek())
        barva = self.barva_na_tahu
        self.herni_plocha.proved_tah(tah)
        self.aktualni_tah = tah

        statistika = self.statistiky[barva]
        statistika["tahu"] += 1
        if tah.vyhozena_figurka is not None:
            statistika["vyhozeno"] += 1

        souper = -barva
        tah.sach = self.revizor_tahu.check_Šach(souper)
        if tah.sach:
            statistika["sachu"] += 1
        self.aktivni_hrac = 1 - self.aktivni_hrac          # na tahu je soupeř
        self._aktualizuj_stav()
        tah.mat = self.stav == self.MAT
        tah.notace = notace_tahu(tah, self.herni_plocha.rozmery)
        self.notace_historie.append(tah.notace)
        self.game_logger.uloz_tah(tah)

        self.posledni_kwesty = []
        if self.quest_manager is not None:
            hrac = self.hrac_barvy(barva)
            kwesty, odmeny = self.quest_manager.vyhodnot_kwesty(hrac, tah, statistika)
            if kwesty:
                self.posledni_kwesty.append((hrac, kwesty, odmeny))

        if self.je_konec():
            self.uloz_log()
        else:
            self.zacni_tah()
        return True

    def zacni_tah(self) -> Optional[Tah]:
        """Připraví nový tah hráče na tahu (vynuluje čas na tah). Vrací předchozí tah."""
        self.casovac.nuluj_cas()
        self.nastav_aktivni_figurku(None)
        return self.aktualni_tah

    def _aktualizuj_stav(self) -> None:
        barva = self.barva_na_tahu
        if self.revizor_tahu.check_Mat(barva):
            self.stav, self.vitez = self.MAT, -barva
        elif self.revizor_tahu.check_Pat(barva):
            self.stav, self.vitez = self.PAT, None
        elif self.revizor_tahu.nedostatek_materialu():
            self.stav, self.vitez = self.REMIZA, None
        elif self.revizor_tahu.check_Šach(barva):
            self.stav = self.SACH
        else:
            self.stav = self.PROBIHA

    # ------------------------------------------------------------ vrácení tahu
    def _snimek(self) -> dict:
        return {"plocha": self.herni_plocha.do_slovniku(), "aktivni_hrac": self.aktivni_hrac,
                "statistiky": copy.deepcopy(self.statistiky), "notace": list(self.notace_historie),
                "cas_tahu": self.casovac.cas_tahu}

    def lze_vratit_tah(self) -> bool:
        return bool(self._snimky) and not self.je_konec()

    def zrus_tah(self) -> None:
        """Vrátí poslední tah (jen hotseat)."""
        if not self._snimky:
            return
        snimek = self._snimky.pop()
        self.herni_plocha.obnov(snimek["plocha"])
        self.aktivni_hrac = snimek["aktivni_hrac"]
        self.statistiky = snimek["statistiky"]
        self.notace_historie = snimek["notace"]
        self.casovac.nuluj_cas()
        self.aktualni_tah = None
        self.nastav_aktivni_figurku(None)
        self._aktualizuj_stav()
        self.game_logger.zapis_text("    (tah vrácen)")

    # ------------------------------------------------------------ konec hry
    def ukonci(self, stav: int, vitez: Optional[int] = None) -> None:
        """Ukončí partii z vnějšího důvodu (čas, vzdání, dohoda na remíze, odpojení)."""
        if self.je_konec():
            return
        self.stav = stav
        self.vitez = vitez
        self.nastav_aktivni_figurku(None)
        self.uloz_log()

    def uloz_log(self) -> None:
        self.game_logger.zapis_text(f"Konec partie: {self.vysledek_text()} ({self.vysledek_pgn()})")

    def vysledek_pgn(self) -> str:
        if not self.je_konec() or self.stav == self.ODPOJENO:
            return "*"
        if self.vitez is None:
            return "½-½"
        return "1-0" if self.vitez == BILA else "0-1"

    def vysledek_text(self) -> str:
        vitez = NAZEV_BARVY.get(self.vitez, "") if self.vitez is not None else ""
        jmeno = self.hrac_barvy(self.vitez).jmeno if self.vitez is not None else ""
        texty = {
            self.PROBIHA: f"Na tahu: {NAZEV_BARVY[self.barva_na_tahu]}",
            self.SACH: f"Šach! Na tahu: {NAZEV_BARVY[self.barva_na_tahu]}",
            self.MAT: f"Šach mat – vyhrává {vitez} ({jmeno})",
            self.PAT: "Pat – remíza",
            self.CAS: f"Došel čas – vyhrává {vitez} ({jmeno})",
            self.VZDANO: f"Soupeř se vzdal – vyhrává {vitez} ({jmeno})",
            self.REMIZA: "Remíza",
            self.ODPOJENO: "Partie nedokončena",
        }
        return texty[self.stav]

    # ------------------------------------------------------------ uložení partie
    def do_slovniku(self) -> dict:
        return {
            "verze": 1,
            "plocha": self.herni_plocha.do_slovniku(),
            "hraci": [{"barva": h.barva, "id": h.uzivatel.id, "jmeno": h.uzivatel.zobrazovane_jmeno,
                       "host": h.uzivatel.je_host, "elo": h.uzivatel.elo} for h in self.hraci],
            "aktivni_hrac": self.aktivni_hrac,
            "casovac": self.casovac.do_slovniku(),
            "notace": self.notace_historie,
            "statistiky": {str(k): v for k, v in self.statistiky.items()},
            "definice_figurek": self.definice_figurek,
        }

    def obnov_stav(self, data: dict) -> None:
        """Doplní průběh partie z uloženého souboru (plochu a hráče řeší ten, kdo GameManager vytváří)."""
        self.aktivni_hrac = int(data.get("aktivni_hrac", 0))
        self.notace_historie = list(data.get("notace", []))
        for klic, hodnoty in data.get("statistiky", {}).items():
            self.statistiky[int(klic)] = dict(hodnoty)
        self._aktualizuj_stav()
