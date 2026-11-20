# -*- coding: utf-8 -*-
"""Konfigurace – uložené nastavení vzhledu (motiv desky, velikost polí...)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Tuple

from utils.konstanty import MOTIVY, SLOZKA_DATA, VYCHOZI_MOTIV


class Konfigurace:
    def __init__(self, soubor: Path = SLOZKA_DATA / "nastaveni.json"):
        self.soubor = soubor
        self.motiv = VYCHOZI_MOTIV
        self.velikost_pole = 64
        self.zobrazit_souradnice = True
        self.zobrazit_mozne_tahy = True
        self.aktivni_set = "muj_set"
        self.nacti()

    def barvy_poli(self) -> Tuple[str, str]:
        return MOTIVY.get(self.motiv, MOTIVY[VYCHOZI_MOTIV])

    def vzhled(self) -> dict:
        """Slovník pro views (ty o Konfiguraci nemusí vědět)."""
        return {"barvy_poli": self.barvy_poli(), "velikost_pole": self.velikost_pole,
                "zobrazit_souradnice": self.zobrazit_souradnice,
                "zobrazit_mozne_tahy": self.zobrazit_mozne_tahy}

    def nacti(self) -> None:
        if not self.soubor.exists():
            return
        try:
            data = json.loads(self.soubor.read_text(encoding="utf-8"))
        except (ValueError, OSError):
            return
        if data.get("motiv") in MOTIVY:
            self.motiv = data["motiv"]
        self.velikost_pole = min(96, max(32, int(data.get("velikost_pole", self.velikost_pole))))
        self.zobrazit_souradnice = bool(data.get("zobrazit_souradnice", True))
        self.zobrazit_mozne_tahy = bool(data.get("zobrazit_mozne_tahy", True))
        self.aktivni_set = str(data.get("aktivni_set", self.aktivni_set))

    def uloz(self) -> None:
        self.soubor.parent.mkdir(parents=True, exist_ok=True)
        data = {"motiv": self.motiv, "velikost_pole": self.velikost_pole,
                "zobrazit_souradnice": self.zobrazit_souradnice,
                "zobrazit_mozne_tahy": self.zobrazit_mozne_tahy, "aktivni_set": self.aktivni_set}
        self.soubor.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
