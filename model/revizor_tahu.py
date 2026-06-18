class RevizorTahu:
    def __init__(self, herni_plocha, tah):
        self.herni_plocha = herni_plocha
        self.tah = tah                      # tah ke kontrole

    def simuluj_move(self):
        mozne = []
        figurka = self.tah.figurka
        if figurka is None:
            return mozne
        for vektor in figurka.vektory:
            novy_radek = figurka.pozice[0] + vektor[0]
            novy_sloupec = figurka.pozice[1] + vektor[1]
            if 0 <= novy_radek < 8 and 0 <= novy_sloupec < 8:
                mozne.append([novy_radek, novy_sloupec])
        return mozne

    def check_sach(self):
        return False

    def check_mat(self):
        return False

    def check_pat(self):
        return False