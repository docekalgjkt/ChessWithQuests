from uzivatel import Uzivatel
from hrac import Hrac
from herni_plocha import Herni_Plocha
from tah import Tah
from revizor_tahu import RevizorTahu
from game_logger import GameLogger
from game_manager import GameManager
from figurka import Pesak
from figurka import Kun
from figurka import Strelec
from figurka import Vez
from figurka import Dama
from figurka import Kral
from kwest import Kwest
from chess_notation_writer import ChessNotationWriter
from model import herni_plocha

uzivatel1 = Uzivatel("zuscak_d", "David Zuščák", "david.zuscak@gjkt.eu", 2500)
uzivatel2 = Uzivatel("ryba_a", "Adam Ryba", "adam@email.cz", 1640)

kwest1 = Kwest("První partie", "Zahraj svou první šachovou partii.")
print(kwest1.validate())
uzivatel1.pridej_kwest(kwest1)

hrac1 = Hrac(barva=0, uzivatel=uzivatel1)
hrac2 = Hrac(barva=1, uzivatel=uzivatel2)
print(hrac1)
print(f"ELO hráče 1: {hrac1.getEloRating()}")

plocha = Herni_Plocha()

pesak = Pesak(barva=0)
plocha.poloz_figurku(pesak, [6, 4])

kun = Kun(barva=0)
plocha.poloz_figurku(kun, [7, 1])

kral = Kral(barva=0)
plocha.poloz_figurku(kral, [7, 4])

print(f"\nNa pozici [6,4]: {plocha.vrat_obsah([6, 4])}")

tah = Tah(
    vychozi_pozice=[6, 4],
    cilova_pozice=[4, 4],
    figurka=pesak,
    typ_tahu="normalni"
)

print(f"\nTah platný: {tah.over_platnost()}")

revizor = RevizorTahu(herni_plocha=plocha, tah=tah)
print(f"Možné tahy koně: {revizor.simuluj_move()}")

logger = GameLogger("partie.txt")
logger.vytvor_soubor("partie.txt")

manager = GameManager(
    plocha=plocha,
    hrac1=hrac1,
    hrac2=hrac2,
    game_logger=logger,
    revizor_tahu=revizor
)

manager.mozne_tahy(tah)
manager.proved_tah()

writer = ChessNotationWriter("PGN")
writer.pridej_tah(tah)
print(f"\n{writer}")
print(f"Záznamy tahů: {writer.zaznam_hry}")