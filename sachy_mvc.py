#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Šachy v architektuře MVC (Model-View-Controller) s grafickým rozhraním Tkinter.
Samostatně spustitelná desktopová aplikace (PyCharm / Python 3) bez externích závislostí.
"""

import random
import tkinter as tk
from tkinter import messagebox
from typing import Any, List, Optional, Tuple


# =====================================================================
# 1. MODEL — Základní entity (Kwest, Uzivatel, Hrac)
# =====================================================================

class Kwest:
    """Reprezentuje herní úkol (quest), který může hráč splnit."""

    def __init__(self, nazev: str, popis: str, odmena_elo: int = 25):
        self.nazev: str = nazev
        self.popis: str = popis
        self.odmena_elo: int = odmena_elo
        self.splneno: bool = False

    def validate(self) -> bool:
        return self.splneno


class Uzivatel:
    """Reprezentuje uživatele a jeho ELO rating."""

    def __init__(self, uzivatelske_jmeno: str, jmeno: str, email: str, elo: int = 1200):
        self.uzivatelske_jmeno: str = uzivatelske_jmeno
        self.jmeno: str = jmeno
        self.email: str = email
        self.elo: int = elo
        self.splnene_kwesty: List[Kwest] = []

    def pridej_kwest(self, quest: Kwest) -> None:
        if quest not in self.splnene_kwesty:
            self.splnene_kwesty.append(quest)
            quest.splneno = True
            self.elo += quest.odmena_elo


class Hrac:
    """Reprezentuje hráče v aktuální partii (0 = Bílý, 1 = Černý)."""

    def __init__(self, barva: int, uzivatel: Uzivatel, je_bot: bool = False):
        self.barva: int = barva
        self.uzivatel: Uzivatel = uzivatel
        self.je_bot: bool = je_bot

    def getEloRating(self) -> int:
        return self.uzivatel.elo


# =====================================================================
# 2. MODEL — Hierarchie šachových figurek
# =====================================================================

class Figurka:
    """Základní třída pro všechny šachové figury."""

    def __init__(self, nazev: str, barva: int):
        self.nazev: str = nazev
        self.barva: int = barva  # 0 = bílá, 1 = černá
        self.vektory: List[List[int]] = []
        self.vektory_utoku: List[List[int]] = []
        self.skok: bool = False
        self.symbol: str = " "
        self.hodnota: int = 0
        self.pocet_tahu: int = 0
        self.aktivni: bool = True

    def klon(self) -> "Figurka":
        nova = self.__class__(self.barva)
        nova.pocet_tahu = self.pocet_tahu
        nova.aktivni = self.aktivni
        return nova

    def __repr__(self) -> str:
        barva_str = "B" if self.barva == 0 else "C"
        return f"{self.nazev}({barva_str})"


class Kun(Figurka):
    def __init__(self, barva: int):
        super().__init__("Kůň", barva)
        self.skok = True
        self.hodnota = 3
        self.symbol = "♞"
        self.vektory = [
            [-2, -1], [-2, 1], [-1, -2], [-1, 2],
            [1, -2], [1, 2], [2, -1], [2, 1],
        ]
        self.vektory_utoku = self.vektory


class Kral(Figurka):
    def __init__(self, barva: int):
        super().__init__("Král", barva)
        self.hodnota = 1000
        self.symbol = "♚"
        self.vektory = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1],           [0, 1],
            [1, -1],  [1, 0],  [1, 1],
        ]
        self.vektory_utoku = self.vektory


class Dama(Figurka):
    def __init__(self, barva: int):
        super().__init__("Dáma", barva)
        self.hodnota = 9
        self.symbol = "♛"
        self.vektory = [
            [-1, -1], [-1, 0], [-1, 1],
            [0, -1],           [0, 1],
            [1, -1],  [1, 0],  [1, 1],
        ]
        self.vektory_utoku = self.vektory


class Strelec(Figurka):
    def __init__(self, barva: int):
        super().__init__("Střelec", barva)
        self.hodnota = 3
        self.symbol = "♝"
        self.vektory = [[-1, -1], [-1, 1], [1, -1], [1, 1]]
        self.vektory_utoku = self.vektory


class Vez(Figurka):
    def __init__(self, barva: int):
        super().__init__("Věž", barva)
        self.hodnota = 5
        self.symbol = "♜"
        self.vektory = [[-1, 0], [1, 0], [0, -1], [0, 1]]
        self.vektory_utoku = self.vektory


class Pesak(Figurka):
    def __init__(self, barva: int):
        super().__init__("Pěšák", barva)
        self.hodnota = 1
        self.symbol = "♟"
        self.smer: int = -1 if barva == 0 else 1
        self.vektory = [[self.smer, 0]]
        self.vektory_utoku = [[self.smer, -1], [self.smer, 1]]


def vytvor_figurku(nazev: str, barva: int) -> Figurka:
    mapa = {
        "Dáma": Dama,
        "Věž": Vez,
        "Střelec": Strelec,
        "Kůň": Kun,
        "Král": Kral,
        "Pěšák": Pesak,
    }
    return mapa.get(nazev, Dama)(barva)


# =====================================================================
# 3. MODEL — Tah, HerniPlocha, Timer, GameLogger, RevizorTahu, GameManager
# =====================================================================

class Tah:
    """Reprezentuje jeden šachový tah."""

    def __init__(
        self,
        vychozi_pozice: List[int],
        cilova_pozice: List[int],
        figurka: Figurka,
        typ_tahu: str = "normal",
        vyhozena_figurka: Optional[Figurka] = None,
        povyseni_na: Optional[str] = None,
    ):
        self.vychozi_pozice: List[int] = list(vychozi_pozice)
        self.cilova_pozice: List[int] = list(cilova_pozice)
        self.figurka: Figurka = figurka
        self.typ_tahu: str = typ_tahu  # normal, brani, rosada, en_passant, povyseni
        self.vyhozena_figurka: Optional[Figurka] = vyhozena_figurka
        self.povyseni_na: Optional[str] = povyseni_na
        self.sach: bool = False
        self.mat: bool = False

    def over_platnost(self) -> bool:
        r1, c1 = self.vychozi_pozice
        r2, c2 = self.cilova_pozice
        return 0 <= r1 < 8 and 0 <= c1 < 8 and 0 <= r2 < 8 and 0 <= c2 < 8

    def proved_tah(self) -> None:
        self.figurka.pocet_tahu += 1

    def notace(self) -> str:
        sloupce = ["a", "b", "c", "d", "e", "f", "g", "h"]
        radky = ["8", "7", "6", "5", "4", "3", "2", "1"]
        cil = f"{sloupce[self.cilova_pozice[1]]}{radky[self.cilova_pozice[0]]}"

        if self.typ_tahu == "rosada":
            znacka = "#" if self.mat else ("+" if self.sach else "")
            return ("O-O" if self.cilova_pozice[1] == 6 else "O-O-O") + znacka

        prefix_mapa = {
            "Pěšák": sloupce[self.vychozi_pozice[1]] if self.vyhozena_figurka else "",
            "Kůň": "J",
            "Střelec": "S",
            "Věž": "V",
            "Dáma": "D",
            "Král": "K",
        }
        prefix = prefix_mapa.get(self.figurka.nazev, "")
        brani = "x" if self.vyhozena_figurka else ""
        promo = ""
        if self.typ_tahu == "povyseni":
            promo_mapa = {"Dáma": "=D", "Věž": "=V", "Střelec": "=S", "Kůň": "=J"}
            promo = promo_mapa.get(self.povyseni_na or "Dáma", "=D")
        znacka = "#" if self.mat else ("+" if self.sach else "")
        return f"{prefix}{brani}{cil}{promo}{znacka}"


class HerniPlocha:
    """Spravuje 8x8 matici šachovnice a vyhozené figury."""

    def __init__(self, prazdna: bool = False):
        self.rozmery: Tuple[int, int] = (8, 8)
        self.herni_deska: List[List[Optional[Figurka]]] = [
            [None for _ in range(8)] for _ in range(8)
        ]
        self.vyhozene_figurky_b: List[Figurka] = []
        self.vyhozene_figurky_c: List[Figurka] = []
        if not prazdna:
            self.nastav_zakladni_rozestaveni()

    def nastav_zakladni_rozestaveni(self) -> None:
        self.herni_deska = [[None for _ in range(8)] for _ in range(8)]
        self.vyhozene_figurky_b.clear()
        self.vyhozene_figurky_c.clear()

        hlavni = [Vez, Kun, Strelec, Dama, Kral, Strelec, Kun, Vez]
        for c in range(8):
            self.herni_deska[0][c] = hlavni[c](1)
            self.herni_deska[1][c] = Pesak(1)
            self.herni_deska[6][c] = Pesak(0)
            self.herni_deska[7][c] = hlavni[c](0)

    def vrat_obsah(self, souradnice: Tuple[int, int]) -> Optional[Figurka]:
        r, c = souradnice
        if 0 <= r < 8 and 0 <= c < 8:
            return self.herni_deska[r][c]
        return None

    def kopie(self) -> "HerniPlocha":
        nova = HerniPlocha(prazdna=True)
        for r in range(8):
            for c in range(8):
                f = self.herni_deska[r][c]
                if f is not None:
                    nova.herni_deska[r][c] = f.klon()
        return nova

    def posun_figurky(self, tah: Tah) -> bool:
        if not tah.over_platnost():
            return False

        r1, c1 = tah.vychozi_pozice
        r2, c2 = tah.cilova_pozice
        fig = self.herni_deska[r1][c1]
        if not fig:
            return False

        # Rošáda (přesun věže)
        if tah.typ_tahu == "rosada" and fig.nazev == "Král":
            if c2 == 6:
                vez = self.herni_deska[r1][7]
                self.herni_deska[r1][7] = None
                self.herni_deska[r1][5] = vez
                if vez:
                    vez.pocet_tahu += 1
            elif c2 == 2:
                vez = self.herni_deska[r1][0]
                self.herni_deska[r1][0] = None
                self.herni_deska[r1][3] = vez
                if vez:
                    vez.pocet_tahu += 1

        # En passant (braní mimochodem)
        if tah.typ_tahu == "en_passant":
            sebrany = self.herni_deska[r1][c2]
            if sebrany:
                sebrany.aktivni = False
                tah.vyhozena_figurka = sebrany
                self.herni_deska[r1][c2] = None
                if sebrany.barva == 0:
                    self.vyhozene_figurky_b.append(sebrany)
                else:
                    self.vyhozene_figurky_c.append(sebrany)
        else:
            cil_obsah = self.herni_deska[r2][c2]
            if cil_obsah:
                cil_obsah.aktivni = False
                tah.vyhozena_figurka = cil_obsah
                if cil_obsah.barva == 0:
                    self.vyhozene_figurky_b.append(cil_obsah)
                else:
                    self.vyhozene_figurky_c.append(cil_obsah)

        # Povýšení pěšce
        if fig.nazev == "Pěšák" and (r2 == 0 or r2 == 7):
            cilova_trida = tah.povyseni_na or "Dáma"
            nova_fig = vytvor_figurku(cilova_trida, fig.barva)
            nova_fig.pocet_tahu = fig.pocet_tahu
            fig = nova_fig
            tah.typ_tahu = "povyseni"

        self.herni_deska[r1][c1] = None
        self.herni_deska[r2][c2] = fig
        tah.proved_tah()
        return True

    def najdi_krale(self, barva: int) -> Optional[Tuple[int, int]]:
        for r in range(8):
            for c in range(8):
                f = self.herni_deska[r][c]
                if f and f.nazev == "Král" and f.barva == barva:
                    return (r, c)
        return None


class Timer:
    """Šachový časovač se samostatným odpočtem pro oba hráče."""

    def __init__(self, vychozi_sekundy: int = 300):
        self.vychozi_sekundy: int = vychozi_sekundy
        self.cas_hrac: List[int] = [vychozi_sekundy, vychozi_sekundy]
        self.bezi: bool = False

    def nuluj_cas(self) -> None:
        self.cas_hrac = [self.vychozi_sekundy, self.vychozi_sekundy]
        self.bezi = False

    def pocitej_cas(self, hrac: int) -> None:
        if self.bezi and self.cas_hrac[hrac] > 0:
            self.cas_hrac[hrac] -= 1

    def formatuj_cas(self, hrac: int) -> str:
        s = max(0, self.cas_hrac[hrac])
        return f"{s // 60:02d}:{s % 60:02d}"


class GameLogger:
    """Ukládá a exportuje záznam šachové partie."""

    def __init__(self, soubor: str = "log_partie.txt"):
        self.soubor: str = soubor
        self.tahy: List[Tah] = []

    def uloz_tah(self, tah: Tah) -> None:
        self.tahy.append(tah)

    def vytvor_soubor(self, nazev: str) -> None:
        self.soubor = nazev
        with open(nazev, "w", encoding="utf-8") as f:
            f.write("=== ZÁZNAM ŠACHOVÉ PARTIE ===\n")
            for i in range(0, len(self.tahy), 2):
                cislo = i // 2 + 1
                bily = self.tahy[i].notace()
                cerny = self.tahy[i + 1].notace() if (i + 1) < len(self.tahy) else ""
                f.write(f"{cislo}. {bily:<8} {cerny}\n")


class RevizorTahu:
    """Validátor šachových pravidel (šach, mat, pat, rošáda, en passant)."""

    def __init__(self, herni_plocha: HerniPlocha):
        self.herni_plocha: HerniPlocha = herni_plocha
        self.posledni_tah: Optional[Tah] = None

    def simulate_Move(self, tah: Tah) -> bool:
        r1, c1 = tah.vychozi_pozice
        r2, c2 = tah.cilova_pozice
        puvodni_start = self.herni_plocha.herni_deska[r1][c1]
        puvodni_cil = self.herni_plocha.herni_deska[r2][c2]
        ep_fig = None

        if tah.typ_tahu == "en_passant":
            ep_fig = self.herni_plocha.herni_deska[r1][c2]
            self.herni_plocha.herni_deska[r1][c2] = None

        self.herni_plocha.herni_deska[r1][c1] = None
        self.herni_plocha.herni_deska[r2][c2] = puvodni_start

        je_v_sachu = self.check_Sach(tah.figurka.barva)

        self.herni_plocha.herni_deska[r1][c1] = puvodni_start
        self.herni_plocha.herni_deska[r2][c2] = puvodni_cil
        if tah.typ_tahu == "en_passant":
            self.herni_plocha.herni_deska[r1][c2] = ep_fig

        return not je_v_sachu

    def check_Sach(self, barva: int, plocha: Optional[HerniPlocha] = None) -> bool:
        deska_obj = plocha or self.herni_plocha
        kral_pos = deska_obj.najdi_krale(barva)
        if not kral_pos:
            return False

        opacna = 1 if barva == 0 else 0
        kr, kc = kral_pos

        for r in range(8):
            for c in range(8):
                fig = deska_obj.herni_deska[r][c]
                if fig and fig.barva == opacna:
                    if self._muze_napadnout(fig, (r, c), (kr, kc), deska_obj):
                        return True
        return False

    def _muze_napadnout(
        self,
        fig: Figurka,
        odkud: Tuple[int, int],
        kam: Tuple[int, int],
        deska_obj: HerniPlocha,
    ) -> bool:
        r1, c1 = odkud
        r2, c2 = kam
        dr = r2 - r1
        dc = c2 - c1

        if fig.nazev == "Pěšák":
            smer = -1 if fig.barva == 0 else 1
            return dr == smer and abs(dc) == 1
        if fig.nazev == "Kůň":
            return [dr, dc] in fig.vektory
        if fig.nazev == "Král":
            return max(abs(dr), abs(dc)) == 1 and (dr != 0 or dc != 0)

        je_diag = abs(dr) == abs(dc) and dr != 0
        je_orto = (dr == 0 and dc != 0) or (dc == 0 and dr != 0)

        if fig.nazev == "Střelec" and not je_diag:
            return False
        if fig.nazev == "Věž" and not je_orto:
            return False
        if fig.nazev == "Dáma" and not (je_diag or je_orto):
            return False

        step_r = 0 if dr == 0 else (1 if dr > 0 else -1)
        step_c = 0 if dc == 0 else (1 if dc > 0 else -1)

        cr, cc = r1 + step_r, c1 + step_c
        while (cr, cc) != (r2, c2):
            if deska_obj.herni_deska[cr][cc] is not None:
                return False
            cr += step_r
            cc += step_c
        return True

    def generuj_tahy_figury(self, pozice: Tuple[int, int]) -> List[Tah]:
        r, c = pozice
        fig = self.herni_plocha.herni_deska[r][c]
        if not fig:
            return []

        tahy: List[Tah] = []

        if fig.nazev == "Pěšák":
            smer = -1 if fig.barva == 0 else 1
            r_pred = r + smer
            posledni_rada = 0 if fig.barva == 0 else 7

            if 0 <= r_pred < 8 and self.herni_plocha.herni_deska[r_pred][c] is None:
                typ = "povyseni" if r_pred == posledni_rada else "normal"
                tahy.append(Tah([r, c], [r_pred, c], fig, typ))

                start_rada = 6 if fig.barva == 0 else 1
                r_dva = r + 2 * smer
                if r == start_rada and self.herni_plocha.herni_deska[r_dva][c] is None:
                    tahy.append(Tah([r, c], [r_dva, c], fig, "normal"))

            for dc in [-1, 1]:
                sc = c + dc
                if 0 <= r_pred < 8 and 0 <= sc < 8:
                    cil_obsah = self.herni_plocha.herni_deska[r_pred][sc]
                    if cil_obsah and cil_obsah.barva != fig.barva:
                        typ = "povyseni" if r_pred == posledni_rada else "brani"
                        tahy.append(Tah([r, c], [r_pred, sc], fig, typ, cil_obsah))

                    # En passant
                    if (
                        self.posledni_tah
                        and self.posledni_tah.figurka.nazev == "Pěšák"
                        and abs(self.posledni_tah.vychozi_pozice[0] - self.posledni_tah.cilova_pozice[0]) == 2
                        and self.posledni_tah.cilova_pozice == [r, sc]
                    ):
                        souper_pesak = self.herni_plocha.herni_deska[r][sc]
                        if souper_pesak and souper_pesak.barva != fig.barva:
                            tahy.append(Tah([r, c], [r_pred, sc], fig, "en_passant", souper_pesak))

        elif fig.skok:
            for dr, dc in fig.vektory:
                nr, nc = r + dr, c + dc
                if 0 <= nr < 8 and 0 <= nc < 8:
                    cil_obsah = self.herni_plocha.herni_deska[nr][nc]
                    if cil_obsah is None:
                        tahy.append(Tah([r, c], [nr, nc], fig, "normal"))
                    elif cil_obsah.barva != fig.barva:
                        tahy.append(Tah([r, c], [nr, nc], fig, "brani", cil_obsah))
        else:
            max_dosah = 1 if fig.nazev == "Král" else 7
            for dr, dc in fig.vektory:
                for k in range(1, max_dosah + 1):
                    nr, nc = r + dr * k, c + dc * k
                    if not (0 <= nr < 8 and 0 <= nc < 8):
                        break
                    cil_obsah = self.herni_plocha.herni_deska[nr][nc]
                    if cil_obsah is None:
                        tahy.append(Tah([r, c], [nr, nc], fig, "normal"))
                    else:
                        if cil_obsah.barva != fig.barva:
                            tahy.append(Tah([r, c], [nr, nc], fig, "brani", cil_obsah))
                        break

            # Rošáda
            if fig.nazev == "Král" and fig.pocet_tahu == 0 and not self.check_Sach(fig.barva):
                v1 = self.herni_plocha.herni_deska[r][7]
                if v1 and v1.nazev == "Věž" and v1.barva == fig.barva and v1.pocet_tahu == 0:
                    if self.herni_plocha.herni_deska[r][5] is None and self.herni_plocha.herni_deska[r][6] is None:
                        if self.simulate_Move(Tah([r, c], [r, 5], fig)):
                            tahy.append(Tah([r, c], [r, 6], fig, "rosada"))

                v2 = self.herni_plocha.herni_deska[r][0]
                if v2 and v2.nazev == "Věž" and v2.barva == fig.barva and v2.pocet_tahu == 0:
                    if (
                        self.herni_plocha.herni_deska[r][1] is None
                        and self.herni_plocha.herni_deska[r][2] is None
                        and self.herni_plocha.herni_deska[r][3] is None
                    ):
                        if self.simulate_Move(Tah([r, c], [r, 3], fig)):
                            tahy.append(Tah([r, c], [r, 2], fig, "rosada"))

        return tahy

    def generuj_vsechny_legalni_tahy(self, barva: int) -> List[Tah]:
        vsechny: List[Tah] = []
        for r in range(8):
            for c in range(8):
                fig = self.herni_plocha.herni_deska[r][c]
                if fig and fig.barva == barva:
                    for t in self.generuj_tahy_figury((r, c)):
                        if self.simulate_Move(t):
                            vsechny.append(t)
        return vsechny

    def check_Mat(self, barva: int) -> bool:
        return self.check_Sach(barva) and len(self.generuj_vsechny_legalni_tahy(barva)) == 0

    def check_Pat(self, barva: int) -> bool:
        return not self.check_Sach(barva) and len(self.generuj_vsechny_legalni_tahy(barva)) == 0

    def nedostatek_materialu(self) -> bool:
        figury = [
            f for row in self.herni_plocha.herni_deska for f in row if f is not None
        ]
        if len(figury) == 2:
            return True
        if len(figury) == 3:
            non_king = [f for f in figury if f.nazev != "Král"]
            if len(non_king) == 1 and non_king[0].nazev in ("Kůň", "Střelec"):
                return True
        return False


class GameManager:
    """Hlavní model herní logiky, pravidel, AI bota a stavu partie."""

    def __init__(self):
        self.plocha: HerniPlocha = HerniPlocha()
        self.aktivni_hrac: int = 0
        self.hraci: List[Hrac] = []
        self.casovac: Timer = Timer(300)
        self.game_logger: GameLogger = GameLogger("log_partie.txt")
        self.revizor_tahu: RevizorTahu = RevizorTahu(self.plocha)
        self.stav_hry: str = "hra"  # hra, sach, mat, pat, remiza, cas
        self.kwesty: List[Kwest] = self._vytvor_kwesty()

    def _vytvor_kwesty(self) -> List[Kwest]:
        return [
            Kwest("První krev", "Vyhoď soupeřovu figuru v prvních 10 tazích", 25),
            Kwest("Královská pevnost", "Proveď rošádu", 20),
            Kwest("Šach!", "Dej soupeřovu králi šach", 15),
            Kwest("Lov na dámu", "Vyhoď soupeřovu dámu", 35),
            Kwest("Šachmat", "Vyhraj partii matem", 50),
        ]

    def mozne_tahy(self, pozice: Tuple[int, int]) -> List[Tah]:
        kandidati = self.revizor_tahu.generuj_tahy_figury(pozice)
        return [t for t in kandidati if self.revizor_tahu.simulate_Move(t)]

    def proved_tah(self, tah: Tah) -> bool:
        if self.stav_hry in ("mat", "pat", "remiza", "cas"):
            return False

        self.casovac.bezi = True
        self.plocha.posun_figurky(tah)
        self.revizor_tahu.posledni_tah = tah

        opacny = 1 if self.aktivni_hrac == 0 else 0
        tah.sach = self.revizor_tahu.check_Sach(opacny)
        tah.mat = self.revizor_tahu.check_Mat(opacny)

        self.game_logger.uloz_tah(tah)
        self._zkontroluj_kwesty(tah)

        if tah.mat:
            self.stav_hry = "mat"
            self.casovac.bezi = False
        elif self.revizor_tahu.check_Pat(opacny):
            self.stav_hry = "pat"
            self.casovac.bezi = False
        elif self.revizor_tahu.nedostatek_materialu():
            self.stav_hry = "remiza"
            self.casovac.bezi = False
        elif tah.sach:
            self.stav_hry = "sach"
        else:
            self.stav_hry = "hra"

        self.aktivni_hrac = opacny
        return True

    def _zkontroluj_kwesty(self, tah: Tah) -> None:
        if not self.hraci:
            return
        uzivatel = self.hraci[self.aktivni_hrac].uzivatel

        if tah.vyhozena_figurka and len(self.game_logger.tahy) <= 20 and not self.kwesty[0].splneno:
            uzivatel.pridej_kwest(self.kwesty[0])
        if tah.typ_tahu == "rosada" and not self.kwesty[1].splneno:
            uzivatel.pridej_kwest(self.kwesty[1])
        if tah.sach and not tah.mat and not self.kwesty[2].splneno:
            uzivatel.pridej_kwest(self.kwesty[2])
        if tah.vyhozena_figurka and tah.vyhozena_figurka.nazev == "Dáma" and not self.kwesty[3].splneno:
            uzivatel.pridej_kwest(self.kwesty[3])
        if tah.mat and not self.kwesty[4].splneno:
            uzivatel.pridej_kwest(self.kwesty[4])

    def vrat_zpet(self) -> bool:
        if not self.game_logger.tahy:
            return False

        # V režimu proti botovi vracíme 2 půltahy (tah bota + tah hráče), pokud je na tahu hráč
        pocet_zpet = (
            2
            if len(self.hraci) == 2 and self.hraci[1].je_bot and self.aktivni_hrac == 0 and len(self.game_logger.tahy) >= 2
            else 1
        )
        stare_tahy = self.game_logger.tahy[:-pocet_zpet]

        self.plocha.nastav_zakladni_rozestaveni()
        self.game_logger.tahy.clear()
        self.revizor_tahu.posledni_tah = None
        self.aktivni_hrac = 0

        for t in stare_tahy:
            fig = self.plocha.vrat_obsah((t.vychozi_pozice[0], t.vychozi_pozice[1]))
            if fig:
                novy_tah = Tah(
                    t.vychozi_pozice,
                    t.cilova_pozice,
                    fig,
                    t.typ_tahu,
                    povyseni_na=t.povyseni_na,
                )
                self.plocha.posun_figurky(novy_tah)
                novy_tah.sach = t.sach
                novy_tah.mat = t.mat
                self.game_logger.uloz_tah(novy_tah)
                self.revizor_tahu.posledni_tah = novy_tah
                self.aktivni_hrac = 1 if self.aktivni_hrac == 0 else 0

        if self.revizor_tahu.check_Sach(self.aktivni_hrac):
            self.stav_hry = "sach"
        else:
            self.stav_hry = "hra"
        self.casovac.bezi = len(self.game_logger.tahy) > 0
        return True

    def vypocitej_tah_bota(self) -> Optional[Tah]:
        """Jednoduchý taktický šachový bot (vyhodnocení materiálu, středu a bezpečnosti)."""
        barva = self.aktivni_hrac
        mozne = self.revizor_tahu.generuj_vsechny_legalni_tahy(barva)
        if not mozne:
            return None

        opacna = 1 if barva == 0 else 0
        nejlepsi_tah = mozne[0]
        nejlepsi_skore = -999999.0

        for t in mozne:
            if t.typ_tahu == "povyseni" and not t.povyseni_na:
                t.povyseni_na = "Dáma"

            skore = 0.0
            if t.vyhozena_figurka:
                skore += t.vyhozena_figurka.hodnota * 10.0

            cr, cc = t.cilova_pozice
            if cr in (3, 4) and cc in (3, 4):
                skore += 1.5
            if t.typ_tahu == "rosada":
                skore += 2.0

            # Simulace na kopii desky
            kopie = self.plocha.kopie()
            fig_kopie = kopie.vrat_obsah((t.vychozi_pozice[0], t.vychozi_pozice[1]))
            if fig_kopie:
                sim_tah = Tah(
                    t.vychozi_pozice,
                    t.cilova_pozice,
                    fig_kopie,
                    t.typ_tahu,
                    povyseni_na=t.povyseni_na,
                )
                kopie.posun_figurky(sim_tah)

                sim_revizor = RevizorTahu(kopie)
                sim_revizor.posledni_tah = sim_tah
                if sim_revizor.check_Sach(opacna):
                    skore += 2.0
                    if sim_revizor.check_Mat(opacna):
                        skore += 10000.0

                # Kontrola, zda soupeř může rovnou sebrat přesunutou figuru
                max_odpoved = 0.0
                for pt in sim_revizor.generuj_vsechny_legalni_tahy(opacna):
                    if pt.cilova_pozice == [cr, cc]:
                        hodnota = 9.0 if t.typ_tahu == "povyseni" else float(t.figurka.hodnota)
                        max_odpoved = max(max_odpoved, hodnota * 8.0)
                skore -= max_odpoved

            skore += random.uniform(0.0, 0.4)
            if skore > nejlepsi_skore:
                nejlepsi_skore = skore
                nejlepsi_tah = t

        return nejlepsi_tah

    def uloz_log(self) -> None:
        self.game_logger.vytvor_soubor("log_partie.txt")


# =====================================================================
# 4. VIEW — Tkinter Canvas & GUI Komponenty
# =====================================================================

class GameView:
    """Pohled na šachovnici (Tkinter Canvas)."""

    def __init__(self, root: tk.Widget, controller: "GameManagerController"):
        self.controller = controller
        self.canvas_size: int = 560
        self.sq_size: int = self.canvas_size // 8
        self.otocena: bool = False

        self.barva_svetle = "#f0d9b5"
        self.barva_tmave = "#b58863"
        self.barva_vyberu = "#bbcb2b"
        self.barva_posledni = "#d8d86b"
        self.barva_sach = "#ef4444"

        self.canvas = tk.Canvas(
            root,
            width=self.canvas_size,
            height=self.canvas_size,
            bg="#292524",
            highlightthickness=2,
            highlightbackground="#44403c",
        )
        self.canvas.pack(side=tk.LEFT, padx=10, pady=10)
        self.canvas.bind("<Button-1>", self.on_klik)

    def _na_obrazovku(self, r: int, c: int) -> Tuple[int, int]:
        return (7 - r, 7 - c) if self.otocena else (r, c)

    def _na_desku(self, sr: int, sc: int) -> Tuple[int, int]:
        return (7 - sr, 7 - sc) if self.otocena else (sr, sc)

    def on_klik(self, event: Any) -> None:
        sc = event.x // self.sq_size
        sr = event.y // self.sq_size
        if 0 <= sr < 8 and 0 <= sc < 8:
            r, c = self._na_desku(sr, sc)
            self.controller.zpracuj_klik(r, c)

    def aktualizuj_plochu(self) -> None:
        self.canvas.delete("all")
        gm = self.controller.game_manager
        deska = gm.plocha.herni_deska
        vybrano = self.controller.vybrana_pozice
        posledni_tah = gm.game_logger.tahy[-1] if gm.game_logger.tahy else None

        kral_v_sachu = None
        if gm.stav_hry in ("sach", "mat"):
            kral_v_sachu = gm.plocha.najdi_krale(gm.aktivni_hrac)

        sloupce_txt = ["a", "b", "c", "d", "e", "f", "g", "h"]

        for r in range(8):
            for c in range(8):
                sr, sc = self._na_obrazovku(r, c)
                x1, y1 = sc * self.sq_size, sr * self.sq_size
                x2, y2 = x1 + self.sq_size, y1 + self.sq_size

                barva = self.barva_svetle if (r + c) % 2 == 0 else self.barva_tmave

                if posledni_tah and (
                    posledni_tah.vychozi_pozice == [r, c] or posledni_tah.cilova_pozice == [r, c]
                ):
                    barva = self.barva_posledni

                if vybrano == (r, c):
                    barva = self.barva_vyberu

                if kral_v_sachu == (r, c):
                    barva = self.barva_sach

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=barva, outline="")

                # Souřadnice po okrajích
                if sc == 0:
                    t_barva = self.barva_tmave if (r + c) % 2 == 0 else self.barva_svetle
                    self.canvas.create_text(
                        x1 + 7, y1 + 10, text=str(8 - r), font=("Helvetica", 9, "bold"), fill=t_barva
                    )
                if sr == 7:
                    t_barva = self.barva_tmave if (r + c) % 2 == 0 else self.barva_svetle
                    self.canvas.create_text(
                        x2 - 8, y2 - 8, text=sloupce_txt[c], font=("Helvetica", 9, "bold"), fill=t_barva
                    )

                fig = deska[r][c]
                if fig:
                    cx = x1 + self.sq_size // 2
                    cy = y1 + self.sq_size // 2
                    hlavni = "#f8fafc" if fig.barva == 0 else "#111827"
                    obrys = "#1c1917" if fig.barva == 0 else "#cbd5e1"
                    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                        self.canvas.create_text(
                            cx + dx, cy + dy, text=fig.symbol, font=("Arial", 35), fill=obrys
                        )
                    self.canvas.create_text(
                        cx, cy, text=fig.symbol, font=("Arial", 35), fill=hlavni
                    )

        # Indikátory legálních tahů
        for t in self.controller.dostupne_tahy:
            cr, cc = t.cilova_pozice
            sr, sc = self._na_obrazovku(cr, cc)
            cx = sc * self.sq_size + self.sq_size // 2
            cy = sr * self.sq_size + self.sq_size // 2

            je_brani = t.vyhozena_figurka is not None or t.typ_tahu == "en_passant"
            if je_brani:
                self.canvas.create_oval(
                    cx - 25, cy - 25, cx + 25, cy + 25, outline="#ef4444", width=3
                )
            else:
                self.canvas.create_oval(
                    cx - 8, cy - 8, cx + 8, cy + 8, fill="#10b981", outline=""
                )


class HracView:
    """Karta hráče s časem, ELO a sebranými figurami."""

    def __init__(self, parent: tk.Widget, barva: int):
        self.barva = barva
        ikona = "♔" if barva == 0 else "♚"

        self.frame = tk.Frame(parent, bg="#1c1917", bd=1, relief=tk.SOLID, padx=10, pady=8)
        self.frame.pack(fill=tk.X, pady=4)

        top = tk.Frame(self.frame, bg="#1c1917")
        top.pack(fill=tk.X)

        self.lbl_ikona = tk.Label(top, text=ikona, font=("Arial", 14), bg="#1c1917", fg="#f59e0b")
        self.lbl_ikona.pack(side=tk.LEFT, padx=(0, 6))

        self.lbl_jmeno = tk.Label(
            top, text="Hráč", font=("Helvetica", 10, "bold"), bg="#1c1917", fg="#fafaf9"
        )
        self.lbl_jmeno.pack(side=tk.LEFT)

        self.lbl_elo = tk.Label(
            top, text="1200 ELO", font=("Helvetica", 9), bg="#1c1917", fg="#a8a29e"
        )
        self.lbl_elo.pack(side=tk.RIGHT)

        mid = tk.Frame(self.frame, bg="#1c1917")
        mid.pack(fill=tk.X, pady=(4, 0))

        self.lbl_stav = tk.Label(
            mid, text="Čeká", font=("Helvetica", 9), bg="#1c1917", fg="#78716c"
        )
        self.lbl_stav.pack(side=tk.LEFT)

        self.lbl_cas = tk.Label(
            mid, text="05:00", font=("Consolas", 13, "bold"), bg="#292524", fg="#38bdf8", padx=7, pady=1
        )
        self.lbl_cas.pack(side=tk.RIGHT)

        self.lbl_vyhozene = tk.Label(
            self.frame, text="", font=("Arial", 11), bg="#1c1917", fg="#d6d3d1", anchor="w"
        )
        self.lbl_vyhozene.pack(fill=tk.X, pady=(3, 0))

    def aktualizuj(self, hrac: Hrac, je_na_tahu: bool, cas_str: str, vyhozene: List[Figurka]) -> None:
        self.lbl_jmeno.config(text=hrac.uzivatel.jmeno)
        self.lbl_elo.config(text=f"{hrac.getEloRating()} ELO")
        self.lbl_cas.config(text=cas_str)

        sebrane_txt = " ".join(f.symbol for f in vyhozene) if vyhozene else "—"
        self.lbl_vyhozene.config(text=f"Sebrané: {sebrane_txt}")

        if je_na_tahu:
            bg = "#292524"
            self.frame.config(bg=bg, highlightbackground="#f59e0b", highlightthickness=1)
            self.lbl_stav.config(text="● NA TAHU", fg="#22c55e", bg=bg)
            self.lbl_cas.config(bg="#0c4a6e", fg="#38bdf8")
        else:
            bg = "#1c1917"
            self.frame.config(bg=bg, highlightbackground="#292524", highlightthickness=1)
            self.lbl_stav.config(text="Čeká", fg="#78716c", bg=bg)
            self.lbl_cas.config(bg="#292524", fg="#94a3b8")

        for w in (self.lbl_ikona, self.lbl_jmeno, self.lbl_elo, self.lbl_vyhozene):
            w.config(bg=bg)
        self.lbl_ikona.master.config(bg=bg)
        self.lbl_stav.master.config(bg=bg)


# =====================================================================
# 5. CONTROLLER — Koordinace událostí a herní smyčky
# =====================================================================

class GameManagerController:
    """Hlavní Controller propojující Model (GameManager) a Tkinter Views."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Šachy MVC (PyCharm / Tkinter)")
        self.root.geometry("980x670")
        self.root.minsize(920, 620)
        self.root.configure(bg="#0c0a09")

        self.rezim_bot: bool = True
        self.bot_premysli: bool = False
        self.vybrana_pozice: Optional[Tuple[int, int]] = None
        self.dostupne_tahy: List[Tah] = []

        self.game_manager = GameManager()
        self._nastav_hrace()
        self._vytvor_gui()
        self._aktualizuj_vse()
        self.root.after(1000, self._tik_casovace)

    def _nastav_hrace(self) -> None:
        u1 = Uzivatel("bily", "Hráč (Bílý)", "bily@sachy.cz", 1380)
        if self.rezim_bot:
            u2 = Uzivatel("bot", "Šachový Bot AI", "bot@sachy.cz", 1500)
        else:
            u2 = Uzivatel("cerny", "Hráč 2 (Černý)", "cerny@sachy.cz", 1420)
        self.game_manager.hraci = [Hrac(0, u1, False), Hrac(1, u2, self.rezim_bot)]

    def _vytvor_gui(self) -> None:
        board_container = tk.Frame(self.root, bg="#0c0a09")
        board_container.pack(side=tk.LEFT, padx=12, pady=12, fill=tk.BOTH)
        self.game_view = GameView(board_container, self)

        sidebar = tk.Frame(self.root, bg="#0c0a09", width=360)
        sidebar.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(0, 14), pady=14)

        # Hlavička stavu
        header = tk.Frame(sidebar, bg="#1c1917", padx=10, pady=8)
        header.pack(fill=tk.X, pady=(0, 4))

        tk.Label(
            header, text="ŠACHOVÁ PARTIE MVC", font=("Helvetica", 11, "bold"), fg="#f59e0b", bg="#1c1917"
        ).pack(anchor="w")
        self.lbl_stav_hry = tk.Label(
            header, text="Partie probíhá", font=("Helvetica", 10), fg="#a8a29e", bg="#1c1917"
        )
        self.lbl_stav_hry.pack(anchor="w")

        # Černý hráč (nahoře)
        self.view_cerny = HracView(sidebar, 1)

        # Zápis tahů
        hist_frame = tk.Frame(sidebar, bg="#1c1917", padx=8, pady=6)
        hist_frame.pack(fill=tk.BOTH, expand=True, pady=4)
        tk.Label(
            hist_frame, text="ZÁPIS TAHŮ", font=("Helvetica", 8, "bold"), fg="#78716c", bg="#1c1917"
        ).pack(anchor="w")
        self.txt_historie = tk.Text(
            hist_frame, height=6, bg="#0c0a09", fg="#e7e5e4", font=("Consolas", 9),
            relief=tk.FLAT, padx=6, pady=4, state=tk.DISABLED
        )
        self.txt_historie.pack(fill=tk.BOTH, expand=True, pady=(3, 0))

        # Kwesty
        kwest_frame = tk.Frame(sidebar, bg="#1c1917", padx=8, pady=6)
        kwest_frame.pack(fill=tk.X, pady=4)
        tk.Label(
            kwest_frame, text="ÚKOLY (KWESTY)", font=("Helvetica", 8, "bold"), fg="#78716c", bg="#1c1917"
        ).pack(anchor="w")
        self.lbl_kwesty = tk.Label(
            kwest_frame, text="", font=("Helvetica", 8), fg="#d6d3d1", bg="#1c1917", justify=tk.LEFT, anchor="w"
        )
        self.lbl_kwesty.pack(fill=tk.X, pady=(2, 0))

        # Bílý hráč (dole)
        self.view_bily = HracView(sidebar, 0)

        # Tlačítka ovládání
        btn_row1 = tk.Frame(sidebar, bg="#0c0a09")
        btn_row1.pack(fill=tk.X, pady=(6, 3))

        tk.Button(
            btn_row1, text="Nová hra", bg="#f59e0b", fg="#0c0a09",
            font=("Helvetica", 9, "bold"), relief=tk.FLAT, padx=8, pady=5, command=self.nova_hra
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        tk.Button(
            btn_row1, text="Zpět", bg="#292524", fg="#fafaf9",
            font=("Helvetica", 9), relief=tk.FLAT, padx=8, pady=5, command=self.vrat_tah
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=3)

        tk.Button(
            btn_row1, text="Otočit", bg="#292524", fg="#fafaf9",
            font=("Helvetica", 9), relief=tk.FLAT, padx=8, pady=5, command=self.otoc_desku
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

        btn_row2 = tk.Frame(sidebar, bg="#0c0a09")
        btn_row2.pack(fill=tk.X, pady=(3, 0))

        self.btn_rezim = tk.Button(
            btn_row2, text="Režim: vs Bot", bg="#1e293b", fg="#38bdf8",
            font=("Helvetica", 9, "bold"), relief=tk.FLAT, padx=8, pady=5, command=self.prepni_rezim
        )
        self.btn_rezim.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        tk.Button(
            btn_row2, text="Uložit log", bg="#292524", fg="#fafaf9",
            font=("Helvetica", 9), relief=tk.FLAT, padx=8, pady=5, command=self.uloz_log
        ).pack(side=tk.RIGHT, fill=tk.X, expand=True, padx=(3, 0))

    def _vyber_povyseni_dialog(self) -> Optional[str]:
        """Otevře modální dialog pro volbu figury při povýšení pěšce."""
        vyber: List[Optional[str]] = [None]
        dialog = tk.Toplevel(self.root)
        dialog.title("Povýšení pěšce")
        dialog.configure(bg="#1c1917")
        dialog.resizable(False, False)
        dialog.transient(self.root)
        dialog.grab_set()

        tk.Label(
            dialog, text="Vyber figuru pro povýšení:", font=("Helvetica", 10, "bold"),
            fg="#fafaf9", bg="#1c1917", padx=16, pady=10
        ).pack()

        frame = tk.Frame(dialog, bg="#1c1917", padx=14, pady=10)
        frame.pack()

        for nazev, ikona in [("Dáma", "♛"), ("Věž", "♜"), ("Střelec", "♝"), ("Kůň", "♞")]:
            def zvol(n: str = nazev) -> None:
                vyber[0] = n
                dialog.destroy()

            tk.Button(
                frame, text=f"{ikona}\n{nazev}", width=8, font=("Helvetica", 10, "bold"),
                bg="#292524", fg="#f59e0b", relief=tk.FLAT, pady=8, command=zvol
            ).pack(side=tk.LEFT, padx=4)

        self.root.wait_window(dialog)
        return vyber[0]

    def zpracuj_klik(self, radka: int, sloupec: int) -> None:
        if self.bot_premysli or self.game_manager.stav_hry in ("mat", "pat", "remiza", "cas"):
            return

        hrac = self.game_manager.hraci[self.game_manager.aktivni_hrac]
        if hrac.je_bot:
            return

        fig = self.game_manager.plocha.vrat_obsah((radka, sloupec))
        aktivni = self.game_manager.aktivni_hrac

        if self.vybrana_pozice is None:
            if fig and fig.barva == aktivni:
                self.vybrana_pozice = (radka, sloupec)
                self.dostupne_tahy = self.game_manager.mozne_tahy((radka, sloupec))
        else:
            vybrany_tah = next(
                (t for t in self.dostupne_tahy if t.cilova_pozice == [radka, sloupec]), None
            )
            if vybrany_tah:
                if vybrany_tah.typ_tahu == "povyseni" and not vybrany_tah.povyseni_na:
                    volba = self._vyber_povyseni_dialog()
                    if not volba:
                        return
                    vybrany_tah.povyseni_na = volba

                self._vykonej_tah(vybrany_tah)
                return
            elif fig and fig.barva == aktivni:
                if (radka, sloupec) == self.vybrana_pozice:
                    self.vybrana_pozice = None
                    self.dostupne_tahy = []
                else:
                    self.vybrana_pozice = (radka, sloupec)
                    self.dostupne_tahy = self.game_manager.mozne_tahy((radka, sloupec))
            else:
                self.vybrana_pozice = None
                self.dostupne_tahy = []

        self._aktualizuj_vse()

    def _vykonej_tah(self, tah: Tah) -> None:
        self.game_manager.proved_tah(tah)
        self.vybrana_pozice = None
        self.dostupne_tahy = []
        self._aktualizuj_vse()

        stav = self.game_manager.stav_hry
        if stav == "mat":
            vitez = "BÍLÝ" if self.game_manager.aktivni_hrac == 1 else "ČERNÝ"
            messagebox.showinfo("Šachmat!", f"Konec partie! Vítězí {vitez}.")
            return
        elif stav == "pat":
            messagebox.showinfo("Pat", "Remíza! Na šachovnici nastal pat.")
            return
        elif stav == "remiza":
            messagebox.showinfo("Remíza", "Remíza pro nedostatek materiálu.")
            return

        # Tah AI bota
        dalsi_hrac = self.game_manager.hraci[self.game_manager.aktivni_hrac]
        if dalsi_hrac.je_bot:
            self.bot_premysli = True
            self._aktualizuj_vse()
            self.root.after(400, self._tah_bota)

    def _tah_bota(self) -> None:
        self.bot_premysli = False
        if self.game_manager.stav_hry in ("mat", "pat", "remiza", "cas"):
            return
        tah_bota = self.game_manager.vypocitej_tah_bota()
        if tah_bota:
            self._vykonej_tah(tah_bota)
        else:
            self._aktualizuj_vse()

    def _tik_casovace(self) -> None:
        if self.game_manager.casovac.bezi and self.game_manager.stav_hry in ("hra", "sach"):
            aktivni = self.game_manager.aktivni_hrac
            self.game_manager.casovac.pocitej_cas(aktivni)
            if self.game_manager.casovac.cas_hrac[aktivni] <= 0:
                self.game_manager.casovac.bezi = False
                self.game_manager.stav_hry = "cas"
                self._aktualizuj_vse()
                prohral = "Bílý" if aktivni == 0 else "Černý"
                messagebox.showwarning("Čas vypršel", f"{prohral} prohrál na čas!")
            else:
                self._aktualizuj_hrace()
        self.root.after(1000, self._tik_casovace)

    def _aktualizuj_vse(self) -> None:
        self.game_view.aktualizuj_plochu()
        self._aktualizuj_hrace()

        stavy_text = {
            "hra": "Bot přemýšlí..." if self.bot_premysli else "Partie probíhá",
            "sach": "POZOR: ŠACH!",
            "mat": "KONEC HRY — ŠACHMAT",
            "pat": "KONEC HRY — PAT (REMÍZA)",
            "remiza": "KONEC HRY — REMÍZA",
            "cas": "KONEC HRY — VYPRŠEL ČAS",
        }
        barva_stavu = "#ef4444" if self.game_manager.stav_hry == "sach" else (
            "#f59e0b" if self.game_manager.stav_hry in ("mat", "cas") else "#a8a29e"
        )
        self.lbl_stav_hry.config(
            text=stavy_text.get(self.game_manager.stav_hry, "Hra"), fg=barva_stavu
        )

        # Historie tahů
        self.txt_historie.config(state=tk.NORMAL)
        self.txt_historie.delete("1.0", tk.END)
        tahy = self.game_manager.game_logger.tahy
        for i in range(0, len(tahy), 2):
            cislo = i // 2 + 1
            bily = tahy[i].notace()
            cerny = tahy[i + 1].notace() if (i + 1) < len(tahy) else ""
            self.txt_historie.insert(tk.END, f"{cislo:2d}. {bily:<9} {cerny}\n")
        self.txt_historie.see(tk.END)
        self.txt_historie.config(state=tk.DISABLED)

        # Kwesty
        kwest_lines = [
            f"[{'✓' if k.splneno else ' '}] {k.nazev} (+{k.odmena_elo} ELO)"
            for k in self.game_manager.kwesty
        ]
        self.lbl_kwesty.config(text="\n".join(kwest_lines))

    def _aktualizuj_hrace(self) -> None:
        gm = self.game_manager
        self.view_bily.aktualizuj(
            gm.hraci[0],
            gm.aktivni_hrac == 0 and gm.stav_hry in ("hra", "sach"),
            gm.casovac.formatuj_cas(0),
            gm.plocha.vyhozene_figurky_c,
        )
        self.view_cerny.aktualizuj(
            gm.hraci[1],
            gm.aktivni_hrac == 1 and gm.stav_hry in ("hra", "sach"),
            gm.casovac.formatuj_cas(1),
            gm.plocha.vyhozene_figurky_b,
        )

    def nova_hra(self) -> None:
        self.bot_premysli = False
        self.game_manager.plocha.nastav_zakladni_rozestaveni()
        self.game_manager.revizor_tahu.posledni_tah = None
        self.game_manager.aktivni_hrac = 0
        self.game_manager.stav_hry = "hra"
        self.game_manager.game_logger.tahy.clear()
        self.game_manager.casovac.nuluj_cas()
        self.vybrana_pozice = None
        self.dostupne_tahy.clear()
        self._nastav_hrace()
        self._aktualizuj_vse()

    def vrat_tah(self) -> None:
        if self.bot_premysli:
            return
        if self.game_manager.vrat_zpet():
            self.vybrana_pozice = None
            self.dostupne_tahy.clear()
            self._aktualizuj_vse()

    def otoc_desku(self) -> None:
        self.game_view.otocena = not self.game_view.otocena
        self.game_view.aktualizuj_plochu()

    def prepni_rezim(self) -> None:
        self.rezim_bot = not self.rezim_bot
        self.btn_rezim.config(text="Režim: vs Bot" if self.rezim_bot else "Režim: 2 Hráči")
        self.nova_hra()

    def uloz_log(self) -> None:
        self.game_manager.uloz_log()
        messagebox.showinfo("Export hotov", "Záznam partie byl uložen do log_partie.txt")


# =====================================================================
# SPUŠTĚNÍ APLIKACE
# =====================================================================

if __name__ == "__main__":
    okno = tk.Tk()
    app = GameManagerController(okno)
    okno.mainloop()