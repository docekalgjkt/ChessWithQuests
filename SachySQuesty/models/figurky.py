# -*- coding: utf-8 -*-
"""Figurky podle class diagramu: Figurka a potomci Kůň, Král, Dáma, Věž, Pěšák, Střelec
(+ VlastniFigurka pro figurky z editoru setu).

Pohyb každé figurky je popsán vektory:
  * vektory         – kam se smí pohnout na PRÁZDNÉ pole,
  * vektory_utoku   – kam smí BRÁT (a která pole napadá),
  * skok            – smí přeskakovat jiné figurky,
  * max_kroku       – kolikrát smí vektor zopakovat (0 = neomezeně, např. věž).
Vektor je (změna řádku, změna sloupce) z pohledu bílého; "vektor se vynásobí barvou",
takže pro černého (barva -1) se otočí.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Dict, Iterator, List, Optional, Tuple

from models.tah import BRANI, DVOJKROK, EN_PASSANT, NORMALNI, Tah
from utils.konstanty import BILA, SYMBOLY, ZKRATKY

if TYPE_CHECKING:
    from models.herni_plocha import HerniPlocha

Vektor = Tuple[int, int]
Pozice = Tuple[int, int]
Deska = List[List[Optional["Figurka"]]]

ORTOGONALNI: List[Vektor] = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIAGONALNI: List[Vektor] = [(-1, -1), (-1, 1), (1, -1), (1, 1)]
KONSKE: List[Vektor] = [(-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)]


class Figurka:
    """Obecná figurka. Konkrétní figurky jen nastaví své vektory."""

    def __init__(self, nazev: str, barva: int, vektory: List[Vektor],
                 vektory_utoku: Optional[List[Vektor]] = None, skok: bool = False,
                 max_kroku: int = 0, symbol: Optional[str] = None):
        self.nazev = nazev
        self.barva = barva                      # 1 = bílá, -1 = černá
        self.vektory: List[Vektor] = [(int(v[0]), int(v[1])) for v in vektory]
        self.vektory_utoku: List[Vektor] = [(int(v[0]), int(v[1]))
                                            for v in (vektory if vektory_utoku is None else vektory_utoku)]
        self.skok = skok
        self.max_kroku = max_kroku
        self.pohnuto = False                    # kvůli rošádě a dvojkroku pěšáka
        self._symbol = symbol

    # ------------------------------------------------------------ vzhled
    @property
    def symbol(self) -> str:
        """Znak figurky pro vykreslení (u standardních figurek plný šachový znak)."""
        if self._symbol:
            return self._symbol
        return SYMBOLY.get(self.nazev, ("?", "?"))[1]

    @property
    def zkratka(self) -> str:
        """Zkratka pro notaci (K, D, V, S, J, pěšák nemá žádnou)."""
        if self.nazev in ZKRATKY:
            return ZKRATKY[self.nazev]
        return self.symbol

    # ------------------------------------------------------------ pohyb
    def _otoc(self, vektory: List[Vektor]) -> List[Vektor]:
        return [(dr * self.barva, dc * self.barva) for dr, dc in vektory]

    def vektory_pohybu(self) -> List[Vektor]:
        return self._otoc(self.vektory)

    def vektory_napadeni(self) -> List[Vektor]:
        return self._otoc(self.vektory_utoku)

    def _paprsek(self, deska: Deska, pozice: Pozice, vektor: Vektor) -> Iterator[Tuple[Pozice, Optional["Figurka"]]]:
        """Projde pole ve směru vektoru. Bez skoku se zastaví na první figurce."""
        radky, sloupce = len(deska), len(deska[0])
        r, c = pozice
        dr, dc = vektor
        krok = 0
        while True:
            krok += 1
            if self.max_kroku and krok > self.max_kroku:
                return
            r += dr
            c += dc
            if not (0 <= r < radky and 0 <= c < sloupce):
                return
            obsah = deska[r][c]
            yield (r, c), obsah
            if obsah is not None and not self.skok:
                return

    def napadana_pole(self, deska: Deska, pozice: Pozice) -> List[Pozice]:
        """Pole, která figurka ohrožuje (pro kontrolu šachu)."""
        pole: List[Pozice] = []
        for v in self.vektory_napadeni():
            for cil, _ in self._paprsek(deska, pozice, v):
                pole.append(cil)
        return pole

    def pseudo_tahy(self, plocha: "HerniPlocha", pozice: Pozice) -> List[Tah]:
        """Tahy podle vektorů bez ohledu na to, jestli vlastní král zůstane v šachu."""
        deska = plocha.herni_deska
        tahy: List[Tah] = []
        cile = set()
        for v in self.vektory_pohybu():
            for cil, obsah in self._paprsek(deska, pozice, v):
                if obsah is None and cil not in cile:
                    tahy.append(Tah(pozice, cil, self, NORMALNI))
                    cile.add(cil)
        for v in self.vektory_napadeni():
            for cil, obsah in self._paprsek(deska, pozice, v):
                if obsah is not None and obsah.barva != self.barva and cil not in cile:
                    tah = Tah(pozice, cil, self, BRANI)
                    tah.vyhozena_figurka = obsah
                    tah.pozice_vyhozene = cil
                    tahy.append(tah)
                    cile.add(cil)
        return tahy

    # ------------------------------------------------------------ ukládání
    def do_slovniku(self) -> dict:
        return {"nazev": self.nazev, "barva": self.barva, "pohnuto": self.pohnuto}

    def __repr__(self) -> str:
        return f"{type(self).__name__}({'bílá' if self.barva == BILA else 'černá'})"


class Kůň(Figurka):
    def __init__(self, barva: int):
        super().__init__("Kůň", barva, KONSKE, skok=True, max_kroku=1)


class Král(Figurka):
    def __init__(self, barva: int):
        super().__init__("Král", barva, ORTOGONALNI + DIAGONALNI, skok=False, max_kroku=1)


class Dáma(Figurka):
    def __init__(self, barva: int):
        super().__init__("Dáma", barva, ORTOGONALNI + DIAGONALNI, skok=False)


class Věž(Figurka):
    def __init__(self, barva: int):
        super().__init__("Věž", barva, ORTOGONALNI, skok=False)


class Střelec(Figurka):
    def __init__(self, barva: int):
        super().__init__("Střelec", barva, DIAGONALNI, skok=False)


class Pěšák(Figurka):
    """Pěšák chodí rovně, bere šikmo; navíc dvojkrok, braní mimochodem a proměna."""

    def __init__(self, barva: int):
        super().__init__("Pěšák", barva, [(-1, 0)], [(-1, -1), (-1, 1)], skok=False, max_kroku=1)

    def pseudo_tahy(self, plocha: "HerniPlocha", pozice: Pozice) -> List[Tah]:
        tahy = super().pseudo_tahy(plocha, pozice)
        dr, dc = self.vektory_pohybu()[0]
        r, c = pozice
        # dvojkrok z výchozí pozice
        if not self.pohnuto:
            mezi, cil = (r + dr, c + dc), (r + 2 * dr, c + 2 * dc)
            if plocha.je_na_desce(cil) and plocha.vrat_obsah(mezi) is None and plocha.vrat_obsah(cil) is None:
                tahy.append(Tah(pozice, cil, self, DVOJKROK))
        # braní mimochodem
        if plocha.en_passant is not None:
            pole_ep, pozice_obeti = plocha.en_passant
            obet = plocha.vrat_obsah(pozice_obeti)
            for vr, vc in self.vektory_napadeni():
                if (r + vr, c + vc) == pole_ep and obet is not None and obet.barva != self.barva:
                    tah = Tah(pozice, pole_ep, self, EN_PASSANT)
                    tah.vyhozena_figurka = obet
                    tah.pozice_vyhozene = pozice_obeti
                    tahy.append(tah)
        # proměna na poslední řadě
        posledni_rada = 0 if self.barva == BILA else plocha.rozmery[0] - 1
        for tah in tahy:
            if tah.cilova_pozice[0] == posledni_rada:
                tah.promena = True
        return tahy


class VlastniFigurka(Figurka):
    """Figurka vytvořená v editoru setu (Graf. upravení setu).

    Navíc umí 'vektory_skoku' – skok o jeden vektor přes figurky (tah i braní),
    takže jde složit např. věž + kůň.
    """

    def __init__(self, definice: dict, barva: int):
        super().__init__(definice["nazev"], barva, definice.get("vektory", []),
                         definice.get("vektory_utoku"), bool(definice.get("skok", False)),
                         int(definice.get("max_kroku", 0)), definice.get("symbol") or definice["nazev"][:1])
        self.vektory_skoku: List[Vektor] = [(int(v[0]), int(v[1])) for v in definice.get("vektory_skoku", [])]
        self.definice = dict(definice)

    def _skoky(self, deska: Deska, pozice: Pozice) -> Iterator[Tuple[Pozice, Optional[Figurka]]]:
        radky, sloupce = len(deska), len(deska[0])
        for dr, dc in self._otoc(self.vektory_skoku):
            r, c = pozice[0] + dr, pozice[1] + dc
            if 0 <= r < radky and 0 <= c < sloupce:
                yield (r, c), deska[r][c]

    def napadana_pole(self, deska: Deska, pozice: Pozice) -> List[Pozice]:
        return super().napadana_pole(deska, pozice) + [cil for cil, _ in self._skoky(deska, pozice)]

    def pseudo_tahy(self, plocha: "HerniPlocha", pozice: Pozice) -> List[Tah]:
        tahy = super().pseudo_tahy(plocha, pozice)
        cile = {t.cilova_pozice for t in tahy}
        for cil, obsah in self._skoky(plocha.herni_deska, pozice):
            if cil in cile:
                continue
            if obsah is None:
                tahy.append(Tah(pozice, cil, self, NORMALNI))
            elif obsah.barva != self.barva:
                tah = Tah(pozice, cil, self, BRANI)
                tah.vyhozena_figurka = obsah
                tah.pozice_vyhozene = cil
                tahy.append(tah)
            else:
                continue
            cile.add(cil)
        return tahy

    def do_slovniku(self) -> dict:
        data = super().do_slovniku()
        data["definice"] = self.definice
        return data


STANDARDNI: Dict[str, type] = {
    "Král": Král, "Dáma": Dáma, "Věž": Věž, "Střelec": Střelec, "Kůň": Kůň, "Pěšák": Pěšák,
}


def vytvor_figurku(nazev: str, barva: int, definice: Optional[dict] = None) -> Figurka:
    """Tovární funkce – standardní figurka podle názvu, jinak vlastní podle definice."""
    if nazev in STANDARDNI:
        return STANDARDNI[nazev](barva)
    if definice is None:
        raise ValueError(f"Neznámá figurka '{nazev}' bez definice.")
    return VlastniFigurka(definice, barva)


def figurka_ze_slovniku(data: Optional[dict]) -> Optional[Figurka]:
    if data is None:
        return None
    figurka = vytvor_figurku(data["nazev"], int(data["barva"]), data.get("definice"))
    figurka.pohnuto = bool(data.get("pohnuto", False))
    return figurka
