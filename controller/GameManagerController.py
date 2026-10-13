class GameManagerController:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.game_manager: GameManager = GameManager()
        self.herni_plocha: HerniPlocha = self.game_manager.plocha
        self.vybrane_pole: Optional[Pozice] = None
        self.mozne_tahy: List[Tah] = []

        # Inicializace hráčů
        hrac1 = Hrac(0, Uzivatel("bily_jezdec", "Jan Novák", "jan@sachy.cz", 1350))
        hrac2 = Hrac(1, Uzivatel("cerny_kral", "Petr Dvořák", "petr@sachy.cz", 1420))
        self.game_manager.hraci = [hrac1, hrac2]

        # Vytvoření postranního panelu
        sidebar = tk.Frame(root, bg="#0f172a", width=250)
        sidebar.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=15)

        self.hrac_view_cerny = HracView(sidebar, self)
        self.hrac_view_bily = HracView(sidebar, self)
        self.game_view: GameView = GameView(root, self)

        # Aktualizace GUI
        self.start_game()

    def start_game(self):
        self.game_view.aktualizuj_plochu()
        self.aktualizuj_views()

    def aktualizuj_views(self):
        self.hrac_view_bily.aktualizuj_hrace(self.game_manager.hraci[0], self.game_manager.aktivni_hrac == 0)
        self.hrac_view_cerny.aktualizuj_hrace(self.game_manager.hraci[1], self.game_manager.aktivni_hrac == 1)

    def vyber_pole(self, souradnice: Pozice):
        fig = self.herni_plocha.vrat_obsah(souradnice)

        # 1. Žádné pole není vybráno
        if not self.vybrane_pole:
            if fig and fig.barva == self.game_manager.aktivni_hrac:
                self.vybrane_pole = souradnice
                self.mozne_tahy = self.game_manager.revizor_tahu.get_mozne_tahy(fig)
        else:
            # 2. Klik na cíl pro provedení tahu
            vybrany_tah = next((t for t in self.mozne_tahy if t.cilova_pozice == souradnice), None)
            if vybrany_tah:
                self.game_manager.proved_tah(vybrany_tah)
                self.vybrane_pole = None
                self.mozne_tahy = []
            elif fig and fig.barva == self.game_manager.aktivni_hrac:
                # Změna výběru na jinou vlastní figuru
                self.vybrane_pole = souradnice
                self.mozne_tahy = self.game_manager.revizor_tahu.get_mozne_tahy(fig)
            else:
                self.vybrane_pole = None
                self.mozne_tahy = []

        self.game_view.aktualizuj_plochu()
        self.aktualizuj_views()

if __name__ == "__main__":
    okno = tk.Tk()
    okno.title("Šachy MVC - Grafické uživatelské rozhraní Tkinter")
    okno.configure(bg="#0f172a")
    app = GameManagerController(okno)
    okno.mainloop()