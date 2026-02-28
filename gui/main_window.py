# gui/main_window.py  — Fase 1 finalizada
# Correcciones aplicadas:
#   1. QTreeWidget/QHeaderView forzados con colores del tema (sin fondo blanco)
#   2. Botones Marcar/Desmarcar/Quitar en Toolbar Y menú Editar
#   3. Checkboxes: solo procesa marcados, todos marcados al añadir
#   4. Estado "Detenido" en naranja; "Cancelado" en gris para los que no llegaron
#   5. Timer de tiempo transcurrido en status bar durante el proceso

import os, time
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QSplitter, QLabel,
    QTextEdit, QProgressBar, QFileDialog, QMessageBox,
    QToolBar, QTreeWidget, QTreeWidgetItem, QHeaderView, QPushButton
)
from PyQt6.QtGui import (
    QAction, QFont, QIcon, QPainter, QColor, QPen, QBrush,
    QDragEnterEvent, QDropEvent
)
from PyQt6.QtCore import Qt, QSize, QTimer, QSettings

from core.ocr_engine import OCRWorker
from core.utils import load_config
from assets.themes.themes import get_theme
from gui.config_dialog import ConfigDialog
from gui.icons import icono

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def cargar_icono():
    for nombre in ("LocalOCR.ico", "LocalOCR.png", "icon.ico", "icon.png"):
        ruta = os.path.join(BASE_DIR, "assets", "icons", nombre)
        if os.path.exists(ruta):
            return QIcon(ruta)
    return QIcon()


# ── Paletas de colores por tema ───────────────────────────────────
PALETAS = {
    "Oscuro": {
        "bg":     "#1e1e1e",
        "fg":     "#eff0f1",
        "brd":    "#3a3a3a",
        "head":   "#2d2d2d",
        "alt":    "#252525",
        "acento": "#3c7bd4",
        "hover":  "#2a5fa8",   # azul más oscuro al hover
    },
    "Selva": {
        "bg":     "#0a1a0a",
        "fg":     "#d0e0d0",
        "brd":    "#1a3a1a",
        "head":   "#122a12",
        "alt":    "#0d200d",
        "acento": "#3d7a3d",
        "hover":  "#ff6b2b",   # naranja lava al hover (el volcán 🌋)
    },
    "Claro": {
        "bg":     "#f5f5f5",
        "fg":     "#1a1a1a",
        "brd":    "#cccccc",
        "head":   "#e8e8e8",
        "alt":    "#fafafa",
        "acento": "#8e44ad",
        "hover":  "#6c3483",   # morado oscuro al hover
    },
}


