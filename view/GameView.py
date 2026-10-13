class GameView:
    def __init__(self, root: tk.Tk, controller: 'GameManagerController'):
        self.root = root
        self.controller = controller
        self.canvas_size = 520
        self.sq_size = self.canvas_size // 8

        # Plátno šachovnice (Tkinter Canvas)
        self.canvas = tk.Canvas(root, width=self.canvas_size, height=self.canvas_size, bg="#b58863")
        self.canvas.pack(side=tk.LEFT, padx=15, pady=15)
        self.canvas.bind("<Button-1>", self.on_click)

    def aktualizuj_plochu(self):
        self.canvas.delete("all")
        colors = ["#f0d9b5", "#b58863"]

        # Vykreslení 64 polí
        for r in range(8):
            for c in range(8):
                x1, y1 = c * self.sq_size, r * self.sq_size
                x2, y2 = x1 + self.sq_size, y1 + self.sq_size
                color = colors[(r + c) % 2]

                # Zvýraznění vybraného pole
                if self.controller.vybrane_pole and self.controller.vybrane_pole.to_tuple() == (r, c):
                    color = "#bbcb2b"

                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")

                # Vykreslení figurky
                fig = self.controller.herni_plocha.vrat_obsah(Pozice(r, c))
                if fig:
                    text_color = "#111827" if fig.barva == 1 else "#f8fafc"
                    self.canvas.create_text(
                        x1 + self.sq_size // 2, y1 + self.sq_size // 2,
                        text=fig.symbol, font=("Arial", 32, "bold"), fill=text_color
                    )

        # Vykreslení teček pro legální tahy
        for t in self.controller.mozne_tahy:
            cx = t.cilova_pozice.sloupec * self.sq_size + self.sq_size // 2
            cy = t.cilova_pozice.radka * self.sq_size + self.sq_size // 2
            self.canvas.create_oval(cx - 7, cy - 7, cx + 7, cy + 7, fill="#10b981", outline="")

    def on_click(self, event):
        col = event.x // self.sq_size
        row = event.y // self.sq_size
        self.controller.vyber_pole(Pozice(row, col))