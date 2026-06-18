class GameLogger:
    def __init__(self, soubor):
        self.soubor = soubor

    def uloz_tah(self, tah):
        with open(self.soubor, "a", encoding="utf-8") as f:
            f.write(str(tah) + "\n")
        print(f"Tah uložen do {self.soubor}")

    def vytvor_soubor(self, nazev):
        self.soubor = nazev
        with open(self.soubor, "w", encoding="utf-8") as f:
            f.write("")
        print(f"Soubor {self.soubor} vytvořen.")