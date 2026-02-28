# assets/themes/themes.py
# Gestor de temas QSS para Local OCR
# Para agregar un tema nuevo: añade una entrada al dict THEMES
# con su nombre como clave y el QSS como valor.

THEMES = {

    # ─────────────────────────────────────────────
    #  OSCURO  —  Modo por defecto
    # ─────────────────────────────────────────────
    "Oscuro": """
        QMainWindow, QDialog, QWidget {
            background-color: #2b2b2b;
            color: #e0e0e0;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }
        QMenuBar {
            background-color: #1e1e1e;
            color: #e0e0e0;
            padding: 2px;
        }
        QMenuBar::item:selected {
            background-color: #3a3a3a;
            border-radius: 4px;
        }
        QMenu {
            background-color: #2b2b2b;
            color: #e0e0e0;
            border: 1px solid #444;
        }
        QMenu::item:selected {
            background-color: #3c7bd4;
            color: #ffffff;
        }
        QPushButton {
            background-color: #3c7bd4;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 7px 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #5593e8;
        }
        QPushButton:pressed {
            background-color: #2a5fa8;
        }
        QPushButton:disabled {
            background-color: #444444;
            color: #777777;
        }
        QTextEdit, QPlainTextEdit {
            background-color: #1e1e1e;
            color: #e0e0e0;
            border: 1px solid #444;
            border-radius: 6px;
            padding: 6px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
        }
        QLabel {
            color: #e0e0e0;
        }
        QLabel#preview_label {
            background-color: #1a3a5c;
            color: #7ab3e0;
            border: 2px dashed #3c7bd4;
            border-radius: 8px;
            font-size: 14px;
        }
        QComboBox {
            background-color: #3a3a3a;
            color: #e0e0e0;
            border: 1px solid #555;
            border-radius: 6px;
            padding: 5px 10px;
        }
        QComboBox::drop-down {
            border: none;
            width: 24px;
        }
        QComboBox QAbstractItemView {
            background-color: #2b2b2b;
            color: #e0e0e0;
            selection-background-color: #3c7bd4;
        }
        QProgressBar {
            background-color: #1e1e1e;
            border: 1px solid #444;
            border-radius: 4px;
            height: 14px;
            text-align: center;
            color: #e0e0e0;
            font-size: 11px;
        }
        QProgressBar::chunk {
            background-color: #3c7bd4;
            border-radius: 4px;
        }
        QStatusBar {
            background-color: #1e1e1e;
            color: #aaaaaa;
            font-size: 11px;
        }
        QSplitter::handle {
            background-color: #444;
            width: 3px;
        }
        QScrollBar:vertical {
            background: #1e1e1e;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #555;
            border-radius: 5px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: #3c7bd4;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        QGroupBox {
            border: 1px solid #444;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 8px;
            color: #aaaaaa;
            font-size: 11px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
        }
        QToolBar {
            background-color: #1e1e1e;
            border-bottom: 1px solid #444;
            spacing: 4px;
            padding: 4px;
        }
        QToolButton {
            background-color: transparent;
            color: #e0e0e0;
            border-radius: 5px;
            padding: 5px 10px;
        }
        QToolButton:hover {
            background-color: #3a3a3a;
        }
    """,

    # ─────────────────────────────────────────────
    #  CLARO  —  Modo diurno
    # ─────────────────────────────────────────────
    "Claro": """
        QMainWindow, QDialog, QWidget {
            background-color: #f5f5f5;
            color: #1a1a1a;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }
        QMenuBar {
            background-color: #ffffff;
            color: #1a1a1a;
            border-bottom: 1px solid #ddd;
            padding: 2px;
        }
        QMenuBar::item:selected {
            background-color: #e0e9f8;
            border-radius: 4px;
        }
        QMenu {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1px solid #ccc;
        }
        QMenu::item:selected {
            background-color: #2563c7;
            color: #ffffff;
        }
        QPushButton {
            background-color: #2563c7;
            color: #ffffff;
            border: none;
            border-radius: 6px;
            padding: 7px 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #3c7bd4;
        }
        QPushButton:pressed {
            background-color: #1a4fa0;
        }
        QPushButton:disabled {
            background-color: #cccccc;
            color: #888888;
        }
        QTextEdit, QPlainTextEdit {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 6px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
        }
        QLabel {
            color: #1a1a1a;
        }
        QLabel#preview_label {
            background-color: #ddeeff;
            color: #2563c7;
            border: 2px dashed #2563c7;
            border-radius: 8px;
            font-size: 14px;
        }
        QComboBox {
            background-color: #ffffff;
            color: #1a1a1a;
            border: 1px solid #ccc;
            border-radius: 6px;
            padding: 5px 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #ffffff;
            color: #1a1a1a;
            selection-background-color: #2563c7;
            selection-color: #ffffff;
        }
        QProgressBar {
            background-color: #e0e0e0;
            border: 1px solid #ccc;
            border-radius: 4px;
            height: 14px;
            text-align: center;
            color: #1a1a1a;
            font-size: 11px;
        }
        QProgressBar::chunk {
            background-color: #2563c7;
            border-radius: 4px;
        }
        QStatusBar {
            background-color: #ffffff;
            color: #666666;
            border-top: 1px solid #ddd;
            font-size: 11px;
        }
        QSplitter::handle {
            background-color: #cccccc;
            width: 3px;
        }
        QScrollBar:vertical {
            background: #f0f0f0;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #bbbbbb;
            border-radius: 5px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: #2563c7;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        QGroupBox {
            border: 1px solid #ccc;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 8px;
            color: #666666;
            font-size: 11px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
        }
        QToolBar {
            background-color: #ffffff;
            border-bottom: 1px solid #ddd;
            spacing: 4px;
            padding: 4px;
        }
        QToolButton {
            background-color: transparent;
            color: #1a1a1a;
            border-radius: 5px;
            padding: 5px 10px;
        }
        QToolButton:hover {
            background-color: #e0e9f8;
        }
    """,

    # ─────────────────────────────────────────────
    #  SELVA  —  Tema color (inspiración jurásica)
    #  Nota: los colores base vienen de la paleta
    #  original del proyecto. El acento naranja
    #  "lava" es el volcán en erupción. 🌋
    # ─────────────────────────────────────────────
    "Selva": """
        QMainWindow, QDialog, QWidget {
            background-color: #1a2e1a;
            color: #e8f5e8;
            font-family: 'Segoe UI', Arial, sans-serif;
            font-size: 13px;
        }
        QMenuBar {
            background-color: #162614;
            color: #e8f5e8;
            border-bottom: 1px solid #2d5a2d;
            padding: 2px;
        }
        QMenuBar::item:selected {
            background-color: #2d5a2d;
            border-radius: 4px;
        }
        QMenu {
            background-color: #1e3d1e;
            color: #e8f5e8;
            border: 1px solid #2d5a2d;
        }
        QMenu::item:selected {
            background-color: #a8d85a;
            color: #1a2e1a;
        }
        QPushButton {
            background-color: #3d7a3d;
            color: #e8f5e8;
            border: none;
            border-radius: 6px;
            padding: 7px 18px;
            font-weight: bold;
        }
        QPushButton:hover {
            background-color: #ff6b2b;
            color: #ffffff;
        }
        QPushButton:pressed {
            background-color: #cc4a10;
        }
        QPushButton:disabled {
            background-color: #2a3d2a;
            color: #556655;
        }
        QTextEdit, QPlainTextEdit {
            background-color: #0d1f0d;
            color: #a8d85a;
            border: 1px solid #2d5a2d;
            border-radius: 6px;
            padding: 6px;
            font-family: 'Consolas', monospace;
            font-size: 12px;
        }
        QLabel {
            color: #e8f5e8;
        }
        QLabel#preview_label {
            background-color: #0d1f0d;
            color: #5aaa5a;
            border: 2px dashed #3d7a3d;
            border-radius: 8px;
            font-size: 14px;
        }
        QComboBox {
            background-color: #1e3d1e;
            color: #e8f5e8;
            border: 1px solid #2d5a2d;
            border-radius: 6px;
            padding: 5px 10px;
        }
        QComboBox QAbstractItemView {
            background-color: #1e3d1e;
            color: #e8f5e8;
            selection-background-color: #a8d85a;
            selection-color: #1a2e1a;
        }
        QProgressBar {
            background-color: #0d1f0d;
            border: 1px solid #2d5a2d;
            border-radius: 4px;
            height: 14px;
            text-align: center;
            color: #e8f5e8;
            font-size: 11px;
        }
        QProgressBar::chunk {
            background-color: #ff6b2b;
            border-radius: 4px;
        }
        QStatusBar {
            background-color: #162614;
            color: #8ab88a;
            border-top: 1px solid #2d5a2d;
            font-size: 11px;
        }
        QSplitter::handle {
            background-color: #2d5a2d;
            width: 3px;
        }
        QScrollBar:vertical {
            background: #0d1f0d;
            width: 10px;
            border-radius: 5px;
        }
        QScrollBar::handle:vertical {
            background: #3d7a3d;
            border-radius: 5px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: #a8d85a;
        }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0;
        }
        QGroupBox {
            border: 1px solid #2d5a2d;
            border-radius: 6px;
            margin-top: 10px;
            padding-top: 8px;
            color: #8ab88a;
            font-size: 11px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 10px;
            padding: 0 4px;
        }
        QToolBar {
            background-color: #162614;
            border-bottom: 1px solid #2d5a2d;
            spacing: 4px;
            padding: 4px;
        }
        QToolButton {
            background-color: transparent;
            color: #e8f5e8;
            border-radius: 5px;
            padding: 5px 10px;
        }
        QToolButton:hover {
            background-color: #2d5a2d;
        }
    """,
}

# Tema por defecto al iniciar la app
DEFAULT_THEME = "Oscuro"

def get_theme(name: str) -> str:
    """Devuelve el QSS del tema solicitado.
    Si no existe, devuelve el tema Oscuro."""
    return THEMES.get(name, THEMES[DEFAULT_THEME])

def theme_names() -> list:
    """Lista de nombres de temas disponibles."""
    return list(THEMES.keys())
