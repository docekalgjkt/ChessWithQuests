class GameManager:
    def __init__(self):
        self.plocha: HerniPlocha = HerniPlocha()
        self.revizor_tahu: RevizorTahu = RevizorTahu(self.plocha)
        self.casovac: Timer = Timer()
        self.game_logger: GameLogger = GameLogger("log.txt")
        self.aktivni_hrac: int = 0
        self.hraci: List[Hrac] = []
        self.aktualni_tah: Optional[Tah] = None

    def zacni_tah(self) -> Optional[Tah]:
        return self.aktualni_tah

    def proved_tah(self, tah: Tah) -> bool:
        self.plocha.posun_figurky(tah)
        self.game_logger.uloz_tah(tah)
        self.aktivni_hrac = 1 if self.aktivni_hrac == 0 else 0
        return True