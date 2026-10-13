class Tah:
    def __init__(self, vychozi_pozice: Pozice, cilova_pozice: Pozice, figurka: Figurka,
                 typ_tahu: str = "normal", figurka_brana: Optional[Figurka] = None):
        self.vychozi_pozice: Pozice = vychozi_pozice
        self.cilova_pozice: Pozice = cilova_pozice
        self.figurka: Figurka = figurka
        self.figurka_brana: Optional[Figurka] = figurka_brana
        self.typ_tahu: str = typ_tahu
        self.sach: bool = False
        self.mat: bool = False
        self.notation: str = self._generuj_notaci()

    def _generuj_notaci(self) -> str:
        sloupce = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
        radky = ['8', '7', '6', '5', '4', '3', '2', '1']
        prefix = "" if self.figurka.nazev == "Pěšák" else self.figurka.symbol
        cil = f"{sloupce[self.cilova_pozice.sloupec]}{radky[self.cilova_pozice.radka]}"
        brani = "x" if self.figurka_brana else ""
        return f"{prefix}{brani}{cil}"

    def over_platnost(self) -> bool:
        return True