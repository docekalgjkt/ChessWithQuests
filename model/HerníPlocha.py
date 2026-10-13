class HerniPlocha:
    def __init__(self):
        self.rozmery: Tuple[int, int] = (8, 8)
        self.herni_deska: List[List[Optional[Figurka]]] = [[None for _ in range(8)] for _ in range(8)]
        self.vyhozene_figurky_b: List[Figurka] = []
        self.vyhozene_figurky_c: List[Figurka] = []
        self.nastav_zakladni_rozestaveni()

    def nastav_zakladni_rozestaveni(self):
        cerne = [Vez, Kun, Strelec, Dama, Kral, Strelec, Kun, Vez]
        for c in range(8):
            self.herni_deska[0][c] = cerne[c](1, Pozice(0, c))
            self.herni_deska[1][c] = Pesak(1, Pozice(1, c))

        bile = [Vez, Kun, Strelec, Dama, Kral, Strelec, Kun, Vez]
        for c in range(8):
            self.herni_deska[6][c] = Pesak(0, Pozice(6, c))
            self.herni_deska[7][c] = bile[c](0, Pozice(7, c))

    def vrat_obsah(self, souradnice: Pozice) -> Optional[Figurka]:
        if 0 <= souradnice.radka < 8 and 0 <= souradnice.sloupec < 8:
            return self.herni_deska[souradnice.radka][souradnice.sloupec]
        return None

    def posun_figurky(self, tah: Tah) -> bool:
        cil_fig = self.vrat_obsah(tah.cilova_pozice)
        if cil_fig:
            cil_fig.aktivni = False
            if cil_fig.barva == 0:
                self.vyhozene_figurky_b.append(cil_fig)
            else:
                self.vyhozene_figurky_c.append(cil_fig)

        self.herni_deska[tah.vychozi_pozice.radka][tah.vychozi_pozice.sloupec] = None
        tah.figurka.pozice = tah.cilova_pozice
        tah.figurka.pocet_tahu += 1
        self.herni_deska[tah.cilova_pozice.radka][tah.cilova_pozice.sloupec] = tah.figurka
        return True

    def najdi_krale(self, barva: int) -> Optional[Figurka]:
        for r in range(8):
            for c in range(8):
                f = self.herni_deska[r][c]
                if f and f.nazev == "Král" and f.barva == barva:
                    return f
        return None