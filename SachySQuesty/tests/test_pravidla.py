# -*- coding: utf-8 -*-
"""Testy šachových pravidel (spuštění: python -m unittest discover tests).

Perft = počet všech pozic po N tazích. Hodnoty jsou známé z šachového programování
(https://www.chessprogramming.org/Perft_Results), takže odhalí chyby v rošádě,
braní mimochodem, proměně i v kontrole šachu.
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from models.figurky import VlastniFigurka, vytvor_figurku  # noqa: E402
from models.game_manager import GameManager  # noqa: E402
from models.herni_plocha import HerniPlocha  # noqa: E402
from models.hrac import Hrac  # noqa: E402
from models.revizor_tahu import RevizorTahu  # noqa: E402
from models.timer import Timer  # noqa: E402
from users.user_manager import UserManager  # noqa: E402
from utils.game_logger import GameLogger  # noqa: E402
from utils.konstanty import BILA, CERNA  # noqa: E402

FEN_NAZVY = {"k": "Král", "q": "Dáma", "r": "Věž", "b": "Střelec", "n": "Kůň", "p": "Pěšák"}


def nacti_fen(fen: str):
    """Vrátí (plocha, barva na tahu) z FEN zápisu (jen 8×8)."""
    casti = fen.split()
    plocha = HerniPlocha((8, 8))
    for r, rada in enumerate(casti[0].split("/")):
        c = 0
        for znak in rada:
            if znak.isdigit():
                c += int(znak)
                continue
            barva = BILA if znak.isupper() else CERNA
            figurka = vytvor_figurku(FEN_NAZVY[znak.lower()], barva)
            if figurka.nazev == "Pěšák":
                figurka.pohnuto = r != (6 if barva == BILA else 1)
            else:
                figurka.pohnuto = True
            plocha.herni_deska[r][c] = figurka
            c += 1
    rosady = casti[2] if len(casti) > 2 else "-"
    for znak, kral, vez in (("K", (7, 4), (7, 7)), ("Q", (7, 4), (7, 0)), ("k", (0, 4), (0, 7)), ("q", (0, 4), (0, 0))):
        if znak in rosady:
            plocha.vrat_obsah(kral).pohnuto = False
            plocha.vrat_obsah(vez).pohnuto = False
    if len(casti) > 3 and casti[3] != "-":
        c = ord(casti[3][0]) - ord("a")
        r = 8 - int(casti[3][1])
        pesak = (r + 1, c) if r == 2 else (r - 1, c)
        plocha.en_passant = ((r, c), pesak)
    return plocha, (BILA if casti[1] == "w" else CERNA)


def perft(plocha: HerniPlocha, barva: int, hloubka: int) -> int:
    revizor = RevizorTahu(plocha)
    tahy = revizor.vsechny_tahy(barva)
    if hloubka == 1:
        return sum(4 if t.promena else 1 for t in tahy)
    celkem = 0
    for tah in tahy:
        for promena in (("Dáma", "Věž", "Střelec", "Kůň") if tah.promena else (None,)):
            kopie = plocha.kopie()
            tah.promena_na = promena
            kopie.proved_tah(tah)
            celkem += perft(kopie, -barva, hloubka - 1)
    return celkem


def novy_gm(plocha=None):
    if plocha is None:
        plocha = HerniPlocha()
        plocha.standardni_rozestaveni()
    hraci = [Hrac(BILA, UserManager.vytvor_hosta("A")), Hrac(CERNA, UserManager.vytvor_hosta("B"))]
    return GameManager(plocha, hraci, Timer(), GameLogger(Path(tempfile.mkdtemp())))


class TestPerft(unittest.TestCase):
    def test_zakladni_pozice(self):
        plocha = HerniPlocha()
        plocha.standardni_rozestaveni()
        self.assertEqual(perft(plocha, BILA, 1), 20)
        self.assertEqual(perft(plocha, BILA, 2), 400)
        self.assertEqual(perft(plocha, BILA, 3), 8902)

    def test_kiwipete(self):  # rošády, en passant, vazby
        plocha, barva = nacti_fen("r3k2r/p1ppqpb1/bn2pnp1/3PN3/1p2P3/2N2Q1p/PPPBBPPP/R3K2R w KQkq -")
        self.assertEqual(perft(plocha, barva, 1), 48)
        self.assertEqual(perft(plocha, barva, 2), 2039)

    def test_pozice3(self):  # en passant a odkryté šachy
        plocha, barva = nacti_fen("8/2p5/3p4/KP5r/1R3p1k/8/4P1P1/8 w - -")
        self.assertEqual(perft(plocha, barva, 1), 14)
        self.assertEqual(perft(plocha, barva, 2), 191)
        self.assertEqual(perft(plocha, barva, 3), 2812)

    def test_pozice4(self):  # proměny a rošády
        plocha, barva = nacti_fen("r3k2r/Pppp1ppp/1b3nbN/nP6/BBP1P3/q4N2/Pp1P2PP/R2Q1RK1 w kq - 0 1")
        self.assertEqual(perft(plocha, barva, 1), 6)
        self.assertEqual(perft(plocha, barva, 2), 264)
        self.assertEqual(perft(plocha, barva, 3), 9467)


class TestGameManager(unittest.TestCase):
    def tahni(self, gm, z, na, promena=None):
        self.assertTrue(gm.je_vlastni_figurka(z), f"{z} není figurka hráče na tahu")
        gm.vrat_mozne_tahy(z)
        self.assertTrue(gm.proved_tah(na, promena), f"tah {z}->{na} se neprovedl")

    def test_mat_naivni(self):  # f3 e5 g4 Dh4#
        gm = novy_gm()
        self.tahni(gm, (6, 5), (5, 5))
        self.tahni(gm, (1, 4), (3, 4))
        self.tahni(gm, (6, 6), (4, 6))
        self.tahni(gm, (0, 3), (4, 7))
        self.assertEqual(gm.get_stav(), GameManager.MAT)
        self.assertEqual(gm.vitez, CERNA)
        self.assertEqual(gm.notace_historie[-1], "Dd8-h4#")
        self.assertEqual(gm.vysledek_pgn(), "0-1")

    def test_neplatny_tah_a_vraceni(self):
        gm = novy_gm()
        gm.vrat_mozne_tahy((6, 4))
        self.assertFalse(gm.proved_tah((3, 4)))          # pěšák o tři pole nesmí
        self.tahni(gm, (6, 4), (4, 4))
        self.assertEqual(gm.barva_na_tahu, CERNA)
        gm.zrus_tah()
        self.assertEqual(gm.barva_na_tahu, BILA)
        self.assertIsNotNone(gm.herni_plocha.vrat_obsah((6, 4)))
        self.assertEqual(gm.notace_historie, [])

    def test_pat(self):
        plocha, _ = nacti_fen("7k/5Q2/6K1/8/8/8/8/8 w - -")
        gm = novy_gm(plocha)
        self.tahni(gm, (1, 5), (1, 6))                   # Df7-g7# (dámu kryje král)
        self.assertEqual(gm.get_stav(), GameManager.MAT)
        plocha, _ = nacti_fen("7k/8/6K1/8/8/8/8/5Q2 w - -")
        gm = novy_gm(plocha)
        self.tahni(gm, (7, 5), (1, 5))                   # Df1-f7 = pat
        self.assertEqual(gm.get_stav(), GameManager.PAT)

    def test_promena_a_rosada_notace(self):
        plocha, _ = nacti_fen("8/P7/8/8/8/8/8/R3K2k w Q -")
        gm = novy_gm(plocha)
        gm.vrat_mozne_tahy((7, 4))
        self.assertIn((7, 2), [t.cilova_pozice for t in gm.mozne_tahy_figurky])   # velká rošáda
        self.tahni(gm, (7, 4), (7, 2))
        self.assertEqual(gm.notace_historie[-1], "O-O-O+")      # věž na d1 dává šach
        self.assertEqual(gm.herni_plocha.vrat_obsah((7, 3)).nazev, "Věž")
        self.tahni(gm, (7, 7), (6, 7))
        self.tahni(gm, (1, 0), (0, 0), "Kůň")
        self.assertEqual(gm.herni_plocha.vrat_obsah((0, 0)).nazev, "Kůň")
        self.assertEqual(gm.notace_historie[-1], "a7-a8=J")

    def test_ruzne_velikosti(self):
        for r in range(5, 13):
            for c in range(5, 13):
                plocha = HerniPlocha((r, c))
                plocha.standardni_rozestaveni()
                self.assertIsNone(plocha.over_rozestaveni())
                gm = novy_gm(plocha)
                self.assertGreater(len(gm.mozne_tahy()), 0)

    def test_vlastni_figurka_a_ulozeni(self):
        definice = {"nazev": "Kancléř", "symbol": "C", "skok": False, "max_kroku": 0,
                    "vektory": [[-1, 0], [1, 0], [0, -1], [0, 1]],
                    "vektory_utoku": [[-1, 0], [1, 0], [0, -1], [0, 1]],
                    "vektory_skoku": [[-2, -1], [-2, 1], [-1, -2], [-1, 2], [1, -2], [1, 2], [2, -1], [2, 1]]}
        plocha = HerniPlocha()
        plocha.nastav_obsah((7, 4), vytvor_figurku("Král", BILA))
        plocha.nastav_obsah((0, 0), vytvor_figurku("Král", CERNA))
        plocha.nastav_obsah((4, 4), VlastniFigurka(definice, BILA))
        gm = novy_gm(plocha)
        tahy = gm.vrat_mozne_tahy((4, 4))
        # věž: 7 vodorovně + 4 nahoru + 2 dolů (vlastní král v cestě) ; kůň: 8 skoků
        self.assertEqual(len(tahy), 7 + 4 + 2 + 8)
        kopie = HerniPlocha.ze_slovniku(plocha.do_slovniku())
        self.assertEqual(kopie.vrat_obsah((4, 4)).nazev, "Kancléř")
        self.assertEqual(len(RevizorTahu(kopie).mozne_tahy(kopie.vrat_obsah((4, 4)), (4, 4))), 21)


if __name__ == "__main__":
    unittest.main()
