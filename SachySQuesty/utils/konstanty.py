# -*- coding: utf-8 -*-
"""Společné konstanty celé aplikace ŠachySQuesty."""
import sys
from pathlib import Path

# ------------------------------------------------------------------ cesty
ZAKLADNI_SLOZKA = Path(__file__).resolve().parent.parent
SLOZKA_DATA = ZAKLADNI_SLOZKA / "data"                      # questy, nastavení
SLOZKA_UZIVATELE = ZAKLADNI_SLOZKA / "users" / "data"       # profily a historie
SLOZKA_SADY = ZAKLADNI_SLOZKA / "custom_pieces" / "sady"    # vlastní figurky
SLOZKA_LOGY = ZAKLADNI_SLOZKA / "logs"                      # logy partií
SLOZKA_ULOZENE = ZAKLADNI_SLOZKA / "saves"                  # uložené hry


def zajisti_slozky() -> None:
    """Vytvoří datové složky, pokud ještě neexistují."""
    for slozka in (SLOZKA_DATA, SLOZKA_UZIVATELE, SLOZKA_SADY, SLOZKA_LOGY, SLOZKA_ULOZENE):
        slozka.mkdir(parents=True, exist_ok=True)


# ------------------------------------------------------------------ barvy hráčů
# Podle class diagramu: barva (tým) je integer 1 nebo -1.
BILA = 1
CERNA = -1
NAZEV_BARVY = {BILA: "Bílý", CERNA: "Černý"}

# ------------------------------------------------------------------ herní plocha
MIN_ROZMER = 5
MAX_ROZMER = 12
STANDARDNI_FIGURKY = ["Král", "Dáma", "Věž", "Střelec", "Kůň", "Pěšák"]

# (obrys, plný) znak pro každou standardní figurku
SYMBOLY = {
    "Král": ("♔", "♚"),
    "Dáma": ("♕", "♛"),
    "Věž": ("♖", "♜"),
    "Střelec": ("♗", "♝"),
    "Kůň": ("♘", "♞"),
    "Pěšák": ("♙", "♟"),
}
# česká šachová notace (J = jezdec)
ZKRATKY = {"Král": "K", "Dáma": "D", "Věž": "V", "Střelec": "S", "Kůň": "J", "Pěšák": ""}

if sys.platform.startswith("win"):
    PISMO_FIGUREK = "Segoe UI Symbol"
elif sys.platform == "darwin":
    PISMO_FIGUREK = "Apple Symbols"
else:
    PISMO_FIGUREK = "DejaVu Sans"

# ------------------------------------------------------------------ vzhled
# název motivu -> (světlé pole, tmavé pole)
MOTIVY = {
    "Klasický": ("#f0d9b5", "#b58863"),
    "Zelený": ("#eeeed2", "#769656"),
    "Modrý": ("#dee3e6", "#8ca2ad"),
    "Šedý": ("#e6e6e6", "#8f8f8f"),
    "Fialový": ("#efe6f5", "#9a7bb0"),
    "Kontrastní": ("#ffffff", "#4a4a4a"),
}
VYCHOZI_MOTIV = "Klasický"

BARVA_VYBER = "#f6f669"
BARVA_POSLEDNI_TAH = "#cdd26a"
BARVA_SACH = "#e05050"
BARVA_MOZNY_TAH = "#3d6e3d"
BARVA_POZADI = "#f4f1ea"

# ------------------------------------------------------------------ LAN
LAN_PORT = 50007
