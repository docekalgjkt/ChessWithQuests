class Tah:
    def __init__(self, vychozi_pozice, cilova_pozice, figurka, typ_tahu):
        self.vychozi_pozice = vychozi_pozice
        self.cilova_pozice = cilova_pozice
        self.figurka = figurka
        self.typ_tahu = typ_tahu

    def over_platnost(self):
        for pozice in [self.vychozi_pozice, self.cilova_pozice]:
            for souradnice in pozice:
                if not (0 <= souradnice < 8):
                    return False
        return True

    def proved_tah(self):
        self.figurka.pozice = self.cilova_pozice
        print(f"Tah proveden: {self.vychozi_pozice} -> {self.cilova_pozice}")

    def __str__(self):
        return f"Tah: {self.vychozi_pozice} -> {self.cilova_pozice} ({self.figurka})"