from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Any


# ==========================================
# 2. VIEW (Vykreslování a vstupy)
# ==========================================

class KonzoleView:
    def vykresli_plochu(self, plocha: HernaPlocha):
        print("\n    a b c d e f g h")
        print("  +-----------------+")
        for r in range(8):
            radek_str = f"{8 - r} | "
            for c in range(8):
                fig = plocha.vrat_obsah(r, c)
                radek_str += f"{str(fig) if fig else '.'} "
            radek_str += f"| {8 - r}"
            print(radek_str)
        print("  +-----------------+")
        print("    a b c d e f g h\n")

    def ziskej_tah(self, jmeno_hrace: str, barva: str) -> Tuple[Tuple[int, int], Tuple[int, int]]:
        while True:
            vstup = input(f"[{barva}] Hráč {jmeno_hrace}, zadejte tah (např. 'e2 e4') nebo 'konec': ").strip().lower()
            if vstup == 'konec':
                return None, None

            casti = vstup.split()
            if len(casti) != 2:
                print("Chyba: Zadejte tah ve formátu 'odkud kam' (např. e2 e4).")
                continue

            try:
                odkud = self._prevod_souradnic(casti[0])
                kam = self._prevod_souradnic(casti[1])
                return odkud, kam
            except (ValueError, IndexError):
                print("Chyba: Neplatné souřadnice. Používejte a-h pro sloupce a 1-8 pro řádky.")

    def _prevod_souradnic(self, text: str) -> Tuple[int, int]:
        sloupec = ord(text[0]) - ord('a')
        radek = 8 - int(text[1])
        if not (0 <= sloupec <= 7 and 0 <= radek <= 7):
            raise ValueError
        return radek, sloupec

    def zobraz_zpravu(self, zprava: str):
        print(f"\n--- {zprava} ---")