# -*- coding: utf-8 -*-
"""Export partie do souborů: MetadataWriter (údaje o partii) a ChessNotationWriter (PGN / FEN)."""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING

from models.figurky import Věž
from utils.konstanty import BILA, CERNA
from utils.notace import nazev_pole

if TYPE_CHECKING:
    from models.game_manager import GameManager

FEN_ZNAKY = {"Král": "k", "Dáma": "q", "Věž": "r", "Střelec": "b", "Kůň": "n", "Pěšák": "p"}


class ExportWriter(ABC):
    """Společný předek všech exportérů."""
    pripona = ".txt"

    @abstractmethod
    def vytvor_text(self, game_manager: "GameManager") -> str:
        ...

    def zapis(self, game_manager: "GameManager", cesta: Path) -> Path:
        cesta = Path(cesta).with_suffix(self.pripona)
        cesta.write_text(self.vytvor_text(game_manager), encoding="utf-8")
        return cesta


class MetadataWriter(ExportWriter):
    """Údaje o partii: hráči, nastavení, výsledek (bez parametrů)."""
    pripona = ".meta.txt"

    def vytvor_text(self, game_manager: "GameManager") -> str:
        gm = game_manager
        bily, cerny = gm.hraci
        casovac = gm.casovac
        radky = [
            "ŠachySQuesty – údaje o partii",
            f"Datum: {datetime.now():%d.%m.%Y %H:%M}",
            f"Bílý: {bily.jmeno} (ELO {bily.getEloRating()})",
            f"Černý: {cerny.jmeno} (ELO {cerny.getEloRating()})",
            f"Herní plocha: {gm.herni_plocha.rozmery[0]}×{gm.herni_plocha.rozmery[1]}",
            f"Čas na hru: {casovac.limit_hry // 60} min" if casovac.limit_hry else "Čas na hru: bez limitu",
            f"Čas na tah: {casovac.limit_tahu} s" if casovac.limit_tahu else "Čas na tah: bez limitu",
            f"Počet tahů: {len(gm.notace_historie)}",
            f"Stav: {gm.vysledek_text()}",
        ]
        return "\n".join(radky) + "\n"


class ChessNotationWriter(ExportWriter):
    """Zápis partie v notaci. format = 'PGN' (seznam tahů) nebo 'FEN' (aktuální pozice)."""

    def __init__(self, format: str = "PGN"):
        self.format = format.upper()
        self.pripona = ".pgn" if self.format == "PGN" else ".fen"

    def vytvor_text(self, game_manager: "GameManager") -> str:
        return self._pgn(game_manager) if self.format == "PGN" else self._fen(game_manager) + "\n"

    @staticmethod
    def _pgn(gm: "GameManager") -> str:
        bily, cerny = gm.hraci
        hlavicka = [
            '[Event "ŠachySQuesty"]',
            f'[Date "{datetime.now():%Y.%m.%d}"]',
            f'[White "{bily.jmeno}"]',
            f'[Black "{cerny.jmeno}"]',
            f'[Result "{gm.vysledek_pgn()}"]',
            f'[Board "{gm.herni_plocha.rozmery[0]}x{gm.herni_plocha.rozmery[1]}"]',
        ]
        tahy = []
        for i, notace in enumerate(gm.notace_historie):
            if i % 2 == 0:
                tahy.append(f"{i // 2 + 1}.")
            tahy.append(notace)
        tahy.append(gm.vysledek_pgn())
        return "\n".join(hlavicka) + "\n\n" + " ".join(tahy) + "\n"

    @staticmethod
    def _fen(gm: "GameManager") -> str:
        plocha = gm.herni_plocha
        rady = []
        for radek in plocha.herni_deska:
            text, prazdna = "", 0
            for f in radek:
                if f is None:
                    prazdna += 1
                    continue
                if prazdna:
                    text += str(prazdna)
                    prazdna = 0
                znak = FEN_ZNAKY.get(f.nazev, f.symbol[:1])
                text += znak.upper() if f.barva == BILA else znak.lower()
            if prazdna:
                text += str(prazdna)
            rady.append(text)
        rosady = ""
        for barva, k, q in ((BILA, "K", "Q"), (CERNA, "k", "q")):
            kral_pozice = plocha.najdi_krale(barva)
            kral = plocha.vrat_obsah(kral_pozice) if kral_pozice else None
            if kral_pozice is None or kral is None or kral.pohnuto:
                continue
            r, c = kral_pozice

            def ma_vez(sloupce: range) -> bool:
                return any(isinstance(f, Věž) and f.barva == barva and not f.pohnuto
                           for f in (plocha.herni_deska[r][x] for x in sloupce))
            vez_vpravo, vez_vlevo = ma_vez(range(c + 1, plocha.rozmery[1])), ma_vez(range(0, c))
            rosady += (k if vez_vpravo else "") + (q if vez_vlevo else "")
        ep = nazev_pole(plocha.en_passant[0], plocha.rozmery) if plocha.en_passant else "-"
        na_tahu = "w" if gm.barva_na_tahu == BILA else "b"
        cislo_tahu = len(gm.notace_historie) // 2 + 1
        return f"{'/'.join(rady)} {na_tahu} {rosady or '-'} {ep} 0 {cislo_tahu}"

