# -*- coding: utf-8 -*-
"""ŠachySQuesty – desktopové šachy s úkoly, achievementy a vlastními figurkami.

Spuštění:  python main.py   (Python 3.9+, tkinter je součástí běžné instalace Pythonu)
"""
from controllers.app_controller import AppController


def main() -> None:
    AppController().spust_aplikaci()


if __name__ == "__main__":
    main()
