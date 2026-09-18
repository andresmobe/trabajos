"""
LogiDrone-UCC — Punto de Entrada
=================================
Ejecutar:
    python main.py

Empaquetar ejecutable (requiere PyInstaller):
    pip install pyinstaller
    pyinstaller --windowed --onefile --name LogiDrone-UCC main.py
"""

import sys
import os

# Agregar el directorio raíz al path para que los imports funcionen
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from gui.app import LogiDroneApp


def main():
    app = LogiDroneApp()
    app.run()


if __name__ == "__main__":
    main()