class PreviewPlaceholder(QWidget):
    """
    Visor de documentos.
    Fase 1: placeholder con flecha upload dibujada con QPainter.
    Fase 2: reemplazar paintEvent por carga real de PDF/imagen.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(220)
        self._acento = "#3c7bd4"
        self._archivo = None  # ruta del archivo seleccionado

    def set_acento(self, color: str):
        self._acento = color
        self.update()

    def set_archivo(self, ruta):
        self._archivo = ruta
        self.update()

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        w, h = self.width(), self.height()

        # Marco punteado
        p.setPen(QPen(QColor(self._acento), 1.5, Qt.PenStyle.DashLine))
        p.drawRoundedRect(6, 6, w - 12, h - 12, 10, 10)

        if self._archivo:
            # Fase 1: solo muestra nombre del archivo seleccionado
            p.setFont(QFont("Segoe UI", 9))
            p.setPen(QColor(self._acento))
            nombre = os.path.basename(self._archivo)
            p.drawText(10, 0, w - 20, h,
                       Qt.AlignmentFlag.AlignCenter,
                       f"Vista previa:\n{nombre}\n\n[ Disponible en Fase 2 ]")
        else:
            # Flecha upload
            cx, cy = w // 2, h // 2 - 16
            ah, aw, sw = 52, 40, 14
            tip_y  = cy - ah // 2
            base_y = cy + ah // 4

            p.setPen(QPen(QColor(self._acento), 2.5))
            p.drawLine(cx,         tip_y,  cx - aw//2, base_y)
            p.drawLine(cx,         tip_y,  cx + aw//2, base_y)
            p.drawLine(cx - aw//2, base_y, cx - sw//2, base_y)
            p.drawLine(cx + aw//2, base_y, cx + sw//2, base_y)
            p.drawLine(cx - sw//2, base_y, cx - sw//2, cy + ah//2)
            p.drawLine(cx + sw//2, base_y, cx + sw//2, cy + ah//2)
            p.drawLine(cx - sw//2, cy + ah//2, cx + sw//2, cy + ah//2)

            p.setFont(QFont("Segoe UI", 9))
            p.setPen(QColor(self._acento))
            by = cy + ah // 2
            p.drawText(0, by + 14, w, 22,
                       Qt.AlignmentFlag.AlignCenter,
                       "Selecciona un archivo en la lista")
            p.drawText(0, by + 34, w, 20,
                       Qt.AlignmentFlag.AlignCenter,
                       "o arrastra archivos aquí")
        p.end()


class MainWindow(QMainWindow):
    def __init__(self, app):
        super().__init__()
        self._app          = app
        self._cfg          = load_config()
        self._worker       = None
        self._is_stopping  = False
        self._items_map    = {}
        self._active_items = []
        self._current_idx  = 0
        self._t0           = 0.0

        self._timer = QTimer(self)
        self._timer.timeout.connect(self._tick_timer)

        self.setWindowTitle("Local OCR Pro")
        self.setMinimumSize(350, 500)
        self.setWindowIcon(cargar_icono())
        self._settings = QSettings("Emmanuel", "ProyectoOCR")

        # Construir widgets antes de _build_ui
        self._texto   = QTextEdit()
        self._preview = PreviewPlaceholder()

        self._tree = QTreeWidget()
        self._tree.setColumnCount(3)
        self._tree.setHeaderLabels(["Archivo", "Estado", "Ruta Completa"])
        self._tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self._tree.setAlternatingRowColors(True)
        self._tree.setRootIsDecorated(False)
        self._tree.header().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self._tree.header().resizeSection(1, 110)
        self._tree.setColumnHidden(2, True)
        self._tree.currentItemChanged.connect(self._on_item_seleccionado)
        self._tree.setAcceptDrops(True)
        self._tree.dragEnterEvent = self._drag_enter
        self._tree.dragMoveEvent  = lambda e: e.accept()
        self._tree.dropEvent      = self._drop_archivos

        self._build_ui()
        self._aplicar_estilos_tema()
        self._actualizar_iconos_tema()

    def closeEvent(self, event):
        self._settings.setValue("splitter_state", self._splitter.saveState())
        self._settings.setValue("window_geometry", self.saveGeometry())
        super().closeEvent(event)

    # ── Estilos de tema ──────────────────────────────────────────
    def _aplicar_estilos_tema(self):
        tema = self._cfg.get("tema", "Oscuro")
        p    = PALETAS.get(tema, PALETAS["Oscuro"])
        self._preview.set_acento(p["acento"])

        self.setStyleSheet(f"""
            QMainWindow, QDialog, QWidget {{
                background-color: {p['bg']};
                color: {p['fg']};
                font-family: 'Segoe UI', Arial, sans-serif;
                font-size: 13px;
            }}
            QMenuBar {{
                background-color: {p['head']};
                color: {p['fg']};
                border-bottom: 1px solid {p['brd']};
                padding: 2px;
            }}
            QMenuBar::item:selected {{
                background-color: {p['acento']};
                color: white;
                border-radius: 3px;
            }}
            QMenu {{
                background-color: {p['bg']};
                color: {p['fg']};
                border: 1px solid {p['brd']};
            }}
            QMenu::item:selected {{
                background-color: {p['acento']};
                color: white;
            }}
            QToolBar {{
                background-color: {p['head']};
                border-bottom: 2px solid {p['brd']};
                spacing: 4px;
                padding: 3px 6px;
            }}
            QToolButton {{
                background-color: transparent;
                color: {p['fg']};
                border-radius: 5px;
                padding: 4px 8px;
            }}
            QToolButton:hover {{
                background-color: {p['hover']};
                color: white;
            }}
            QPushButton {{
                background-color: {p['acento']};
                color: white;
                border: none;
                border-radius: 5px;
                padding: 6px 16px;
                font-weight: bold;
            }}
            QPushButton:hover  {{ background-color: {p['hover']}; color: white; }}
            QPushButton:disabled {{ background-color: {p['brd']}; color: #777; }}
            QTreeWidget {{
                background-color: {p['bg']};
                alternate-background-color: {p['alt']};
                color: {p['fg']};
                border: 1px solid {p['brd']};
                outline: 0;
                show-decoration-selected: 1;
            }}
            QTreeWidget::item {{
                padding: 3px 0;
                color: {p['fg']};
            }}
            QTreeWidget::item:selected {{
                background-color: {p['acento']};
                color: white;
            }}
            QTreeWidget::item:hover:!selected {{
                background-color: {p['alt']};
            }}
            QHeaderView {{
                background-color: {p['head']};
                color: {p['fg']};
            }}
            QHeaderView::section {{
                background-color: {p['head']};
                color: {p['fg']};
                padding: 5px 8px;
                border: 1px solid {p['brd']};
                font-weight: bold;
            }}
            QHeaderView::section:checked {{
                background-color: {p['acento']};
            }}
            QTextEdit, QPlainTextEdit {{
                background-color: {p['bg']};
                color: {p['fg']};
                border: 1px solid {p['brd']};
                border-radius: 4px;
                font-family: 'Consolas', monospace;
                font-size: 12px;
                padding: 4px;
            }}
            QLineEdit {{
                background-color: {p['bg']};
                color: {p['fg']};
                border: 1px solid {p['brd']};
                border-radius: 4px;
                padding: 4px 6px;
            }}
            QComboBox {{
                background-color: {p['bg']};
                color: {p['fg']};
                border: 1px solid {p['brd']};
                border-radius: 5px;
                padding: 5px 8px;
            }}
            QComboBox QAbstractItemView {{
                background-color: {p['bg']};
                color: {p['fg']};
                selection-background-color: {p['acento']};
                selection-color: white;
            }}
            QGroupBox {{
                border: 1px solid {p['brd']};
                border-radius: 6px;
                margin-top: 12px;
                padding-top: 8px;
                color: {p['fg']};
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 4px;
            }}
            QScrollBar:vertical {{
                background: {p['bg']};
                width: 10px;
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {p['brd']};
                border-radius: 5px;
                min-height: 28px;
            }}
            QScrollBar::handle:vertical:hover {{ background: {p['acento']}; }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
            QProgressBar {{
                background: {p['alt']};
                border: 1px solid {p['brd']};
                border-radius: 4px;
                height: 14px;
                text-align: center;
                font-size: 11px;
                color: {p['fg']};
            }}
            QProgressBar::chunk {{
                background-color: {p['acento']};
                border-radius: 4px;
            }}
            QStatusBar {{
                background-color: {p['head']};
                color: {p['fg']};
                font-size: 11px;
                border-top: 1px solid {p['brd']};
            }}
            QSplitter::handle {{ background-color: {p['brd']}; }}
            QDialogButtonBox QPushButton {{ padding: 6px 20px; }}
            QToolTip {{
                background-color: {p['head']};
                color: {p['fg']};
                border: 1px solid {p['brd']};
            }}
        """)

    # ── Build UI ─────────────────────────────────────────────────
    def _build_ui(self):
        self.a_add = QAction(icono("add"), "Añadir Archivos", self)
        self.a_add.setShortcut("Ctrl+O")
        self.a_add.setToolTip("Añadir archivos a la lista (Ctrl+O)")
        self.a_add.triggered.connect(self._abrir)

        self.a_open_dir = QAction(icono("folder"), "Carpeta de Salida", self)
        self.a_open_dir.setToolTip("Abrir carpeta de resultados")
        self.a_open_dir.triggered.connect(self._abrir_carpeta_salida)

        self.a_limpiar_todo = QAction(icono("trash"), "Limpiar Todo", self)
        self.a_limpiar_todo.setToolTip("Borrar lista y texto extraído")
        self.a_limpiar_todo.triggered.connect(self._limpiar_todo)

        self.a_run = QAction(icono("play"), "Procesar", self)
        self.a_run.setShortcut("F5")
        self.a_run.setToolTip("Iniciar OCR de archivos marcados (F5)")
        self.a_run.setEnabled(False)
        self.a_run.triggered.connect(self._procesar_lote)

        self.a_stop = QAction(icono("stop"), "Detener", self)
        self.a_stop.setToolTip("Detener el proceso actual")
        self.a_stop.setEnabled(False)
        self.a_stop.triggered.connect(self._detener)

        self.a_sel_all = QAction(icono("check_all"), "Marcar Todos", self)
        self.a_sel_all.setToolTip("Marcar todos los archivos")
        self.a_sel_all.triggered.connect(
            lambda: self._set_checks(Qt.CheckState.Checked))

        self.a_desel_all = QAction(icono("uncheck_all"), "Desmarcar Todos", self)
        self.a_desel_all.setToolTip("Desmarcar todos los archivos")
        self.a_desel_all.triggered.connect(
            lambda: self._set_checks(Qt.CheckState.Unchecked))

        self.a_quitar = QAction(icono("remove"), "Quitar Marcados", self)
        self.a_quitar.setToolTip("Eliminar de la lista los archivos marcados")
        self.a_quitar.triggered.connect(self._quitar_seleccionados)

        self.a_copy_all = QAction("Copiar Todo", self)
        self.a_copy_all.triggered.connect(
            lambda: self._app.clipboard().setText(self._texto.toPlainText()))
        self.a_clear_txt = QAction("Limpiar Pantalla", self)
        self.a_clear_txt.triggered.connect(self._texto.clear)

        # Menús
        mb = self.menuBar()
        m_arch = mb.addMenu("&Archivo")
        m_arch.addActions([self.a_add, self.a_open_dir, self.a_limpiar_todo])
        m_arch.addSeparator()
        m_arch.addAction("Salir", self.close)

        m_edit = mb.addMenu("&Editar")
        m_edit.addActions([self.a_sel_all, self.a_desel_all, self.a_quitar])
        m_edit.addSeparator()
        m_edit.addActions([self.a_copy_all, self.a_clear_txt])

        m_proc = mb.addMenu("&Procesar")
        m_proc.addActions([self.a_run, self.a_stop])

        mb.addMenu("&Configuración").addAction(
            "Preferencias...", self._abrir_config)
        mb.addMenu("Ay&uda").addAction("Acerca de...", self._acerca)

        # Toolbar
        tb = self.addToolBar("Acciones")
        tb.setMovable(False)
        tb.setIconSize(QSize(28, 28))
        tb.addActions([self.a_add, self.a_open_dir, self.a_limpiar_todo])
        tb.addSeparator()
        tb.addActions([self.a_run, self.a_stop])
        tb.addSeparator()
        tb.addActions([self.a_sel_all, self.a_desel_all, self.a_quitar])

        # Cuerpo central
        central = QWidget()
        self.setCentralWidget(central)
        lay = QVBoxLayout(central)
        lay.setContentsMargins(6, 4, 6, 4)
        lay.setSpacing(4)

        self._splitter = QSplitter(Qt.Orientation.Horizontal)

        left = QWidget()
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.setSpacing(4)
        self._tree.setMinimumHeight(160)
        left_lay.addWidget(self._tree, 2)
        left_lay.addWidget(self._preview, 3)
        self._splitter.addWidget(left)

        right = QWidget()
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(4)
        lbl = QLabel("Texto extraído:")
        lbl.setFont(QFont("Segoe UI", 9))
        right_lay.addWidget(lbl)
        right_lay.addWidget(self._texto)
        btn_row = QHBoxLayout()
        btn_cop = QPushButton("Copiar todo")
        btn_cop.clicked.connect(
            lambda: self._app.clipboard().setText(self._texto.toPlainText()))
        btn_lim = QPushButton("Limpiar texto")
        btn_lim.clicked.connect(self._texto.clear)
        btn_row.addWidget(btn_cop)
        btn_row.addWidget(btn_lim)
        btn_row.addStretch()
        right_lay.addLayout(btn_row)
        self._splitter.addWidget(right)

        self._splitter.setSizes([420, 780])
        self._splitter.setStretchFactor(1, 1)
        lay.addWidget(self._splitter)

        # Restaurar geometría guardada
        state = self._settings.value("splitter_state")
        if state:
            self._splitter.restoreState(state)
        geo = self._settings.value("window_geometry")
        if geo:
            self.restoreGeometry(geo)

        # Status bar
        self._status_lbl = QLabel("Listo.")
        self._time_lbl   = QLabel("")
        self._time_lbl.setFixedWidth(310)
        self._progress = QProgressBar()
        self._progress.setFixedWidth(190)
        self._progress.hide()

        sb = self.statusBar()
        sb.addWidget(self._status_lbl, 1)
        sb.addPermanentWidget(self._time_lbl)
        sb.addPermanentWidget(self._progress)

    # ── Drag & Drop ──────────────────────────────────────────────
    def _drag_enter(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
        else:
            event.ignore()

    def _drop_archivos(self, event):
        exts = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}
        n = 0
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if os.path.splitext(path)[1].lower() in exts:
                if path not in self._items_map:
                    item = QTreeWidgetItem(
                        [os.path.basename(path), "Pendiente", path])
                    item.setCheckState(0, Qt.CheckState.Checked)
                    self._tree.addTopLevelItem(item)
                    self._items_map[path] = item
                    n += 1
        if n:
            self.a_run.setEnabled(True)
            self._status(f"{n} archivo(s) añadido(s) por arrastre.")
        event.acceptProposedAction()

    # ── Árbol ────────────────────────────────────────────────────
    def _set_checks(self, state):
        for i in range(self._tree.topLevelItemCount()):
            self._tree.topLevelItem(i).setCheckState(0, state)

    def _on_item_seleccionado(self, current, _previous):
        if current:
            ruta = current.text(2)
            self._preview.set_archivo(ruta if ruta else None)

    def _abrir(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Añadir archivos",
            self._cfg.get("output_dir", ""),
            "Documentos (*.pdf *.png *.jpg *.jpeg *.tiff *.bmp);;"
            "PDF (*.pdf);;Imágenes (*.png *.jpg *.jpeg *.tiff *.bmp)")
        if paths:
            n = 0
            for p in paths:
                if p not in self._items_map:
                    item = QTreeWidgetItem(
                        [os.path.basename(p), "Pendiente", p])
                    item.setCheckState(0, Qt.CheckState.Checked)
                    self._tree.addTopLevelItem(item)
                    self._items_map[p] = item
                    n += 1
            if n:
                self.a_run.setEnabled(True)
                self._status(f"{n} archivo(s) añadido(s).")

    def _quitar_seleccionados(self):
        root = self._tree.invisibleRootItem()
        for i in range(self._tree.topLevelItemCount() - 1, -1, -1):
            item = self._tree.topLevelItem(i)
            if item.checkState(0) == Qt.CheckState.Checked:
                self._items_map.pop(item.text(2), None)
                root.removeChild(item)
        if self._tree.topLevelItemCount() == 0:
            self.a_run.setEnabled(False)
            self._preview.set_archivo(None)

    def _limpiar_todo(self):
        self._items_map.clear()
        self._tree.clear()
        self._texto.clear()
        self._preview.set_archivo(None)
        self.a_run.setEnabled(False)
        self._status("Listo.")

    # ── Procesar lote ────────────────────────────────────────────
    def _procesar_lote(self):
        self._active_items = [
            self._tree.topLevelItem(i)
            for i in range(self._tree.topLevelItemCount())
            if self._tree.topLevelItem(i).checkState(0) == Qt.CheckState.Checked
        ]
        if not self._active_items:
            return

        for item in self._active_items:
            self._set_estado(item, "En cola...", "#555555")

        self._current_idx = 0
        self._is_stopping = False
        self._t0          = time.time()
        self.a_run.setEnabled(False)
        self.a_stop.setEnabled(True)
        self.a_add.setEnabled(False)
        self._progress.setValue(0)
        self._progress.show()
        self._timer.start(1000)
        self._procesar_siguiente()

    def _procesar_siguiente(self):
        if self._is_stopping or self._current_idx >= len(self._active_items):
            self._finalizar_lote(success=not self._is_stopping)
            return

        item  = self._active_items[self._current_idx]
        total = len(self._active_items)
        self._set_estado(item, "En curso...", "#3498db")
        self._status(f"Procesando {self._current_idx+1}/{total}: {item.text(0)}")

        self._worker = OCRWorker(item.text(2), dict(self._cfg))
        self._worker.progreso.connect(self._progress.setValue)
        self._worker.resultado.connect(
            lambda t, it=item: self._on_resultado(t, it))
        self._worker.error.connect(
            lambda msg, it=item: self._on_error_worker(msg, it))
        self._worker.terminado.connect(
            lambda dur, it=item: self._on_archivo_terminado(dur, it))
        self._worker.start()

    def _on_resultado(self, texto, item):
        self._texto.append(
            f"\n{'─'*46}\n  {item.text(0)}\n{'─'*46}\n{texto}\n")

    def _on_error_worker(self, msg, item):
        self._set_estado(item, "Error", "#c0392b")
        self._texto.append(f"\n[ERROR] {item.text(0)}:\n{msg}\n")

    def _on_archivo_terminado(self, duracion, item):
        if self._is_stopping:
            return
        if item.text(1) != "Error":
            self._set_estado(item, f"OK  {duracion:.1f}s", "#27ae60")
        self._current_idx += 1
        self._procesar_siguiente()

    def _set_estado(self, item, texto, color):
        item.setText(1, texto)
        item.setBackground(1, QBrush(QColor(color)))
        item.setForeground(1, QBrush(QColor("white")))

    def _detener(self):
        self._is_stopping = True
        if self._worker:
            self._worker.detener()
        if 0 <= self._current_idx < len(self._active_items):
            self._set_estado(
                self._active_items[self._current_idx],
                "Detenido", "#e67e22")
        for i in range(self._current_idx + 1, len(self._active_items)):
            self._set_estado(self._active_items[i], "Cancelado", "#7f8c8d")
        self._finalizar_lote(success=False)

    def _finalizar_lote(self, success):
        self._timer.stop()
        self.a_run.setEnabled(True)
        self.a_stop.setEnabled(False)
        self.a_add.setEnabled(True)
        self._progress.hide()
        self._worker    = None
        elapsed         = time.time() - self._t0
        if success:
            n = len(self._active_items)
            self._status(f"✨ Completado — {n} archivo(s) en {elapsed:.1f}s")
            self._play_sound()
            self._verificar_apertura_carpeta()
        else:
            self._status("🛑 Detenido.")
        self._time_lbl.setText("")

    def _verificar_apertura_carpeta(self):
        modo   = self._cfg.get("modo_salida", "ambos")
        outdir = self._cfg.get("output_dir", "")
        if modo != "texto" and self._cfg.get("abrir_carpeta") and outdir:
            if os.path.isdir(outdir):
                try:
                    os.startfile(outdir)
                except Exception:
                    pass

    def _tick_timer(self):
        elapsed = time.time() - self._t0
        total   = len(self._active_items)
        hecho   = self._current_idx
        if hecho > 0 and total > 0:
            est      = elapsed / (hecho / total)
            restante = max(0.0, est - elapsed)
            self._time_lbl.setText(
                f"{hecho}/{total}  ·  {self._fmt(elapsed)}"
                f"  ~{self._fmt(restante)} restante")
        else:
            self._time_lbl.setText(f"Transcurrido: {self._fmt(elapsed)}")

    def _abrir_config(self):
        dlg = ConfigDialog(self, self._cfg)
        dlg.config_guardada.connect(self._on_config_updated)
        dlg.tema_cambiado.connect(
            lambda t: (
                self._app.setStyleSheet(get_theme(t)),
                self._on_config_updated({**self._cfg, "tema": t})
            ))
        dlg.exec()

    def _on_config_updated(self, cfg):
        self._cfg = cfg
        self._aplicar_estilos_tema()
        self._actualizar_iconos_tema()

    def _actualizar_iconos_tema(self):
        p = PALETAS.get(self._cfg.get("tema", "Oscuro"), PALETAS["Oscuro"])
        c = p["fg"]
        self.a_add.setIcon(icono("add",              c))
        self.a_open_dir.setIcon(icono("folder",      c))
        self.a_limpiar_todo.setIcon(icono("trash",   c))
        self.a_run.setIcon(icono("play",              p["acento"]))
        self.a_stop.setIcon(icono("stop",             "#e74c3c"))
        self.a_sel_all.setIcon(icono("check_all",    c))
        self.a_desel_all.setIcon(icono("uncheck_all",c))
        self.a_quitar.setIcon(icono("remove",         c))

    def _abrir_carpeta_salida(self):
        outdir = self._cfg.get("output_dir", os.path.expanduser("~"))
        if os.path.isdir(outdir):
            try:
                os.startfile(outdir)
            except Exception:
                pass
        else:
            QMessageBox.warning(self, "Carpeta no encontrada",
                f"La carpeta configurada no existe:\n{outdir}\n\n"
                "Cámbiala en Configuración › Preferencias.")

    def _status(self, txt):
        self._status_lbl.setText(txt)

    def _fmt(self, seg):
        seg = int(seg)
        m, s = divmod(seg, 60)
        h, m = divmod(m, 60)
        if h:  return f"{h}h {m:02d}m {s:02d}s"
        if m:  return f"{m}m {s:02d}s"
        return f"{s}s"

    def _play_sound(self):
        try:
            import winsound
            winsound.PlaySound(
                "SystemAsterisk", winsound.SND_ALIAS | winsound.SND_ASYNC)
        except Exception:
            pass

    def _acerca(self):
        QMessageBox.information(self, "Acerca de Local OCR Pro",
            "Local OCR Pro\n\n"
            "Convierte PDF e Imágenes a Texto Editable\n\n"
            "Autor: Emmanuel Arroyo\n\n"
            "Desarrollado con IA — Claude  •  Gemini\n\n"
            "Tesseract OCR  |  Poppler  |  pdf2image\n"
            "pytesseract  |  reportlab  |  Pillow  |  PyQt6")
