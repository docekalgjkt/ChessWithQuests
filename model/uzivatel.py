class Uzivatel:
    def __init__(self, uzivatelske_jmeno, jmeno, email, elo):
        self.uzivatelske_jmeno = uzivatelske_jmeno
        self.jmeno = jmeno
        self.email = email
        self.elo = elo
        self.splnene_kvesty = []

    def pridej_kwest(self, kwest):
        self.splnene_kvesty.append(kwest)

    def __str__(self):
        return f"Uzivatel: {self.uzivatelske_jmeno}, ELO: {self.elo}"