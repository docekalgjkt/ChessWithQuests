# -*- coding: utf-8 -*-
"""GameManagerController – zpracovává události během partie (klik na desku, časovač, LAN zprávy).

Tok podle sekvenčního diagramu "výběr tahu":
  klik_na_desku -> vyber_pole -> GameManager.je_vlastni_figurka
     ne  -> GameView.reset_stavu
     ano -> GameManager.vrat_mozne_tahy -> GameView.zobraz_mozne_tahy
  další klik na cílové pole -> GameManager.proved_tah -> GameView.aktualizuj_desku, HracGameView.aktualizuj_hrace
"""
from __future__ import annotations

from typing import TYPE_CHECKING, List, Optional, Sequence, Tuple

from models.game_manager import GameManager
from utils.konstanty import BILA, CERNA
from utils.lan import LanSpojeni
from views.dialog_view import DialogView
from views.game_view import GameView

if TYPE_CHECKING:
    from controllers.app_controller import AppController

Pozice = Tuple[int, int]
VYBER_FIGURKY = "vyber_figurky"
VYBER_CILE = "vyber_cile"


class GameManagerController:
    def __init__(self, app: "AppController", game_manager: GameManager, lan: Optional[LanSpojeni] = None,
                 mistni_barvy: Sequence[int] = (BILA, CERNA), otoceno: bool = False):
        self.app = app
        self.okno = app.okno
        self.game_manager = game_manager
        self.herni_plocha = game_manager.herni_plocha
        self.user_manager = app.user_manager
        self.quest_manager = app.quest_manager
        self.lan = lan
        self.mistni_barvy: Tuple[int, ...] = tuple(mistni_barvy)   # za které barvy se hraje na tomto PC
        self.stav = VYBER_FIGURKY
        self._id_casovace: Optional[str] = None
        self._id_lan: Optional[str] = None
        self._vyhodnoceno = False
        self._cekani_na_cas = 0

        self.game_view = GameView(self.okno, self, self.herni_plocha.rozmery, app.konfigurace.vzhled(),
                                  otoceno, lan is not None)
        self.hraci_view = self.game_view.hraci_view
        self.okno.pridej_obrazovku("hra", self.game_view)
        self.aktualizuj_view()
        self.okno.zobraz_obrazovku("hra")
        if self.lan is not None:
            self._id_lan = self.okno.after(100, self._zpracuj_lan)
        if game_manager.je_konec():
            self._konec_partie()
        else:
            self._id_casovace = self.okno.after(1000, self.tik_casovace)

    # ------------------------------------------------------------ pomocné
    def _muze_tahnout(self) -> bool:
        return self.game_manager.barva_na_tahu in self.mistni_barvy

    def _moje_barva(self) -> int:
        """Barva, za kterou se vzdává / odchází: v LAN moje, v hotseatu hráč na tahu."""
        return self.mistni_barvy[0] if self.lan is not None else self.game_manager.barva_na_tahu

    # ------------------------------------------------------------ události z GameView
    def klik_na_desku(self, udalost) -> None:
        pole = self.game_view.deska_view.na_souradnice(udalost.x, udalost.y)
        if pole is not None:
            self.vyber_pole(pole)

    def vyber_pole(self, souradnice: Pozice) -> None:
        gm = self.game_manager
        if gm.je_konec() or not self._muze_tahnout():
            return
        if self.stav == VYBER_CILE and any(t.cilova_pozice == souradnice for t in gm.mozne_tahy_figurky):
            self._proved_tah(souradnice)
            return
        if gm.je_vlastni_figurka(souradnice):
            tahy = gm.vrat_mozne_tahy(souradnice)
            self.stav = VYBER_CILE
            self.game_view.zobraz_mozne_tahy(tahy, souradnice)
        else:
            self.zrus_vyber()

    def zrus_vyber(self) -> None:
        self.stav = VYBER_FIGURKY
        self.game_manager.nastav_aktivni_figurku(None)
        self.game_view.reset_stavu()

    def _proved_tah(self, souradnice: Pozice, promena_na: Optional[str] = None, vzdaleny: bool = False) -> None:
        gm = self.game_manager
        odkud = gm.aktivni_figurka
        kandidat = next((t for t in gm.mozne_tahy_figurky if t.cilova_pozice == souradnice), None)
        if kandidat is None or odkud is None:
            self.zrus_vyber()
            return
        if kandidat.promena and promena_na is None:
            vybrana = DialogView(self.okno, "Proměna pěšáka").vyber_figurku(gm.moznosti_promeny(gm.barva_na_tahu))
            promena_na = vybrana.nazev
        if not gm.proved_tah(souradnice, promena_na):
            self.zrus_vyber()
            return
        if self.lan is not None and not vzdaleny:
            self.lan.posli({"typ": "tah", "z": list(odkud), "na": list(souradnice), "promena": promena_na})
        self.stav = VYBER_FIGURKY
        self._cekani_na_cas = 0
        self.game_view.reset_stavu()
        self.aktualizuj_view()
        self._zpracuj_kwesty()
        if gm.je_konec():
            self._konec_partie()

    def vratit_tah(self) -> None:
        if self.lan is not None or not self.game_manager.lze_vratit_tah():
            return
        self.game_manager.zrus_tah()
        self.zrus_vyber()
        self.aktualizuj_view()

    def vzdat_partii(self) -> None:
        gm = self.game_manager
        if gm.je_konec():
            return
        barva = self._moje_barva()
        if not DialogView(self.okno, "Vzdát partii").potvrd(f"Opravdu se {gm.hrac_barvy(barva).jmeno} vzdává?"):
            return
        gm.ukonci(GameManager.VZDANO, vitez=-barva)
        if self.lan is not None:
            self.lan.posli({"typ": "vzdat"})
        self._konec_partie()

    def nabidnout_remizu(self) -> None:
        gm = self.game_manager
        if gm.je_konec():
            return
        if self.lan is not None:
            self.lan.posli({"typ": "remiza_nabidka"})
            self.game_view.zobraz_kwest_info("Remíza nabídnuta – čekám na odpověď soupeře…")
            return
        if DialogView(self.okno, "Remíza").potvrd("Souhlasí oba hráči s remízou?"):
            gm.ukonci(GameManager.REMIZA)
            self._konec_partie()

    def uloz_hru(self) -> None:
        self.app.uloz_hru()

    def odejit(self) -> None:
        gm = self.game_manager
        if not gm.je_konec():
            if self.lan is not None:
                otazka = "Partie ještě běží. Odchod do menu znamená vzdání. Pokračovat?"
            else:
                otazka = "Partie ještě běží a nebude započítána. Opravdu odejít do menu?"
            if not DialogView(self.okno, "Odejít z partie").potvrd(otazka):
                return
            if self.lan is not None:
                gm.ukonci(GameManager.VZDANO, vitez=-self._moje_barva())
                self.lan.posli({"typ": "vzdat"})
            else:
                gm.ukonci(GameManager.ODPOJENO)
            self._vyhodnot_konec()
        self.ukonci()
        self.app.konec_partie()

    # ------------------------------------------------------------ časovač
    def tik_casovace(self) -> None:
        self._id_casovace = None
        gm = self.game_manager
        if gm.je_konec():
            return
        gm.casovac.pocitej_cas(gm.aktivni_hrac)
        self._aktualizuj_casy()
        if gm.casovac.vyprsel_cas(gm.aktivni_hrac):
            # v LAN rozhoduje počítač hráče, kterému čas došel (soupeř čeká max. 5 s na zprávu)
            if self.lan is None or self._muze_tahnout() or self._cekani_na_cas >= 5:
                gm.ukonci(GameManager.CAS, vitez=-gm.barva_na_tahu)
                if self.lan is not None and self._muze_tahnout():
                    self.lan.posli({"typ": "cas"})
                self._konec_partie()
                return
            self._cekani_na_cas += 1
        self._id_casovace = self.okno.after(1000, self.tik_casovace)

    # ------------------------------------------------------------ LAN
    def _zpracuj_lan(self) -> None:
        self._id_lan = None
        if self.lan is None:
            return
        gm = self.game_manager
        for zprava in self.lan.vrat_zpravy():
            typ = zprava.get("typ")
            if typ == "tah" and not gm.je_konec() and not self._muze_tahnout():
                odkud, kam = tuple(zprava["z"]), tuple(zprava["na"])
                gm.vrat_mozne_tahy(odkud)
                if any(t.cilova_pozice == kam for t in gm.mozne_tahy_figurky):
                    self._proved_tah(kam, zprava.get("promena") or "Dáma", vzdaleny=True)
                else:
                    gm.ukonci(GameManager.ODPOJENO)
                    self._konec_partie("Hra se rozešla se soupeřem (neplatný tah ze sítě).")
            elif typ == "vzdat" and not gm.je_konec():
                gm.ukonci(GameManager.VZDANO, vitez=self.mistni_barvy[0])
                self._konec_partie()
            elif typ == "cas" and not gm.je_konec():
                gm.ukonci(GameManager.CAS, vitez=self.mistni_barvy[0])
                self._konec_partie()
            elif typ == "remiza_nabidka" and not gm.je_konec():
                prijato = DialogView(self.okno, "Nabídka remízy").potvrd("Soupeř nabízí remízu. Přijímáš?")
                self.lan.posli({"typ": "remiza_odpoved", "prijato": prijato})
                if prijato:
                    gm.ukonci(GameManager.REMIZA)
                    self._konec_partie()
            elif typ == "remiza_odpoved" and not gm.je_konec():
                if zprava.get("prijato"):
                    gm.ukonci(GameManager.REMIZA)
                    self._konec_partie()
                else:
                    self.game_view.zobraz_kwest_info("Soupeř remízu odmítl.")
            elif typ == "_odpojeno":
                if not gm.je_konec():
                    gm.ukonci(GameManager.ODPOJENO)
                    self._konec_partie("Soupeř se odpojil.")
                self.lan.zavri()
                self.lan = None
                return
            if self.lan is None:
                return
        self._id_lan = self.okno.after(100, self._zpracuj_lan)

    # ------------------------------------------------------------ zobrazení
    def aktualizuj_view(self) -> None:
        gm = self.game_manager
        self.game_view.aktualizuj_desku(self.herni_plocha.herni_deska, gm.aktualni_tah, gm.pole_v_sachu())
        for i, hrac in enumerate(gm.hraci):
            panel = self.hraci_view[i]
            panel.aktualizuj_hrace(hrac)
            panel.zobraz_vyhozene(self.herni_plocha.vyhozene(-hrac.barva))
            panel.nastav_aktivni(i == gm.aktivni_hrac and not gm.je_konec())
        self._aktualizuj_casy()
        self.game_view.aktualizuj_historii(gm.notace_historie)
        text = gm.vysledek_text()
        if self.lan is not None and not gm.je_konec():
            text += "  (hraješ ty)" if self._muze_tahnout() else "  (soupeř přemýšlí…)"
        self.game_view.zobraz_stav(text, gm.stav in (GameManager.SACH, GameManager.MAT))
        konec = gm.je_konec()
        self.game_view.nastav_tlacitka(vratit=self.lan is None and gm.lze_vratit_tah(), remiza=not konec,
                                       vzdat=not konec, ulozit=self.lan is None and not konec)

    def _aktualizuj_casy(self) -> None:
        casovac = self.game_manager.casovac
        for i in range(2):
            cas_tahu = casovac.zbyva_tah() if i == self.game_manager.aktivni_hrac else None
            self.hraci_view[i].aktualizuj_cas(casovac.zbyva_hrac(i), cas_tahu)

    def _zpracuj_kwesty(self) -> None:
        gm = self.game_manager
        if not gm.posledni_kwesty:
            return
        self.user_manager.uloz()
        for hrac, kwesty, odmeny in gm.posledni_kwesty:
            if self.lan is not None and hrac.barva not in self.mistni_barvy:
                continue
            self.game_view.zobraz_kwest_info(f"★ {hrac.jmeno}: " + ", ".join(q.nazev for q in kwesty))
            self.hraci_view[0 if hrac.barva == BILA else 1].aktualizuj_hrace(hrac)
            DialogView(self.okno, "Quest splněn!").zobraz_odmenu(kwesty, hrac.jmeno, odmeny)

    # ------------------------------------------------------------ konec partie
    def _konec_partie(self, poznamka: str = "") -> None:
        self._zastav_casovac()
        self.zrus_vyber()
        self.aktualizuj_view()
        radky = self._vyhodnot_konec()
        vysledek = self.game_manager.vysledek_text()
        self.game_view.zobraz_konec_hry(vysledek)
        text = "\n".join(filter(None, [poznamka, vysledek, "", *radky]))
        DialogView(self.okno, "Konec partie").zobraz_zpravu("Konec partie", text)

    def _vyhodnot_konec(self) -> List[str]:
        """ELO, statistiky a questy po konci partie (jen jednou)."""
        if self._vyhodnoceno:
            return []
        self._vyhodnoceno = True
        gm = self.game_manager
        if gm.stav == GameManager.ODPOJENO:
            return ["Partie se nezapočítává."]
        if not gm.notace_historie:
            return ["Partie bez jediného tahu se nezapočítává."]
        elo_pred = {h.barva: h.getEloRating() for h in gm.hraci}
        radky: List[str] = []
        for hrac in gm.hraci:
            uzivatel = hrac.uzivatel
            if uzivatel.je_host or (self.lan is not None and hrac.barva not in self.mistni_barvy):
                continue
            if gm.vitez is None:
                vysledek = "remiza"
            else:
                vysledek = "vyhra" if gm.vitez == hrac.barva else "prohra"
            skore = {"vyhra": 1.0, "remiza": 0.5, "prohra": 0.0}[vysledek]
            zmena = self.user_manager.vyhodnot_elo(uzivatel, elo_pred[-hrac.barva], skore)
            self.user_manager.zaznamenej_vysledek(uzivatel, vysledek)
            kwesty, _ = self.quest_manager.vyhodnot_konec_partie(hrac, vysledek, gm.statistiky[hrac.barva]["tahu"])
            radky.append(f"{uzivatel.zobrazovane_jmeno}: ELO {uzivatel.elo} ({zmena:+d}), {uzivatel.xp} XP")
            radky += [f"   ★ {q.nazev} (+{q.odmena_xp} XP, +{q.odmena_body} b.)" for q in kwesty]
        bily, cerny = gm.hraci[0].uzivatel, gm.hraci[1].uzivatel
        if not (bily.je_host and cerny.je_host):
            self.user_manager.zaznamenej_partii(bily, cerny, gm.vysledek_pgn(), len(gm.notace_historie),
                                                "LAN" if self.lan is not None else "hotseat")
        self.user_manager.uloz()
        return radky

    def _zastav_casovac(self) -> None:
        if self._id_casovace is not None:
            self.okno.after_cancel(self._id_casovace)
            self._id_casovace = None

    def ukonci(self) -> None:
        """Uklidí časovače a síťové spojení (při odchodu z partie / zavření aplikace)."""
        self._zastav_casovac()
        if self._id_lan is not None:
            self.okno.after_cancel(self._id_lan)
            self._id_lan = None
        if self.lan is not None:
            self.lan.zavri()
            self.lan = None

