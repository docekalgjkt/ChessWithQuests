# -*- coding: utf-8 -*-
"""Timer – hlídá čas na celou hru i na jeden tah (0 = bez limitu)."""
from __future__ import annotations

from typing import List, Optional


class Timer:
    def __init__(self, cas_na_hru: int = 0, cas_na_tah: int = 0):
        """Časy v sekundách. 0 znamená bez limitu."""
        self.limit_hry = max(0, int(cas_na_hru))
        self.limit_tahu = max(0, int(cas_na_tah))
        self.cas_hrac: List[int] = [self.limit_hry, self.limit_hry]   # zbývající čas hráčů
        self.cas_tahu = self.limit_tahu                               # zbývající čas na tah

    def nuluj_cas(self) -> None:
        """Na začátku tahu znovu nastaví čas na tah."""
        self.cas_tahu = self.limit_tahu

    def pocitej_cas(self, hrac: int) -> None:
        """Odečte jednu sekundu hráči na tahu (volá se každou sekundu)."""
        if self.limit_hry:
            self.cas_hrac[hrac] = max(0, self.cas_hrac[hrac] - 1)
        if self.limit_tahu:
            self.cas_tahu = max(0, self.cas_tahu - 1)

    def vyprsel_cas(self, hrac: int) -> bool:
        return bool((self.limit_hry and self.cas_hrac[hrac] <= 0) or (self.limit_tahu and self.cas_tahu <= 0))

    def zbyva_hrac(self, hrac: int) -> Optional[int]:
        return self.cas_hrac[hrac] if self.limit_hry else None

    def zbyva_tah(self) -> Optional[int]:
        return self.cas_tahu if self.limit_tahu else None

    @staticmethod
    def formatuj(sekundy: Optional[int]) -> str:
        if sekundy is None:
            return "∞"
        return f"{sekundy // 60:02d}:{sekundy % 60:02d}"

    def do_slovniku(self) -> dict:
        return {"limit_hry": self.limit_hry, "limit_tahu": self.limit_tahu,
                "cas_hrac": list(self.cas_hrac), "cas_tahu": self.cas_tahu}

    @classmethod
    def ze_slovniku(cls, data: dict) -> "Timer":
        timer = cls(data["limit_hry"], data["limit_tahu"])
        timer.cas_hrac = list(data["cas_hrac"])
        timer.cas_tahu = int(data["cas_tahu"])
        return timer
