class Timer:
    def __init__(self, vychozi_sekundy: int = 300):
        self.cas_hrac: List[int] = [vychozi_sekundy, vychozi_sekundy]
        self.bezi: bool = False

    def nuluj_cas(self):
        self.cas_hrac = [300, 300]
        self.bezi = False

    def pocitej_cas(self, hrac: int):
        if self.bezi and self.cas_hrac[hrac] > 0:
            self.cas_hrac[hrac] -= 1