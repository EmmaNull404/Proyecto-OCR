# gui/theme_editor.py
# Editor de temas en vivo para Local OCR Pro
# Permite editar colores de cualquier tema y ver los cambios en tiempo real.
# Los temas personalizados se guardan en assets/themes/custom_themes.json

import os, json
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QComboBox, QLineEdit, QFrame, QMessageBox, QInputDialog, QScrollArea,
    QWidget, QSizePolicy
)
from PyQt6.QtGui import QColor, QFont, QPainter, QBrush
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtWidgets import QColorDialog

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CUSTOM_PATH = os.path.join(BASE_DIR, "assets", "themes", "custom_themes.json")

# Etiquetas amigables para cada clave de la paleta
ETIQUETAS = {
    "bg":     "Fondo principal",
    "fg":     "Texto principal",
    "brd":    "Bordes",
    "head":   "Cabeceras / Toolbar",
    "alt":    "Filas alternas",
    "acento": "Botones / Acento",
    "hover":  "Hover de botones",
}


def cargar_custom_themes() -> dict:
    if os.path.exists(CUSTOM_PATH):
        try:
            with open(CUSTOM_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {}


def guardar_custom_themes(temas: dict):
    os.makedirs(os.path.dirname(CUSTOM_PATH), exist_ok=True)
    with open(CUSTOM_PATH, "w", encoding="utf-8") as f:
        json.dump(temas, f, indent=4, ensure_ascii=False)


# Paletas base de los temas integrados (solo lectura, para clonar)
PALETAS_BASE = {
    "Oscuro": {
        "bg": "#1e1e1e", "fg": "#eff0f1", "brd": "#3a3a3a",
        "head": "#2d2d2d", "alt": "#252525",
        "acento": "#3c7bd4", "hover": "#2a5fa8",
    },
    "Selva": {
        "bg": "#0a1a0a", "fg": "#d0e0d0", "brd": "#1a3a1a",
        "head": "#122a12", "alt": "#0d200d",
        "acento": "#3d7a3d", "hover": "#ff6b2b",
    },
    "Claro": {
        "bg": "#f5f5f5", "fg": "#1a1a1a", "brd": "#cccccc",
        "head": "#e8e8e8", "alt": "#fafafa",
        "acento": "#8e44ad", "hover": "#6c3483",
    },
}


class ColorBoton(QPushButton):
    """Botón que muestra un color sólido y abre QColorDialog al hacer clic."""
    color_cambiado = pyqtSignal(str, str)  # clave, nuevo_hex

    def __init__(self, clave: str, hex_color: str, parent=None):
        super().__init__(parent)
        self.clave = clave
        self._hex  = hex_color
        self.setFixedSize(QSize(100, 32))
        self._actualizar()

    def _actualizar(self):
        c = QColor(self._hex)
        # Texto blanco o negro según luminosidad del fondo
        fg = "#ffffff" if c.lightness() < 140 else "#000000"
        self.setStyleSheet(
            f"background-color: {self._hex}; color: {fg}; "
            f"border: 1px solid #555; border-radius: 4px; "
            f"font-family: Consolas; font-size: 10px;")
        self.setText(self._hex.upper())

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            color = QColorDialog.getColor(
                QColor(self._hex), self,
                f"Color: {ETIQUETAS.get(self.clave, self.clave)}")
            if color.isValid():
                self._hex = color.name()
                self._actualizar()
                self.color_cambiado.emit(self.clave, self._hex)
        super().mousePressEvent(event)

    def set_color(self, hex_color: str):
        self._hex = hex_color
        self._actualizar()

    def get_color(self) -> str:
        return self._hex


class ThemeEditor(QDialog):
    """
    Editor de temas en vivo.

    Señales:
        tema_aplicado(str, dict)  — nombre del tema y paleta para preview
        tema_guardado(str)        — nombre del tema guardado
    """
    tema_aplicado = pyqtSignal(str, dict)
    tema_guardado = pyqtSignal(str)

    def __init__(self, parent, paletas_activas: dict):
        super().__init__(parent)
        self._paletas    = paletas_activas   # referencia a PALETAS de main_window
        self._custom     = cargar_custom_themes()
        self._editando   = dict(list(paletas_activas.items())[0][1])  # copia editable
        self._nombre_sel = list(paletas_activas.keys())[0]
        self._botones    = {}  # clave -> ColorBoton

        self.setWindowTitle("Editor de Temas")
        self.setMinimumWidth(480)
        self.setMinimumHeight(420)
        self.setModal(False)  # no modal: permite ver cambios en la ventana principal
        self._build()
        self._centrar()

    # ── Construcción UI ─────────────────────────────────────────
    def _build(self):
        lay = QVBoxLayout(self)
        lay.setSpacing(10)
        lay.setContentsMargins(16, 14, 16, 12)

        # ── Selector de tema base ──
        top = QHBoxLayout()
        top.addWidget(QLabel("Tema base:"))
        self._combo = QComboBox()
        self._combo.setMinimumWidth(160)
        self._poblar_combo()
        self._combo.currentTextChanged.connect(self._cargar_tema)
        top.addWidget(self._combo)
        top.addStretch()
        lay.addLayout(top)

        sep = QFrame(); sep.setFrameShape(QFrame.Shape.HLine)
        lay.addWidget(sep)

        # ── Grid de colores ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        contenedor = QWidget()
        grid = QGridLayout(contenedor)
        grid.setSpacing(8)
        grid.setContentsMargins(0, 0, 0, 0)

        grid.addWidget(self._lbl_bold("Variable"), 0, 0)
        grid.addWidget(self._lbl_bold("Color actual"), 0, 1)
        grid.addWidget(self._lbl_bold("Vista previa"), 0, 2)

        for fila, (clave, etiqueta) in enumerate(ETIQUETAS.items(), 1):
            hex_c = self._editando.get(clave, "#888888")

            lbl = QLabel(etiqueta)
            lbl.setMinimumWidth(150)
            btn = ColorBoton(clave, hex_c)
            btn.color_cambiado.connect(self._on_color_cambiado)

            preview = QLabel()
            preview.setFixedSize(QSize(60, 28))
            preview.setObjectName(f"prev_{clave}")
            self._actualizar_preview(preview, hex_c)

            grid.addWidget(lbl,     fila, 0)
            grid.addWidget(btn,     fila, 1)
            grid.addWidget(preview, fila, 2)

            self._botones[clave] = (btn, preview)

        scroll.setWidget(contenedor)
        lay.addWidget(scroll, 1)

        sep2 = QFrame(); sep2.setFrameShape(QFrame.Shape.HLine)
        lay.addWidget(sep2)

        # ── Botones inferiores ──
        bar = QHBoxLayout()
        bar.setSpacing(8)

        btn_preview = QPushButton("▶  Aplicar preview")
        btn_preview.setToolTip("Ver los colores en la ventana principal sin guardar")
        btn_preview.clicked.connect(self._aplicar_preview)

        btn_guardar = QPushButton("💾  Guardar tema")
        btn_guardar.setToolTip("Guardar como tema personalizado")
        btn_guardar.clicked.connect(self._guardar_tema)

        btn_borrar = QPushButton("🗑  Eliminar tema")
        btn_borrar.setToolTip("Eliminar tema personalizado seleccionado")
        btn_borrar.clicked.connect(self._borrar_tema)
        btn_borrar.setStyleSheet(
            "background-color: #c0392b; color: white; border-radius: 5px; padding: 6px 12px;")

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.accept)

        bar.addWidget(btn_preview)
        bar.addWidget(btn_guardar)
        bar.addWidget(btn_borrar)
        bar.addStretch()
        bar.addWidget(btn_cerrar)
        lay.addLayout(bar)

    # ── Helpers UI ───────────────────────────────────────────────
    def _lbl_bold(self, texto):
        l = QLabel(texto)
        l.setFont(QFont("Segoe UI", 9, QFont.Weight.Bold))
        return l

    def _actualizar_preview(self, lbl: QLabel, hex_c: str):
        lbl.setStyleSheet(
            f"background-color: {hex_c}; border: 1px solid #888; border-radius: 3px;")

    def _poblar_combo(self):
        self._combo.blockSignals(True)
        self._combo.clear()
        # Temas integrados
        for nombre in self._paletas:
            self._combo.addItem(f"● {nombre}", nombre)
        # Temas personalizados
        for nombre in self._custom:
            self._combo.addItem(f"★ {nombre}", nombre)
        self._combo.blockSignals(False)
        # Seleccionar el primero
        if self._combo.count():
            self._combo.setCurrentIndex(0)

    # ── Lógica principal ─────────────────────────────────────────
    def _cargar_tema(self, texto_combo: str):
        nombre = self._combo.currentData()
        if not nombre:
            return
        self._nombre_sel = nombre

        if nombre in self._paletas:
            paleta = dict(self._paletas[nombre])
        elif nombre in self._custom:
            paleta = dict(self._custom[nombre])
        else:
            return

        self._editando = paleta
        for clave, (btn, preview) in self._botones.items():
            hex_c = paleta.get(clave, "#888888")
            btn.set_color(hex_c)
            self._actualizar_preview(preview, hex_c)

    def _on_color_cambiado(self, clave: str, hex_c: str):
        self._editando[clave] = hex_c
        _, preview = self._botones[clave]
        self._actualizar_preview(preview, hex_c)

    def _aplicar_preview(self):
        """Envía la paleta editada a MainWindow para ver en vivo."""
        nombre = self._combo.currentData() or self._nombre_sel
        self.tema_aplicado.emit(nombre, dict(self._editando))

    def _guardar_tema(self):
        nombre_base = self._combo.currentData() or "Mi Tema"
        # Si es un tema integrado, sugerir un nombre nuevo
        if nombre_base in self._paletas:
            nombre_base = f"{nombre_base} personalizado"

        nombre, ok = QInputDialog.getText(
            self, "Guardar tema",
            "Nombre del tema:",
            text=nombre_base)
        if not ok or not nombre.strip():
            return
        nombre = nombre.strip()

        # No sobreescribir temas integrados
        if nombre in self._paletas:
            QMessageBox.warning(self, "Nombre reservado",
                f'"{nombre}" es un tema integrado y no puede sobreescribirse.\n'
                "Elige un nombre diferente.")
            return

        self._custom[nombre] = dict(self._editando)
        guardar_custom_themes(self._custom)
        self._poblar_combo()

        # Seleccionar el recién guardado
        for i in range(self._combo.count()):
            if self._combo.itemData(i) == nombre:
                self._combo.setCurrentIndex(i)
                break

        self.tema_guardado.emit(nombre)
        QMessageBox.information(self, "Guardado",
            f'Tema "{nombre}" guardado correctamente.')

    def _borrar_tema(self):
        nombre = self._combo.currentData()
        if not nombre or nombre in self._paletas:
            QMessageBox.warning(self, "No se puede eliminar",
                "Solo se pueden eliminar temas personalizados (★).")
            return

        resp = QMessageBox.question(self, "Eliminar tema",
            f'¿Eliminar el tema "{nombre}"?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp != QMessageBox.StandardButton.Yes:
            return

        self._custom.pop(nombre, None)
        guardar_custom_themes(self._custom)
        self._poblar_combo()

    def _centrar(self):
        if self.parent():
            pr = self.parent().geometry()
            self.adjustSize()
            self.setGeometry(
                pr.x() + (pr.width()  - self.width())  // 2,
                pr.y() + (pr.height() - self.height()) // 2,
                self.width(), self.height())
