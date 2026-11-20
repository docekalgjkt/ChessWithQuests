# -*- coding: utf-8 -*-
"""UserManager – správa profilů hráčů, jejich historie a vyhodnocení ELO."""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from users.uzivatel import Uzivatel
from utils.konstanty import SLOZKA_UZIVATELE

K_FAKTOR = 32
EMAIL_VZOR = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class UserManager:
    def __init__(self, slozka: Path = SLOZKA_UZIVATELE):
        slozka.mkdir(parents=True, exist_ok=True)
        self.Id_uzivatele = 1                                    # další volné ID
        self.log_uzivatelu: Path = slozka / "uzivatele.json"     # soubor s profily
        self.historie_uzivatele: Path = slozka / "historie.json" # soubor s odehranými partiemi
        self.uzivatele: Dict[int, Uzivatel] = {}
        self.historie: List[dict] = []
        self.nacti()

    # ------------------------------------------------------------ soubory
    def nacti(self) -> None:
        if self.log_uzivatelu.exists():
            try:
                data = json.loads(self.log_uzivatelu.read_text(encoding="utf-8"))
                self.uzivatele = {int(d["id"]): Uzivatel.ze_slovniku(d) for d in data.get("uzivatele", [])}
                self.Id_uzivatele = int(data.get("dalsi_id", max(self.uzivatele, default=0) + 1))
            except (ValueError, KeyError, OSError):
                self.uzivatele = {}
        if self.historie_uzivatele.exists():
            try:
                self.historie = json.loads(self.historie_uzivatele.read_text(encoding="utf-8"))
            except (ValueError, OSError):
                self.historie = []

    def uloz(self) -> None:
        data = {"dalsi_id": self.Id_uzivatele, "uzivatele": [u.do_slovniku() for u in self.uzivatele.values()]}
        self.log_uzivatelu.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        self.historie_uzivatele.write_text(json.dumps(self.historie, ensure_ascii=False, indent=2), encoding="utf-8")

    # ------------------------------------------------------------ uživatelé
    def vytvor_uzivatele(self, uzivatelske_jmeno: str, jmeno: str = "", email: str = "") -> Uzivatel:
        uzivatelske_jmeno = uzivatelske_jmeno.strip()
        if not uzivatelske_jmeno:
            raise ValueError("Uživatelské jméno nesmí být prázdné.")
        if uzivatelske_jmeno.lower() == "host":
            raise ValueError("Jméno 'Host' je vyhrazené pro hráče bez profilu.")
        if any(u.uzivatelske_jmeno.lower() == uzivatelske_jmeno.lower() for u in self.uzivatele.values()):
            raise ValueError(f"Uživatel '{uzivatelske_jmeno}' už existuje.")
        if email and not EMAIL_VZOR.match(email.strip()):
            raise ValueError("E-mail nemá správný tvar.")
        uzivatel = Uzivatel(self.Id_uzivatele, uzivatelske_jmeno, jmeno.strip(), email.strip())
        self.uzivatele[uzivatel.id] = uzivatel
        self.Id_uzivatele += 1
        self.uloz()
        return uzivatel

    def smaz_uzivatele(self, id_uzivatele: int) -> None:
        self.uzivatele.pop(id_uzivatele, None)
        self.uloz()

    def najdi_uzivatele(self, id_uzivatele: int) -> Optional[Uzivatel]:
        return self.uzivatele.get(id_uzivatele)

    def vrat_uzivatele(self) -> List[Uzivatel]:
        return sorted(self.uzivatele.values(), key=lambda u: u.uzivatelske_jmeno.lower())

    @staticmethod
    def vytvor_hosta(jmeno: str = "Host", elo: int = 1200) -> Uzivatel:
        """Hráč bez profilu – hraje, ale nic se mu neukládá."""
        return Uzivatel(0, "host", jmeno, elo=elo, je_host=True)

    # ------------------------------------------------------------ výsledky
    @staticmethod
    def ocekavane_skore(elo_a: int, elo_b: int) -> float:
        return 1.0 / (1.0 + 10 ** ((elo_b - elo_a) / 400.0))

    def vyhodnot_elo(self, uzivatel: Uzivatel, elo_soupere: int, skore: float) -> int:
        """Upraví ELO uživatele (skóre 1 = výhra, 0.5 = remíza, 0 = prohra). Vrací změnu."""
        if uzivatel.je_host:
            return 0
        zmena = round(K_FAKTOR * (skore - self.ocekavane_skore(uzivatel.elo, elo_soupere)))
        uzivatel.elo += zmena
        return zmena

    @staticmethod
    def zaznamenej_vysledek(uzivatel: Uzivatel, vysledek: str) -> None:
        if uzivatel.je_host:
            return
        if vysledek == "vyhra":
            uzivatel.vyhry += 1
        elif vysledek == "prohra":
            uzivatel.prohry += 1
        else:
            uzivatel.remizy += 1

    def zaznamenej_partii(self, bily: Uzivatel, cerny: Uzivatel, vysledek: str, pocet_tahu: int,
                          rezim: str) -> None:
        """Zapíše partii do historie (vysledek: '1-0', '0-1' nebo '½-½')."""
        self.historie.append({
            "datum": datetime.now().strftime("%Y-%m-%d %H:%M"),
            "bily": {"id": bily.id, "jmeno": bily.zobrazovane_jmeno},
            "cerny": {"id": cerny.id, "jmeno": cerny.zobrazovane_jmeno},
            "vysledek": vysledek, "tahu": pocet_tahu, "rezim": rezim,
        })

    def vrat_historii(self, id_uzivatele: int) -> List[dict]:
        return [p for p in self.historie
                if (p["bily"]["id"] == id_uzivatele and id_uzivatele) or (p["cerny"]["id"] == id_uzivatele and id_uzivatele)]
