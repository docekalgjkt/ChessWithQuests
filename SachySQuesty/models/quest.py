# -*- coding: utf-8 -*-
"""Quest a QuestManager – úkoly/achievementy, za které hráč dostává XP a body."""
from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple

from models.tah import EN_PASSANT, ROSADA, Tah
from utils.konstanty import SLOZKA_DATA

if TYPE_CHECKING:
    from models.hrac import Hrac

# typ questu -> popis podmínky (N / P je parametr questu)
TYPY_QUESTU: Dict[str, str] = {
    "vyhozeni": "Vyhoď v jedné partii alespoň N figurek",
    "vyhozeni_figurky": "Vyhoď soupeři figurku s názvem P",
    "rosada": "Proveď rošádu",
    "promena": "Proměň pěšáka",
    "en_passant": "Vezmi mimochodem (en passant)",
    "sach": "Dej v jedné partii alespoň N šachů",
    "vyhra": "Vyhraj partii",
    "vyhra_do_tahu": "Vyhraj partii do N vlastních tahů",
    "remiza": "Dosáhni remízy",
    "odehrane_partie": "Odehraj celkem alespoň N partií",
}
TAHOVE_TYPY = {"vyhozeni", "vyhozeni_figurky", "rosada", "promena", "en_passant", "sach"}

Odmeny = Dict[str, int]


class Quest:
    def __init__(self, id_questu: str, nazev: str, popis: str, typ: str, parametr: str = "",
                 odmena_xp: int = 10, odmena_body: int = 5, aktivni: bool = True):
        if typ not in TYPY_QUESTU:
            raise ValueError(f"Neznámý typ questu: {typ}")
        self.id = id_questu
        self.nazev = nazev
        self.popis = popis
        self.typ = typ
        self.parametr = parametr
        self.odmena_xp = int(odmena_xp)
        self.odmena_body = int(odmena_body)
        self.aktivni = aktivni

    def _cislo(self, vychozi: int = 1) -> int:
        try:
            return int(self.parametr)
        except (TypeError, ValueError):
            return vychozi

    def validate(self, udalost: dict) -> bool:
        """Je quest splněn touto událostí? Událost je 'tah' nebo 'konec' partie."""
        if not self.aktivni:
            return False
        typ = self.typ
        if udalost.get("druh") == "tah":
            if typ == "vyhozeni":
                return udalost.get("vyhozeno_v_partii", 0) >= self._cislo()
            if typ == "vyhozeni_figurky":
                return bool(udalost.get("vyhozena")) and udalost.get("vyhozena", "").lower() == str(self.parametr).strip().lower()
            if typ == "rosada":
                return udalost.get("typ_tahu") == ROSADA
            if typ == "promena":
                return bool(udalost.get("promena"))
            if typ == "en_passant":
                return udalost.get("typ_tahu") == EN_PASSANT
            if typ == "sach":
                return udalost.get("sachu_v_partii", 0) >= self._cislo()
            return False
        if udalost.get("druh") == "konec":
            vysledek = udalost.get("vysledek")
            if typ == "vyhra":
                return vysledek == "vyhra"
            if typ == "vyhra_do_tahu":
                return vysledek == "vyhra" and udalost.get("tahu", 10 ** 6) <= self._cislo(20)
            if typ == "remiza":
                return vysledek == "remiza"
            if typ == "odehrane_partie":
                return udalost.get("odehrane_partie", 0) >= self._cislo()
        return False

    def do_slovniku(self) -> dict:
        return {"id": self.id, "nazev": self.nazev, "popis": self.popis, "typ": self.typ,
                "parametr": self.parametr, "odmena_xp": self.odmena_xp,
                "odmena_body": self.odmena_body, "aktivni": self.aktivni}

    @classmethod
    def ze_slovniku(cls, d: dict) -> "Quest":
        return cls(d["id"], d["nazev"], d.get("popis", ""), d["typ"], str(d.get("parametr", "")),
                   int(d.get("odmena_xp", 10)), int(d.get("odmena_body", 5)), bool(d.get("aktivni", True)))


VYCHOZI_QUESTY = [
    ("Ochutnávka", "Vyhoď svou první figurku.", "vyhozeni", "1", 10, 5),
    ("Lovec", "Vyhoď v jedné partii 6 figurek.", "vyhozeni", "6", 40, 20),
    ("Královrah dámy", "Vyhoď soupeři dámu.", "vyhozeni_figurky", "Dáma", 30, 15),
    ("Hrad v bezpečí", "Proveď rošádu.", "rosada", "", 15, 5),
    ("Povýšení", "Proměň pěšáka na jinou figurku.", "promena", "", 30, 15),
    ("Mimochodem", "Vezmi pěšáka mimochodem.", "en_passant", "", 40, 20),
    ("Šach!", "Dej v jedné partii 3 šachy.", "sach", "3", 15, 5),
    ("První vítězství", "Vyhraj partii.", "vyhra", "", 50, 25),
    ("Blesková výhra", "Vyhraj partii do 25 vlastních tahů.", "vyhra_do_tahu", "25", 60, 30),
    ("Smír", "Dosáhni remízy.", "remiza", "", 20, 10),
    ("Veterán", "Odehraj 10 partií.", "odehrane_partie", "10", 100, 50),
]


