# gui/config_dialog.py  — Fase 1 finalizada
# Corrección 5:
#   - Botón "Restablecer Valores de Fábrica" presente y funcional
#   - Switch "Abrir al terminar": Verde (SÍ) / Rojo (NO), visualmente claro
#   - _restablecer emite señales para que MainWindow actualice tema/estilos
#   - _guardar incluye TODOS los campos (lang, dpi también)

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QComboBox,
    QLineEdit, QPushButton, QFileDialog, QMessageBox,
    QDialogButtonBox, QWidget, QLabel, QFrame
)
from PyQt6.QtCore import pyqtSignal, Qt
from PyQt6.QtGui import QFont

from assets.themes.themes import theme_names
from core.utils import save_config, reset_to_defaults


class ConfigDialog(QDialog):
    """
    Diálogo de configuración.

    Señales:
        tema_cambiado(str)    — nombre del nuevo tema seleccionado
        config_guardada(dict) — dict completo de configuración guardada
    """
    tema_cambiado   = pyqtSignal(str)
    config_guardada = pyqtSignal(dict)

    def __init__(self, parent, cfg: dict):
        super().__init__(parent)
        self._cfg = dict(cfg)
        self._abrir_estado = bool(cfg.get("abrir_carpeta", True))
        self.setWindowTitle("Preferencias del Sistema")
        self.setMinimumWidth(560)
        self.setModal(True)
        self._build()
        self._centrar()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(16, 16, 16, 12)

        form = QFormLayout()
        form.setSpacing(8)
        form.setLabelAlignment(Qt.AlignmentFlag.AlignRight)

        # ── Rutas ──
        self._inp_tess = QLineEdit(self._cfg.get("tesseract_path", ""))
        self._inp_pop  = QLineEdit(self._cfg.get("poppler_path", ""))
        self._inp_out  = QLineEdit(self._cfg.get("output_dir", ""))

        form.addRow("Tesseract EXE:",   self._campo_ruta(self._inp_tess, "file"))
        form.addRow("Poppler Bin:",     self._campo_ruta(self._inp_pop,  "dir"))
        form.addRow("Carpeta Salida:",  self._campo_ruta(self._inp_out,  "dir"))

        # ── Separador ──
        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setStyleSheet("color: #555;")
        form.addRow(sep)

        # ── Tema ──
        self._combo_tema = QComboBox()
        self._combo_tema.addItems(theme_names())
        self._combo_tema.setCurrentText(self._cfg.get("tema", "Oscuro"))
        form.addRow("Tema Visual:", self._combo_tema)

        # ── Modo de salida ──
        self._combo_salida = QComboBox()
        self._combo_salida.addItems(["ambos", "pdf", "texto"])
        self._combo_salida.setCurrentText(self._cfg.get("modo_salida", "ambos"))
        form.addRow("Modo de Salida:", self._combo_salida)

        # ── Idioma OCR ──
        self._combo_lang = QComboBox()
        self._combo_lang.addItems(["spa+eng", "spa", "eng"])
        self._combo_lang.setCurrentText(self._cfg.get("lang", "spa+eng"))
        form.addRow("Idioma OCR:", self._combo_lang)

        # ── DPI ──
        self._combo_dpi = QComboBox()
        self._combo_dpi.addItems(["150", "200", "300", "400", "600"])
        self._combo_dpi.setCurrentText(self._cfg.get("dpi", "300"))
        form.addRow("DPI (PDF→imagen):", self._combo_dpi)

        # ── CORRECCIÓN 5: Switch Verde/Rojo visualmente claro ────
        self._btn_switch = QPushButton()
        self._btn_switch.setFixedWidth(90)
        self._btn_switch.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        self._btn_switch.clicked.connect(self._toggle_switch)
        self._actualizar_switch()
        form.addRow("Abrir al terminar:", self._btn_switch)

        layout.addLayout(form)

        # ── Línea separadora ──
        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setStyleSheet("color: #555; margin-top: 4px;")
        layout.addWidget(sep2)

        # ── CORRECCIÓN 5: Botón Restablecer + Guardar/Cancelar ───
        bar = QHBoxLayout()
        bar.setSpacing(8)

        btn_reset = QPushButton("↺  Restablecer valores de fábrica")
        btn_reset.setToolTip("Carga config_default.json y aplica inmediatamente")
        btn_reset.clicked.connect(self._restablecer)
        # Estilo diferenciado para que no parezca acción principal
        btn_reset.setStyleSheet(
            "background-color: #7f8c8d; color: white; "
            "border-radius: 5px; padding: 6px 12px; font-weight: normal;")

        btns = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save |
            QDialogButtonBox.StandardButton.Cancel)
        btns.button(QDialogButtonBox.StandardButton.Save).setText("Guardar")
        btns.button(QDialogButtonBox.StandardButton.Cancel).setText("Cancelar")
        btns.accepted.connect(self._guardar)
        btns.rejected.connect(self.reject)

        bar.addWidget(btn_reset)
        bar.addStretch()
        bar.addWidget(btns)
        layout.addLayout(bar)

    # ── Helpers de construcción ──────────────────────────────────
    def _campo_ruta(self, edit: QLineEdit, tipo: str) -> QWidget:
        w = QWidget()
        l = QHBoxLayout(w)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(4)
        btn = QPushButton("...")
        btn.setFixedWidth(36)
        btn.clicked.connect(lambda: self._sel_ruta(edit, tipo))
        l.addWidget(edit)
        l.addWidget(btn)
        return w

    def _sel_ruta(self, edit: QLineEdit, tipo: str):
        if tipo == "file":
            res, _ = QFileDialog.getOpenFileName(
                self, "Seleccionar archivo", edit.text(),
                "Ejecutable (*.exe);;Todos (*.*)")
        else:
            res = QFileDialog.getExistingDirectory(
                self, "Seleccionar carpeta", edit.text())
        if res:
            edit.setText(res)
        self.raise_()
        self.activateWindow()

    # ── Switch "Abrir al terminar" ───────────────────────────────
    def _toggle_switch(self):
        self._abrir_estado = not self._abrir_estado
        self._actualizar_switch()

    def _actualizar_switch(self):
        if self._abrir_estado:
            self._btn_switch.setText("SÍ")
            self._btn_switch.setStyleSheet(
                "background-color: #27ae60; color: white; "
                "font-weight: bold; border-radius: 4px; padding: 6px;")
        else:
            self._btn_switch.setText("NO")
            self._btn_switch.setStyleSheet(
                "background-color: #c0392b; color: white; "
                "font-weight: bold; border-radius: 4px; padding: 6px;")

    # ── Leer campos a dict ───────────────────────────────────────
    def _leer_campos(self) -> dict:
        return {
            "tesseract_path": self._inp_tess.text(),
            "poppler_path":   self._inp_pop.text(),
            "output_dir":     self._inp_out.text(),
            "tema":           self._combo_tema.currentText(),
            "modo_salida":    self._combo_salida.currentText(),
            "lang":           self._combo_lang.currentText(),
            "dpi":            self._combo_dpi.currentText(),
            "abrir_carpeta":  self._abrir_estado,
        }

    def _aplicar_a_campos(self, d: dict):
        self._inp_tess.setText(d.get("tesseract_path", ""))
        self._inp_pop.setText(d.get("poppler_path", ""))
        self._inp_out.setText(d.get("output_dir", ""))
        idx = self._combo_tema.findText(d.get("tema", "Oscuro"))
        if idx >= 0:
            self._combo_tema.setCurrentIndex(idx)
        self._combo_salida.setCurrentText(d.get("modo_salida", "ambos"))
        self._combo_lang.setCurrentText(d.get("lang", "spa+eng"))
        self._combo_dpi.setCurrentText(d.get("dpi", "300"))
        self._abrir_estado = bool(d.get("abrir_carpeta", True))
        self._actualizar_switch()

    # ── Guardar ──────────────────────────────────────────────────
    def _guardar(self):
        tema_ant      = self._cfg.get("tema", "Oscuro")
        nueva_cfg     = self._leer_campos()
        self._cfg     = nueva_cfg
        save_config(nueva_cfg)
        self.config_guardada.emit(nueva_cfg)
        if nueva_cfg["tema"] != tema_ant:
            self.tema_cambiado.emit(nueva_cfg["tema"])
        self.accept()

    # ── CORRECCIÓN 5: Restablecer desde config_default.json ──────
    def _restablecer(self):
        resp = QMessageBox.question(
            self, "Restablecer valores de fábrica",
            "Se reemplazará la configuración actual con los valores\n"
            "de fábrica (config_default.json) y se guardará.\n\n"
            "¿Continuar?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if resp != QMessageBox.StandardButton.Yes:
            return

        tema_ant  = self._cfg.get("tema", "Oscuro")
        defaults  = reset_to_defaults()   # escribe en disco y devuelve dict
        self._cfg = defaults
        self._aplicar_a_campos(defaults)

        # Emitir señales para que MainWindow actualice tema y estilos
        self.config_guardada.emit(defaults)
        if defaults.get("tema", "Oscuro") != tema_ant:
            self.tema_cambiado.emit(defaults["tema"])

        QMessageBox.information(
            self, "Restablecer",
            "Valores de fábrica aplicados y guardados correctamente.")

    # ── Centrar sobre la ventana padre ───────────────────────────
    def _centrar(self):
        if self.parent():
            pr = self.parent().geometry()
            self.adjustSize()
            self.setGeometry(
                pr.x() + (pr.width()  - self.width())  // 2,
                pr.y() + (pr.height() - self.height()) // 2,
                self.width(), self.height())



