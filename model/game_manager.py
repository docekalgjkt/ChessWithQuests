from game_logger import GameLogger
from game_timer import GameTimer

class GameManager:
    def __init__(self, plocha, hrac1, hrac2, game_logger, revizor_tahu):
        self.plocha = plocha
        self.aktivni_hrac = 0
        self.hraci = [hrac1, hrac2]
        self.aktualni_tah = None
        self.casovac = None
        self.game_logger = game_logger
        self.revizor_tahu = revizor_tahu

    def proved_tah(self):
        if self.aktualni_tah and self.aktualni_tah.over_platnost():
            self.aktualni_tah.proved_tah()
            self.game_logger.uloz_tah(self.aktualni_tah)
            return True
        return False

    def zacni_tah(self):
        mozne = []
        if self.revizor_tahu:
            mozne = self.revizor_tahu.simuluj_move()
        return mozne

    def mozne_tahy(self, tah):
        self.aktualni_tah = tah

    def zrus_tah(self):
        self.aktualni_tah = None

    def uloz_log(self):
        print("Log hry uložen.")

    def get_stav(self):
        return 0

    def najdi_uzivatele(self, id_uzivatele):
        for hrac in self.hraci:
            if hrac.uzivatel.id_uzivatele == id_uzivatele:
                return hrac.uzivatel
        return None

    def __str__(self):
        return f"GameManager – aktivní hráč: {self.aktivni_hrac}"