class QuestManager:
    def __init__(self, soubor: Path = SLOZKA_DATA / "questy.json"):
        self.soubor = soubor
        self.questy: List[Quest] = []
        self.nacti()

    # ------------------------------------------------------------ soubor (log questů)
    def nacti(self) -> None:
        if self.soubor.exists():
            try:
                data = json.loads(self.soubor.read_text(encoding="utf-8"))
                self.questy = [Quest.ze_slovniku(d) for d in data]
                return
            except (ValueError, KeyError, OSError):
                pass
        self.questy = [Quest(f"q{i + 1}", *q) for i, q in enumerate(VYCHOZI_QUESTY)]
        self.uloz()

    def uloz(self) -> None:
        self.soubor.parent.mkdir(parents=True, exist_ok=True)
        self.soubor.write_text(json.dumps([q.do_slovniku() for q in self.questy], ensure_ascii=False, indent=2),
                               encoding="utf-8")

    def najdi_quest(self, id_questu: str) -> Optional[Quest]:
        return next((q for q in self.questy if q.id == id_questu), None)

    def _nove_id(self) -> str:
        cisla = [int(q.id[1:]) for q in self.questy if q.id[1:].isdigit()]
        return f"q{max(cisla, default=0) + 1}"

    def pridej_quest(self, nazev: str, popis: str, typ: str, parametr: str, odmena_xp: int,
                     odmena_body: int, aktivni: bool = True) -> Quest:
        self._over(nazev, typ)
        quest = Quest(self._nove_id(), nazev.strip(), popis.strip(), typ, parametr.strip(), odmena_xp, odmena_body, aktivni)
        self.questy.append(quest)
        self.uloz()
        return quest

    def uprav_quest(self, quest: Quest, nazev: str, popis: str, typ: str, parametr: str, odmena_xp: int,
                    odmena_body: int, aktivni: bool = True) -> None:
        self._over(nazev, typ)
        quest.nazev, quest.popis, quest.typ = nazev.strip(), popis.strip(), typ
        quest.parametr, quest.odmena_xp, quest.odmena_body = parametr.strip(), int(odmena_xp), int(odmena_body)
        quest.aktivni = aktivni
        self.uloz()

    def smaz_quest(self, quest: Quest) -> None:
        self.questy = [q for q in self.questy if q.id != quest.id]
        self.uloz()

    @staticmethod
    def _over(nazev: str, typ: str) -> None:
        if not nazev.strip():
            raise ValueError("Quest musí mít název.")
        if typ not in TYPY_QUESTU:
            raise ValueError("Vyber typ questu.")

    # ------------------------------------------------------------ vyhodnocení
    def _vyhodnot(self, hrac: "Hrac", udalost: dict) -> Tuple[List[Quest], Odmeny]:
        splnene: List[Quest] = []
        odmeny: Odmeny = {"xp": 0, "body": 0}
        uzivatel = hrac.uzivatel
        if uzivatel.je_host:
            return splnene, odmeny
        for quest in self.questy:
            if not uzivatel.ma_quest(quest) and quest.validate(udalost):
                uzivatel.pridej_quest(quest)
                splnene.append(quest)
                odmeny["xp"] += quest.odmena_xp
                odmeny["body"] += quest.odmena_body
        return splnene, odmeny

    def vyhodnot_kwesty(self, hrac: "Hrac", tah: Tah, statistiky: Optional[dict] = None) -> Tuple[List[Quest], Odmeny]:
        """Vyhodnotí questy po tahu hráče. Vrací (splněné questy, odměny)."""
        statistiky = statistiky or {}
        udalost = {
            "druh": "tah",
            "typ_tahu": tah.typ_tahu,
            "promena": tah.promena,
            "vyhozena": tah.vyhozena_figurka.nazev if tah.vyhozena_figurka else None,
            "sach": tah.sach,
            "vyhozeno_v_partii": statistiky.get("vyhozeno", 0),
            "sachu_v_partii": statistiky.get("sachu", 0),
        }
        return self._vyhodnot(hrac, udalost)

    def vyhodnot_konec_partie(self, hrac: "Hrac", vysledek: str, pocet_tahu: int) -> Tuple[List[Quest], Odmeny]:
        """Vyhodnotí questy po konci partie (vysledek: 'vyhra' / 'prohra' / 'remiza')."""
        udalost = {"druh": "konec", "vysledek": vysledek, "tahu": pocet_tahu,
                   "odehrane_partie": hrac.uzivatel.odehrane_partie}
        return self._vyhodnot(hrac, udalost)
