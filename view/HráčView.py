class HracView:
    def __init__(self, parent: tk.Widget, controller: 'GameManagerController'):
        self.controller = controller
        self.frame = tk.Frame(parent, bg="#1e293b", padx=10, pady=10)
        self.frame.pack(side=tk.TOP, fill=tk.X, pady=5)

        self.label_info = tk.Label(self.frame, text="Hráč", font=("Arial", 12, "bold"), fg="#f8fafc", bg="#1e293b")
        self.label_info.pack(anchor="w")

    def aktualizuj_hrace(self, hrac: Hrac, je_na_tahu: bool):
        stav = "NA TAHU" if je_na_tahu else "Čeká"
        barva_str = "Bílý" if hrac.barva == 0 else "Černý"
        self.label_info.config(
            text=f"{barva_str}: {hrac.uzivatel.jmeno} ({hrac.getEloRating()} ELO) [{stav}]"
        )