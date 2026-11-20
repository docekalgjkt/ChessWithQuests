# -*- coding: utf-8 -*-
"""RevizorTahu – hlídá šachová pravidla: legální tahy, šach, mat, pat, rošáda."""
from __future__ import annotations

from typing import List, Optional, Tuple

from models.figurky import Deska, Figurka, Král, Věž
from models.herni_plocha import HerniPlocha
from models.tah import ROSADA, Tah

Pozice = Tuple[int, int]


class RevizorTahu:
    def __init__(self, herni_plocha: HerniPlocha):
        self.herni_plocha = herni_plocha
        self.tah: Optional[Tah] = None          # naposledy kontrolovaný tah

    # ------------------------------------------------------------ simulace
    def simulate_Move(self, tah: Tah) -> Deska:
        """Vrátí KOPII desky, na které je tah proveden (původní deska se nemění)."""
        deska = [radek[:] for radek in self.herni_plocha.herni_deska]
        (r1, c1), (r2, c2) = tah.vychozi_pozice, tah.cilova_pozice
        if tah.pozice_vyhozene is not None:
            pr, pc = tah.pozice_vyhozene
            deska[pr][pc] = None
        deska[r2][c2] = deska[r1][c1]
        deska[r1][c1] = None
        if tah.typ_tahu == ROSADA and tah.vez_z and tah.vez_na:
            (vr1, vc1), (vr2, vc2) = tah.vez_z, tah.vez_na
            deska[vr2][vc2] = deska[vr1][vc1]
            deska[vr1][vc1] = None
        return deska

    @staticmethod
    def je_napadeno(deska: Deska, pole: Pozice, barva_utocnika: int) -> bool:
        for r, radek in enumerate(deska):
            for c, figurka in enumerate(radek):
                if figurka is not None and figurka.barva == barva_utocnika:
                    if pole in figurka.napadana_pole(deska, (r, c)):
                        return True
        return False

    @staticmethod
    def _najdi_krale(deska: Deska, barva: int) -> Optional[Pozice]:
        for r, radek in enumerate(deska):
            for c, figurka in enumerate(radek):
                if isinstance(figurka, Král) and figurka.barva == barva:
                    return (r, c)
        return None

    # ------------------------------------------------------------ šach, mat, pat
    def check_Šach(self, barva: int, deska: Optional[Deska] = None) -> bool:
        """Je král dané barvy v šachu?"""
        deska = self.herni_plocha.herni_deska if deska is None else deska
        kral = self._najdi_krale(deska, barva)
        if kral is None:
            return False
        return self.je_napadeno(deska, kral, -barva)

    def check_Mat(self, barva: int) -> bool:
        return self.check_Šach(barva) and not self.vsechny_tahy(barva)

    def check_Pat(self, barva: int) -> bool:
        return not self.check_Šach(barva) and not self.vsechny_tahy(barva)

    def nedostatek_materialu(self) -> bool:
        """Na desce zůstali jen králové – remíza."""
        return all(isinstance(f, Král) for _, f in self.herni_plocha.figurky())

    # ------------------------------------------------------------ legální tahy
    def mozne_tahy(self, figurka: Figurka, pozice: Optional[Pozice] = None) -> List[Tah]:
        """Všechny legální tahy figurky (vlastní král po tahu nesmí být v šachu)."""
        if pozice is None:
            pozice = self.herni_plocha.najdi_figurku(figurka)
            if pozice is None:
                return []
        kandidati = figurka.pseudo_tahy(self.herni_plocha, pozice)
        if isinstance(figurka, Král):
            kandidati += self._rosady(figurka, pozice)
        return [t for t in kandidati if not self.check_Šach(figurka.barva, self.simulate_Move(t))]

    def _rosady(self, kral: Král, pozice: Pozice) -> List[Tah]:
        if kral.pohnuto or self.check_Šach(kral.barva):
            return []
        deska = self.herni_plocha.herni_deska
        sloupce = self.herni_plocha.rozmery[1]
        r, c = pozice
        tahy = []
        for smer in (-1, 1):
            x = c + smer
            while 0 <= x < sloupce and deska[r][x] is None:
                x += smer
            if not (0 <= x < sloupce) or abs(x - c) < 3:
                continue
            vez = deska[r][x]
            if not isinstance(vez, Věž) or vez.barva != kral.barva or vez.pohnuto:
                continue
            # král nesmí projít napadeným polem
            if any(self.je_napadeno(deska, (r, c + smer * k), -kral.barva) for k in (1, 2)):
                continue
            tah = Tah(pozice, (r, c + 2 * smer), kral, ROSADA)
            tah.vez_z = (r, x)
            tah.vez_na = (r, c + smer)
            tahy.append(tah)
        return tahy

    def vsechny_tahy(self, barva: int) -> List[Tah]:
        tahy: List[Tah] = []
        for pozice, figurka in self.herni_plocha.figurky(barva):
            tahy.extend(self.mozne_tahy(figurka, pozice))
        return tahy

    def kontrola_tahu(self, tah: Tah) -> bool:
        """Ověří, že je tah podle pravidel."""
        self.tah = tah
        figurka = self.herni_plocha.vrat_obsah(tah.vychozi_pozice)
        if figurka is None or figurka is not tah.figurka or not tah.over_platnost(self.herni_plocha.rozmery):
            return False
        return any(t.cilova_pozice == tah.cilova_pozice for t in self.mozne_tahy(figurka, tah.vychozi_pozice))
