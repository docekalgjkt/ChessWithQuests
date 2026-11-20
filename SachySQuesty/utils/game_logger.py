# -*- coding: utf-8 -*-
"""GameLogger – průběžně zapisuje tahy partie do textového logu."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from utils.konstanty import SLOZKA_LOGY

if TYPE_CHECKING:
    from models.tah import Tah


class GameLogger:
    def __init__(self, slozka: Path = SLOZKA_LOGY):
        self.slozka = slozka
        self.soubor: Optional[Path] = None
        self.pocet_tahu = 0

    def vytvor_soubor(self, nazev: str) -> None:
        """Založí nový log, např. vytvor_soubor('Pepa vs Host')."""
        self.slozka.mkdir(parents=True, exist_ok=True)
        cas = datetime.now().strftime("%Y%m%d_%H%M%S")
        bezpecny = "".join(z if z.isalnum() or z in "-_" else "_" for z in nazev)[:40]
        self.soubor = self.slozka / f"partie_{cas}_{bezpecny}.log"
        self.pocet_tahu = 0
        self._zapis(f"ŠachySQuesty – {nazev}\nZačátek: {datetime.now():%d.%m.%Y %H:%M:%S}\n")

    def uloz_tah(self, tah: "Tah") -> None:
        self.pocet_tahu += 1
        barva = "bílý" if tah.figurka.barva == 1 else "černý"
        self._zapis(f"{self.pocet_tahu:>3}. {barva:<6} {tah.notace}\n")

    def zapis_text(self, text: str) -> None:
        self._zapis(text + "\n")

    def _zapis(self, text: str) -> None:
        if self.soubor is None:
            return
        try:
            with open(self.soubor, "a", encoding="utf-8") as f:
                f.write(text)
        except OSError:
            pass  # log nesmí shodit hru
