from metadata_writer import MetadataWriter

class ChessNotationWriter(MetadataWriter):
    def __init__(self, format_notace):
        super().__init__()
        self.format_notace = format_notace
        self.zaznam_hry = []

    def method(self, typ):
        print(f"Zápis notace formátu {self.format_notace}: {typ}")

    def pridej_tah(self, tah):
        self.zaznam_hry.append(str(tah))

    def __str__(self):
        return f"ChessNotationWriter ({self.format_notace})"