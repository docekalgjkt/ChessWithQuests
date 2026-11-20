# -*- coding: utf-8 -*-
"""HerniPlocha – šachovnice libovolné velikosti a operace s figurkami."""
from __future__ import annotations

from typing import List, Optional, Tuple

from models.figurky import Figurka, Král, Pěšák, figurka_ze_slovniku, vytvor_figurku
from models.tah import DVOJKROK, ROSADA, Tah
from utils.konstanty import BILA, CERNA, MAX_ROZMER, MIN_ROZMER

Pozice = Tuple[int, int]


class HerniPlocha:
    def __init__(self, rozmery: Tuple[int, int] = (8, 8)):
        radky, sloupce = int(rozmery[0]), int(rozmery[1])
        if not (MIN_ROZMER <= radky <= MAX_ROZMER and MIN_ROZMER <= sloupce <= MAX_ROZMER):
            raise ValueError(f"Rozměry plochy musí být {MIN_ROZMER}–{MAX_ROZMER}.")
        self.rozmery: Tuple[int, int] = (radky, sloupce)
        self.herni_deska: List[List[Optional[Figurka]]] = [[None] * sloupce for _ in range(radky)]
        self.vyhozene_figurky_b: List[Figurka] = []    # vyhozené bílé figurky
        self.vyhozene_figurky_c: List[Figurka] = []    # vyhozené černé figurky
        # (přeskočené pole, pozice pěšáka) po dvojkroku – pro braní mimochodem
        self.en_passant: Optional[Tuple[Pozice, Pozice]] = None

    # ------------------------------------------------------------ přístup k polím
    def je_na_desce(self, souradnice: Pozice) -> bool:
        r, c = souradnice
        return 0 <= r < self.rozmery[0] and 0 <= c < self.rozmery[1]

    def vrat_obsah(self, souradnice: Pozice) -> Optional[Figurka]:
        if not self.je_na_desce(souradnice):
            return None
        r, c = souradnice
        return self.herni_deska[r][c]

    def nastav_obsah(self, souradnice: Pozice, figurka: Optional[Figurka]) -> None:
        r, c = souradnice
        self.herni_deska[r][c] = figurka

    def figurky(self, barva: Optional[int] = None) -> List[Tuple[Pozice, Figurka]]:
        vysledek = []
        for r, radek in enumerate(self.herni_deska):
            for c, figurka in enumerate(radek):
                if figurka is not None and (barva is None or figurka.barva == barva):
                    vysledek.append(((r, c), figurka))
        return vysledek

    def najdi_figurku(self, figurka: Figurka) -> Optional[Pozice]:
        for pozice, f in self.figurky():
            if f is figurka:
                return pozice
        return None

    def najdi_krale(self, barva: int) -> Optional[Pozice]:
        for pozice, f in self.figurky(barva):
            if isinstance(f, Král):
                return pozice
        return None

    def vyhozene(self, barva: int) -> List[Figurka]:
        """Vyhozené figurky dané barvy."""
        return self.vyhozene_figurky_b if barva == BILA else self.vyhozene_figurky_c

    # ------------------------------------------------------------ provedení tahu
    def posun_figurky(self, tah: Tah) -> bool:
        """Přesune figurku z výchozí na cílovou pozici (a případně vyhodí soupeře)."""
        figurka = self.vrat_obsah(tah.vychozi_pozice)
        if figurka is None:
            return False
        if tah.pozice_vyhozene is not None:
            vyhozena = self.vrat_obsah(tah.pozice_vyhozene)
            if vyhozena is not None:
                self.vyhozene(vyhozena.barva).append(vyhozena)
                self.nastav_obsah(tah.pozice_vyhozene, None)
        self.nastav_obsah(tah.cilova_pozice, figurka)
        self.nastav_obsah(tah.vychozi_pozice, None)
        figurka.pohnuto = True
        return True

    def nahrad_figurku(self, figurka: Figurka, tah: Tah) -> None:
        """Nahradí figurku na cílovém poli tahu (proměna pěšáka)."""
        figurka.pohnuto = True
        self.nastav_obsah(tah.cilova_pozice, figurka)

    def proved_tah(self, tah: Tah) -> bool:
        """Provede celý tah včetně rošády, braní mimochodem a proměny."""
        barva = tah.figurka.barva
        if not self.posun_figurky(tah):
            return False
        if tah.typ_tahu == ROSADA and tah.vez_z is not None and tah.vez_na is not None:
            vez = self.vrat_obsah(tah.vez_z)
            self.nastav_obsah(tah.vez_na, vez)
            self.nastav_obsah(tah.vez_z, None)
            if vez is not None:
                vez.pohnuto = True
        if tah.promena:
            nova = vytvor_figurku(tah.promena_na or "Dáma", barva, tah.promena_definice)
            self.nahrad_figurku(nova, tah)
        if tah.typ_tahu == DVOJKROK:
            (r1, c1), (r2, c2) = tah.vychozi_pozice, tah.cilova_pozice
            self.en_passant = (((r1 + r2) // 2, c1), (r2, c2))
        else:
            self.en_passant = None
        return True

    # ------------------------------------------------------------ rozestavení
    def vycisti(self) -> None:
        radky, sloupce = self.rozmery
        self.herni_deska = [[None] * sloupce for _ in range(radky)]
        self.vyhozene_figurky_b.clear()
        self.vyhozene_figurky_c.clear()
        self.en_passant = None

    @staticmethod
    def zakladni_rada(sloupce: int) -> List[str]:
        """Rozestavení zadní řady pro libovolnou šířku (pro 8 sloupců klasické V J S D K S J V)."""
        rada: List[Optional[str]] = [None] * sloupce

        def poloz(i: int, nazev: str) -> None:
            if 0 <= i < sloupce and rada[i] is None:
                rada[i] = nazev

        poloz(sloupce // 2, "Král")
        poloz(sloupce // 2 - 1, "Dáma")
        for i, nazev in ((0, "Věž"), (1, "Kůň"), (2, "Střelec")):
            poloz(i, nazev)
            poloz(sloupce - 1 - i, nazev)
        nahradni = ["Kůň", "Střelec"]
        return [nazev or nahradni[i % 2] for i, nazev in enumerate(rada)]

    def standardni_rozestaveni(self) -> None:
        self.vycisti()
        radky, sloupce = self.rozmery
        rada = self.zakladni_rada(sloupce)
        for c in range(sloupce):
            self.herni_deska[0][c] = vytvor_figurku(rada[c], CERNA)
            self.herni_deska[1][c] = Pěšák(CERNA)
            self.herni_deska[radky - 2][c] = Pěšák(BILA)
            self.herni_deska[radky - 1][c] = vytvor_figurku(rada[c], BILA)

    def over_rozestaveni(self) -> Optional[str]:
        """Vrátí chybovou zprávu, pokud rozestavení nejde hrát, jinak None."""
        for barva, jmeno in ((BILA, "bílý"), (CERNA, "černý")):
            krale = [f for _, f in self.figurky(barva) if isinstance(f, Král)]
            if len(krale) != 1:
                return f"Každá strana musí mít právě jednoho krále ({jmeno} jich má {len(krale)})."
        posledni = {BILA: 0, CERNA: self.rozmery[0] - 1}
        for (r, _), f in self.figurky():
            if isinstance(f, Pěšák) and r == posledni[f.barva]:
                return "Pěšák nesmí na začátku stát na řadě, kde se proměňuje."
        return None

    # ------------------------------------------------------------ ukládání
    def do_slovniku(self) -> dict:
        return {
            "rozmery": list(self.rozmery),
            "deska": [[f.do_slovniku() if f else None for f in radek] for radek in self.herni_deska],
            "vyhozene_b": [f.do_slovniku() for f in self.vyhozene_figurky_b],
            "vyhozene_c": [f.do_slovniku() for f in self.vyhozene_figurky_c],
            "en_passant": [list(self.en_passant[0]), list(self.en_passant[1])] if self.en_passant else None,
        }

    def obnov(self, data: dict) -> None:
        """Načte stav ze slovníku do TÉTO plochy (objekt zůstane stejný)."""
        self.rozmery = (int(data["rozmery"][0]), int(data["rozmery"][1]))
        self.herni_deska = [[figurka_ze_slovniku(f) for f in radek] for radek in data["deska"]]
        self.vyhozene_figurky_b = [f for f in map(figurka_ze_slovniku, data.get("vyhozene_b", [])) if f is not None]
        self.vyhozene_figurky_c = [f for f in map(figurka_ze_slovniku, data.get("vyhozene_c", [])) if f is not None]
        ep = data.get("en_passant")
        self.en_passant = (tuple(ep[0]), tuple(ep[1])) if ep else None

    @classmethod
    def ze_slovniku(cls, data: dict) -> "HerniPlocha":
        plocha = cls(tuple(data["rozmery"]))
        plocha.obnov(data)
        return plocha

    def kopie(self) -> "HerniPlocha":
        return HerniPlocha.ze_slovniku(self.do_slovniku())
