# -*- coding: utf-8 -*-
"""LanSpojeni – jednoduché spojení dvou počítačů v síti (TCP, zprávy jako JSON po řádcích).

Síťová komunikace běží ve vlastním vlákně a přijaté zprávy ukládá do fronty.
GUI si je vyzvedává metodou vrat_zpravy() (přes okno.after), protože tkinter
se nesmí volat z jiného vlákna.

Interní zprávy: {"typ": "_pripojeno"}, {"typ": "_odpojeno"}, {"typ": "_chyba", "text": ...}
"""
from __future__ import annotations

import json
import queue
import socket
import threading
from typing import List, Optional

from utils.konstanty import LAN_PORT


class LanSpojeni:
    def __init__(self, port: int = LAN_PORT):
        self.port = int(port)
        self.role: Optional[str] = None          # "host" nebo "klient"
        self.pripojeno = False
        self._server: Optional[socket.socket] = None
        self._spojeni: Optional[socket.socket] = None
        self._fronta: "queue.Queue[dict]" = queue.Queue()
        self._zamek = threading.Lock()
        self._bezi = False

    # ------------------------------------------------------------ navázání spojení
    def hostuj(self) -> None:
        """Začne čekat na soupeře (neblokuje)."""
        self.role = "host"
        self._bezi = True
        threading.Thread(target=self._cekej_na_klienta, daemon=True).start()

    def pripoj(self, ip: str) -> None:
        """Připojí se k hostiteli (neblokuje)."""
        self.role = "klient"
        self._bezi = True
        threading.Thread(target=self._pripoj_k_hostiteli, args=(ip.strip(),), daemon=True).start()

    def _cekej_na_klienta(self) -> None:
        try:
            self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self._server.bind(("", self.port))
            self._server.listen(1)
            self._server.settimeout(0.5)
            while self._bezi:
                try:
                    spojeni, _ = self._server.accept()
                except socket.timeout:
                    continue
                self._spusteno(spojeni)
                return
        except OSError as chyba:
            if self._bezi:
                self._fronta.put({"typ": "_chyba", "text": f"Nelze založit hru na portu {self.port}: {chyba}"})

    def _pripoj_k_hostiteli(self, ip: str) -> None:
        try:
            spojeni = socket.create_connection((ip, self.port), timeout=5)
            spojeni.settimeout(None)
            self._spusteno(spojeni)
        except OSError as chyba:
            self._fronta.put({"typ": "_chyba", "text": f"Nepodařilo se připojit k {ip}:{self.port} ({chyba})."})

    def _spusteno(self, spojeni: socket.socket) -> None:
        self._spojeni = spojeni
        self.pripojeno = True
        self._fronta.put({"typ": "_pripojeno"})
        self._prijimej()

    def _prijimej(self) -> None:
        assert self._spojeni is not None
        try:
            with self._spojeni.makefile("r", encoding="utf-8") as soubor:
                for radek in soubor:
                    radek = radek.strip()
                    if radek:
                        try:
                            self._fronta.put(json.loads(radek))
                        except ValueError:
                            continue
        except OSError:
            pass
        if self.pripojeno:
            self.pripojeno = False
            self._fronta.put({"typ": "_odpojeno"})

    # ------------------------------------------------------------ zprávy
    def posli(self, zprava: dict) -> bool:
        if not self.pripojeno or self._spojeni is None:
            return False
        data = (json.dumps(zprava, ensure_ascii=False) + "\n").encode("utf-8")
        try:
            with self._zamek:
                self._spojeni.sendall(data)
            return True
        except OSError:
            return False

    def vrat_zpravy(self) -> List[dict]:
        zpravy = []
        while True:
            try:
                zpravy.append(self._fronta.get_nowait())
            except queue.Empty:
                return zpravy

    def zavri(self) -> None:
        self._bezi = False
        self.pripojeno = False
        if self._spojeni is not None:
            try:
                # shutdown pošle soupeři konec spojení hned (samotné close() čeká na zavření makefile)
                self._spojeni.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
        for s in (self._spojeni, self._server):
            if s is not None:
                try:
                    s.close()
                except OSError:
                    pass
        self._spojeni = None
        self._server = None

    @staticmethod
    def mistni_ip() -> str:
        """IP adresa tohoto počítače v místní síti (pro zobrazení hostiteli)."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
                s.connect(("10.255.255.255", 1))
                return s.getsockname()[0]
        except OSError:
            return "127.0.0.1"
