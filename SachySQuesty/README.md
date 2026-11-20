# ŠachySQuesty

Desktopové šachy v Pythonu (tkinter). Za splněné úkoly a achievementy dostává hráč XP a body.
Hra umí vlastní figurky, libovolnou velikost plochy (5×5 až 12×12), čas na hru i na tah,
libovolné počáteční rozestavení a hru hotseat i po LAN. Eviduje ELO, úspěšnost a XP hráčů.

## Spuštění
1. Python 3.9 nebo novější (tkinter je součástí instalace z python.org; na Linuxu `sudo apt install python3-tk`).
2. V PyCharmu otevři složku `SachySQuesty` jako projekt a spusť `main.py`, nebo v terminálu:
   ```
   python main.py
   ```
Nepotřebuje žádné další knihovny. Datové soubory (profily, questy, nastavení, logy) se vytvoří samy při prvním spuštění.

## Struktura (MVC)
| Složka | Vrstva | Obsah |
|---|---|---|
| `models/` | Model | `Figurka` + `Kůň, Král, Dáma, Věž, Pěšák, Střelec, VlastniFigurka`, `Tah`, `HerniPlocha`, `RevizorTahu`, `Timer`, `Hrac`, `GameManager`, `Quest`, `QuestManager` |
| `users/` | Model | `Uzivatel`, `UserManager` (profily, ELO, historie partií) |
| `custom_pieces/` | Model | `SpravceSetu` – sady vlastních figurek (`sady/*.json`) |
| `views/` | View | `HlavniOkno`, `Obrazovka` a všechny obrazovky, `HerniDeskaView`, `HracGameView`, `DialogView` |
| `controllers/` | Controller | `AppController`, `GameManagerController`, `ProfilController`, `NastaveniController` |
| `utils/` | pomocné | `GameLogger`, `ExportWriter` / `MetadataWriter` / `ChessNotationWriter` (PGN, FEN), `LanSpojeni`, `Konfigurace`, konstanty |
| `docs/` | | class diagram GUI vrstvy (`.drawio` + PDF) |
| `tests/` | | testy pravidel (`python -m unittest discover tests`) |

View nikdy nesahá na Model – data mu předává Controller. Controller zpracovává události
(kliknutí na desku, tlačítka, časovač `after()`, zprávy z LAN) a volá Model.

## Funkce podle use case diagramu
- **Spustit hru / Zahájit partii** – menu *Nová hra*: režim, hráči (profil nebo Host), rozměry plochy, čas na hru a na tah.
- **Vytvoření herní plochy** – v nastavení partie se dají figurky (i vlastní) pokládat levým tlačítkem a odebírat pravým.
- **Proveď tah / Vyhodnocení tahu** – kliknutí na figurku ukáže možné tahy; hlídá se šach, mat, pat, rošáda, braní mimochodem, proměna pěšáka.
- **Vyhodnocení ELO** – po konci partie (K = 32) u hráčů s profilem.
- **Timer** – čas na celou hru i na jeden tah; po vypršení hráč prohrává.
- **Uložit hru** – uloží `.json` (lze znovu načíst), `.pgn` (zápis tahů) a `.meta.txt`; každá partie se navíc průběžně loguje do `logs/`.
- **Profil, Úkoly/Achievementy** – statistiky, historie partií, splněné úkoly.
- **Upravit log kwestů** – menu *Log questů*: přidat, upravit, vypnout nebo smazat úkol.
- **Nastavení vzhledu** – motiv desky, velikost polí, souřadnice, nápověda tahů.
- **Graf. upravení setu** – menu *Editor figurek*: vlastní figurka se navrhne klikáním do mřížky (pohyb, braní, skok).

## Hra po LAN
1. Oba počítače musí být ve stejné síti (port 50007, případně ho povol ve firewallu).
2. Hostitel zvolí *LAN – založit hru* a klikne na *Zahájit partii*. Zobrazí se jeho IP adresa.
3. Druhý hráč zvolí *LAN – připojit se*, zadá tuto IP a klikne na *Zahájit partii*.
4. Plochu, rozestavení i čas určuje hostitel (hraje bílými). Pro vyzkoušení na jednom PC použij IP `127.0.0.1` a spusť aplikaci dvakrát.
