# main.py
# Punto de entrada — Local OCR
# Ejecutar: python main.py

import sys
import os

BASE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE)

from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QFont

from core.utils import load_config
from assets.themes.themes import get_theme
from gui.main_window import MainWindow, cargar_icono


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Local OCR")
    app.setOrganizationName("Emmanuel Arroyo")
    app.setFont(QFont("Segoe UI", 10))

    # Cargar tema guardado y aplicar al inicio
    cfg  = load_config()
    tema = cfg.get("tema", "Oscuro")
    app.setStyleSheet(get_theme(tema))

    # Icono de la aplicacion
    icono = cargar_icono()
    if not icono.isNull():
        app.setWindowIcon(icono)

    window = MainWindow(app)
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
