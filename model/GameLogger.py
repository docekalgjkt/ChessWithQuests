class GameLogger:
    def __init__(self, soubor: str = "log.txt"):
        self.soubor: str = soubor
        self.zaznamy: List[Tah] = []

    def uloz_tah(self, tah: Tah):
        self.zaznamy.append(tah)