# -*- coding: utf-8 -*-
"""Uzivatel – profil hráče (ELO, XP, body, splněné questy, statistiky)."""
from __future__ import annotations

from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from models.quest import Quest

VYCHOZI_ELO = 1200


class Uzivatel:
    def __init__(self, id_uzivatele: int, uzivatelske_jmeno: str, jmeno: str = "", email: str = "",
                 elo: int = VYCHOZI_ELO, je_host: bool = False):
        self.id = id_uzivatele
        self.uzivatelske_jmeno = uzivatelske_jmeno
        self.jmeno = jmeno
        self.email = email
        self.elo = elo
        self.splnene_kwesty: List[str] = []     # ID splněných questů
        self.xp = 0
        self.body = 0
        self.vyhry = 0
        self.prohry = 0
        self.remizy = 0
        self.je_host = je_host                  # host = hráč bez profilu (nic se neukládá)

    @property
    def odehrane_partie(self) -> int:
        return self.vyhry + self.prohry + self.remizy

    @property
    def uspesnost(self) -> float:
        """Úspěšnost v procentech (remíza = půl bodu)."""
        if not self.odehrane_partie:
            return 0.0
        return 100.0 * (self.vyhry + 0.5 * self.remizy) / self.odehrane_partie

    @property
    def uroven(self) -> int:
        """Úroveň hráče podle XP – každých 100 XP jedna úroveň."""
        return 1 + self.xp // 100

    @property
    def zobrazovane_jmeno(self) -> str:
        return self.jmeno or self.uzivatelske_jmeno

    def ma_quest(self, quest: "Quest") -> bool:
        return quest.id in self.splnene_kwesty

    def pridej_quest(self, quest: "Quest") -> bool:
        """Zapíše splněný quest a připíše odměnu. Vrací False, pokud už byl splněn dřív."""
        if self.ma_quest(quest):
            return False
        self.splnene_kwesty.append(quest.id)
        self.xp += quest.odmena_xp
        self.body += quest.odmena_body
        return True

    def do_slovniku(self) -> dict:
        return {
            "id": self.id, "uzivatelske_jmeno": self.uzivatelske_jmeno, "jmeno": self.jmeno,
            "email": self.email, "elo": self.elo, "splnene_kwesty": list(self.splnene_kwesty),
            "xp": self.xp, "body": self.body, "vyhry": self.vyhry, "prohry": self.prohry,
            "remizy": self.remizy,
        }

    @classmethod
    def ze_slovniku(cls, data: dict) -> "Uzivatel":
        u = cls(int(data["id"]), data["uzivatelske_jmeno"], data.get("jmeno", ""), data.get("email", ""),
                int(data.get("elo", VYCHOZI_ELO)))
        u.splnene_kwesty = list(data.get("splnene_kwesty", []))
        for klic in ("xp", "body", "vyhry", "prohry", "remizy"):
            setattr(u, klic, int(data.get(klic, 0)))
        return u

    def __repr__(self) -> str:
        return f"Uzivatel({self.id}, {self.uzivatelske_jmeno})"
