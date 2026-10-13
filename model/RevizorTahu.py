class RevizorTahu:
    def __init__(self, herni_plocha: HerniPlocha):
        self.herni_plocha: HerniPlocha = herni_plocha

    def check_Sach(self, barva: int) -> bool:
        kral = self.herni_plocha.najdi_krale(barva)
        if not kral:
            return False
        opacna = 1 if barva == 0 else 0
        for r in range(8):
            for c in range(8):
                f = self.herni_plocha.herni_deska[r][c]
                if f and f.barva == opacna:
                    if self.muze_ohrozit(f, kral.pozice):
                        return True
        return False

    def muze_ohrozit(self, f: Figurka, cil: Pozice) -> bool:
        dR = cil.radka - f.pozice.radka
        dS = cil.sloupec - f.pozice.sloupec
        if f.nazev == "Kůň":
            return [dR, dS] in f.vektory
        if f.nazev == "Král":
            return max(abs(dR), abs(dS)) == 1
        if f.nazev == "Pěšák":
            pesak = f # type: ignore
            return dR == pesak.smer and abs(dS) == 1
        # Pro Střelce, Věž, Dámu paprsky
        absR, absS = abs(dR), abs(dS)
        je_diag = (absR == absS)
        je_orto = (dR == 0 or dS == 0)
        if f.nazev == "Střelec" and not je_diag: return False
        if f.nazev == "Věž" and not je_orto: return False
        if f.nazev == "Dáma" and not (je_diag or je_orto): return False

        stepR = 0 if dR == 0 else int(dR / absR)
        stepS = 0 if dS == 0 else int(dS / (1 if absS == 0 else absS))
        cR, cS = f.pozice.radka + stepR, f.pozice.sloupec + stepS
        while (cR, cS) != (cil.radka, cil.sloupec):
            if self.herni_plocha.vrat_obsah(Pozice(cR, cS)) is not None:
                return False
            cR += stepR
            cS += stepS
        return True

    def get_mozne_tahy(self, f: Figurka) -> List[Tah]:
        mozne = []
        for r in range(8):
            for c in range(8):
                cil = Pozice(r, c)
                obsah = self.herni_plocha.vrat_obsah(cil)
                if obsah and obsah.barva == f.barva:
                    continue
                # Validace pohybu
                if f.nazev == "Pěšák":
                    pesak = f # type: ignore
                    dR = r - f.pozice.radka
                    dS = c - f.pozice.sloupec
                    if dS == 0 and dR == pesak.smer and not obsah:
                        mozne.append(Tah(f.pozice, cil, f))
                    elif dS == 0 and dR == pesak.smer * 2 and f.pocet_tahu == 0 and not obsah:
                        mezilehle = self.herni_plocha.vrat_obsah(Pozice(f.pozice.radka + pesak.smer, c))
                        if not mezilehle:
                            mozne.append(Tah(f.pozice, cil, f))
                    elif abs(dS) == 1 and dR == pesak.smer and obsah and obsah.barva != f.barva:
                        mozne.append(Tah(f.pozice, cil, f, "brani", obsah))
                else:
                    if self.muze_ohrozit(f, cil):
                        mozne.append(Tah(f.pozice, cil, f, "brani" if obsah else "normal", obsah))
        return mozne