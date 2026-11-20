# -*- coding: utf-8 -*-
"""Třída Tah – jeden tah figurky (viz class diagram)."""
from __future__ import annotations

from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from models.figurky import Figurka
    from models.herni_plocha import HerniPlocha

Pozice = Tuple[int, int]

# možné hodnoty atributu typ_tahu
NORMALNI = "normalni"
BRANI = "brani"
DVOJKROK = "dvojkrok"
EN_PASSANT = "en_passant"
ROSADA = "rosada"


class Tah:
    """Tah z výchozí na cílovou pozici. Pozice jsou (řádek, sloupec), řádek 0 je nahoře (strana černého)."""

    def __init__(self, vychozi_pozice: Pozice, cilova_pozice: Pozice, figurka: "Figurka",
                 typ_tahu: str = NORMALNI):
        self.vychozi_pozice: Pozice = (int(vychozi_pozice[0]), int(vychozi_pozice[1]))
        self.cilova_pozice: Pozice = (int(cilova_pozice[0]), int(cilova_pozice[1]))
        self.figurka = figurka
        self.typ_tahu = typ_tahu
        # doplňující informace
        self.vyhozena_figurka: Optional["Figurka"] = None
        self.pozice_vyhozene: Optional[Pozice] = None   # u en passant se liší od cílové pozice
        self.vez_z: Optional[Pozice] = None              # rošáda – odkud jde věž
        self.vez_na: Optional[Pozice] = None             # rošáda – kam jde věž
        self.promena = False                             # pěšák došel na poslední řadu
        self.promena_na: Optional[str] = None            # název nové figurky
        self.promena_definice: Optional[dict] = None     # definice, je-li nová figurka vlastní
        self.sach = False
        self.mat = False
        self.notace = ""

    def over_platnost(self, rozmery: Tuple[int, int] = (8, 8)) -> bool:
        """Základní kontrola: obě pozice leží na desce a nejsou stejné (pravidla řeší RevizorTahu)."""
        radky, sloupce = rozmery
        for r, c in (self.vychozi_pozice, self.cilova_pozice):
            if not (0 <= r < radky and 0 <= c < sloupce):
                return False
        return self.vychozi_pozice != self.cilova_pozice and self.figurka is not None

    def proved_tah(self, herni_plocha: "HerniPlocha") -> None:
        """Provede tah na zadané herní ploše."""
        herni_plocha.proved_tah(self)

    def __repr__(self) -> str:
        return f"Tah({self.figurka and self.figurka.nazev}, {self.vychozi_pozice}->{self.cilova_pozice}, {self.typ_tahu})"
