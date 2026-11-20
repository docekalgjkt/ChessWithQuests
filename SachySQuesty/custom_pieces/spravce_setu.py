# -*- coding: utf-8 -*-
"""SpravceSetu – ukládání a načítání vlastních figurek (sady/<název>.json)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, List, Optional

from models.figurky import STANDARDNI, VlastniFigurka
from utils.konstanty import SLOZKA_SADY

UKAZKOVE_FIGURKY = [
    {   # věž + kůň (z variant Capablanca chess)
        "nazev": "Kancléř", "symbol": "C", "skok": False, "max_kroku": 0,
        "vektory": [[-1, 0], [1, 0], [0, -1], [0, 1]], "vektory_utoku": [[-1, 0], [1, 0], [0, -1], [0, 1]],
        "vektory_skoku": [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]],
    },
    {   # chodí o jedno pole do všech stran, bere jen dopředu šikmo – "silnější pěšák"
        "nazev": "Strážce", "symbol": "G", "skok": False, "max_kroku": 1,
        "vektory": [[-1, -1], [-1, 0], [-1, 1], [0, -1], [0, 1], [1, -1], [1, 0], [1, 1]],
        "vektory_utoku": [[-1, -1], [-1, 1]],
    },
    {   # skáče přesně o dvě pole rovně i šikmo (přes figurky)
        "nazev": "Skokan", "symbol": "Z", "skok": True, "max_kroku": 1,
        "vektory": [[-2, 0], [2, 0], [0, -2], [0, 2], [-2, -2], [-2, 2], [2, -2], [2, 2]],
        "vektory_utoku": [[-2, 0], [2, 0], [0, -2], [0, 2], [-2, -2], [-2, 2], [2, -2], [2, 2]],
    },
]


class SpravceSetu:
    def __init__(self, slozka: Path = SLOZKA_SADY, nazev_setu: str = "muj_set"):
        self.slozka = slozka
        self.slozka.mkdir(parents=True, exist_ok=True)
        self.nazev_setu = nazev_setu
        self.definice: Dict[str, dict] = {}
        if not any(self.slozka.glob("*.json")):
            self.definice = {str(d["nazev"]): self._uprav_definici(d) for d in UKAZKOVE_FIGURKY}
            self.uloz_set()
        self.nacti_set(nazev_setu)

    # ------------------------------------------------------------ sety
    def vrat_sety(self) -> List[str]:
        return sorted(p.stem for p in self.slozka.glob("*.json"))

    def _cesta(self, nazev: str) -> Path:
        bezpecny = "".join(z for z in nazev if z.isalnum() or z in "-_ ").strip() or "muj_set"
        return self.slozka / f"{bezpecny}.json"

    def nacti_set(self, nazev: str) -> None:
        self.nazev_setu = nazev
        cesta = self._cesta(nazev)
        self.definice = {}
        if cesta.exists():
            try:
                for d in json.loads(cesta.read_text(encoding="utf-8")):
                    self.definice[d["nazev"]] = self._uprav_definici(d)
            except (ValueError, KeyError, OSError):
                self.definice = {}

    def uloz_set(self) -> None:
        self._cesta(self.nazev_setu).write_text(
            json.dumps(list(self.definice.values()), ensure_ascii=False, indent=2), encoding="utf-8")

    # ------------------------------------------------------------ figurky
    @staticmethod
    def _uprav_definici(d: dict) -> dict:
        """Sjednotí formát definice. 'vektory_skoku' (např. u kancléře) jsou tahy přes figurky o 1 krok."""
        vektory = [list(v) for v in d.get("vektory", [])]
        utok = [list(v) for v in d.get("vektory_utoku", vektory)]
        return {"nazev": str(d["nazev"]).strip(), "symbol": str(d.get("symbol", d["nazev"][:1]))[:2],
                "skok": bool(d.get("skok", False)), "max_kroku": int(d.get("max_kroku", 0)),
                "vektory": vektory, "vektory_utoku": utok,
                "vektory_skoku": [list(v) for v in d.get("vektory_skoku", [])]}

    @staticmethod
    def over_definici(d: dict) -> Optional[str]:
        """Vrátí text chyby, nebo None, když je definice v pořádku."""
        nazev = str(d.get("nazev", "")).strip()
        if not nazev:
            return "Figurka musí mít název."
        if nazev in STANDARDNI:
            return "Název standardní figurky nelze použít."
        if not str(d.get("symbol", "")).strip():
            return "Figurka musí mít symbol (1–2 znaky)."
        if not (d.get("vektory") or d.get("vektory_utoku") or d.get("vektory_skoku")):
            return "Figurka se musí umět pohnout – přidej aspoň jeden vektor."
        return None

    def uloz_figurku(self, definice: dict, puvodni_nazev: Optional[str] = None) -> None:
        chyba = self.over_definici(definice)
        if chyba:
            raise ValueError(chyba)
        definice = self._uprav_definici(definice)
        if puvodni_nazev and puvodni_nazev != definice["nazev"]:
            self.definice.pop(puvodni_nazev, None)
        self.definice[definice["nazev"]] = definice
        self.uloz_set()

    def smaz_figurku(self, nazev: str) -> None:
        self.definice.pop(nazev, None)
        self.uloz_set()

    def vrat_definici(self, nazev: str) -> Optional[dict]:
        return self.definice.get(nazev)

    def vrat_nazvy(self) -> List[str]:
        return sorted(self.definice)

    def vytvor_figurku(self, nazev: str, barva: int) -> VlastniFigurka:
        return VlastniFigurka(self.definice[nazev], barva)
