# gui/icons.py
# Iconos vectoriales dibujados con QPainter.
# Ventaja: color ajustable por tema, sin dependencia de archivos externos,
# se ven igual en Oscuro, Claro y Selva.
#
# Uso:
#   from gui.icons import icono
#   accion = QAction(icono("add", "#e0e0e0"), "Añadir", self)
#   # Al cambiar tema: accion.setIcon(icono("add", nuevo_color))

from PyQt6.QtGui import QIcon, QPixmap, QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QRect, QPointF


def icono(nombre: str, color: str = "#e0e0e0", size: int = 22) -> QIcon:
    """Devuelve un QIcon vectorial del tamaño indicado."""
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    _dibujar(p, nombre, QColor(color), size)
    p.end()
    return QIcon(pix)


def _dibujar(p: QPainter, nombre: str, c: QColor, s: int):
    pen = QPen(c, max(1.5, s * 0.07))
    pen.setCapStyle(Qt.PenCapStyle.RoundCap)
    pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.BrushStyle.NoBrush)

    m = s * 0.15   # margen
    w = s - 2*m    # ancho útil

    if nombre == "add":          _add(p, c, m, w, s)
    elif nombre == "folder":     _folder(p, c, m, w, s)
    elif nombre == "trash":      _trash(p, c, m, w, s)
    elif nombre == "play":       _play(p, c, m, w, s)
    elif nombre == "stop":       _stop(p, c, m, w, s)
    elif nombre == "check_all":  _check_all(p, c, m, w, s)
    elif nombre == "uncheck_all":_uncheck_all(p, c, m, w, s)
    elif nombre == "remove":     _remove(p, c, m, w, s)


def _add(p, c, m, w, s):
    # Carpeta con signo +
    p.drawRoundedRect(int(m), int(m + w*0.2), int(w), int(w*0.75), 2, 2)
    p.drawLine(int(m), int(m + w*0.35), int(m + w*0.45), int(m + w*0.35))
    p.drawLine(int(m + w*0.45), int(m + w*0.2), int(m + w*0.45), int(m + w*0.35))
    # Cruz +
    cx, cy = int(s * 0.72), int(s * 0.72)
    r = int(s * 0.22)
    p.setBrush(QColor(c))
    p.drawEllipse(cx - r, cy - r, 2*r, 2*r)
    p.setBrush(Qt.BrushStyle.NoBrush)
    wp = QPen(QColor("#000000" if c.lightness() > 128 else "#ffffff"),
              max(1.5, s * 0.07))
    wp.setCapStyle(Qt.PenCapStyle.RoundCap)
    p.setPen(wp)
    p.drawLine(cx, cy - r + 3, cx, cy + r - 3)
    p.drawLine(cx - r + 3, cy, cx + r - 3, cy)
    p.setPen(QPen(c, max(1.5, s * 0.07)))

def _folder(p, c, m, w, s):
    p.drawRoundedRect(int(m), int(m + w*0.2), int(w), int(w*0.75), 2, 2)
    p.drawLine(int(m), int(m + w*0.35), int(m + w*0.45), int(m + w*0.35))
    p.drawLine(int(m + w*0.45), int(m + w*0.2), int(m + w*0.45), int(m + w*0.35))

def _trash(p, c, m, w, s):
    # Cuerpo
    p.drawRoundedRect(int(m + w*0.1), int(m + w*0.25), int(w*0.8), int(w*0.7), 2, 2)
    # Tapa
    p.drawLine(int(m), int(m + w*0.22), int(m + w), int(m + w*0.22))
    p.drawRoundedRect(int(m + w*0.3), int(m + w*0.05), int(w*0.4), int(w*0.18), 2, 2)
    # Líneas internas
    p.drawLine(int(m + w*0.38), int(m + w*0.4), int(m + w*0.38), int(m + w*0.83))
    p.drawLine(int(m + w*0.62), int(m + w*0.4), int(m + w*0.62), int(m + w*0.83))

def _play(p, c, m, w, s):
    path = QPainterPath()
    path.moveTo(m + w*0.2, m)
    path.lineTo(m + w*0.2, m + w)
    path.lineTo(m + w*0.95, m + w*0.5)
    path.closeSubpath()
    p.fillPath(path, QBrush(c))

def _stop(p, c, m, w, s):
    p.setBrush(QBrush(c))
    p.drawRoundedRect(int(m), int(m), int(w), int(w), 3, 3)

def _check_all(p, c, m, w, s):
    # Dos checkmarks apilados
    for dy in (0, w*0.42):
        p.drawRoundedRect(int(m), int(m + dy), int(w), int(w*0.42), 2, 2)
        # Tilde
        x0, y0 = m + w*0.18, m + dy + w*0.22
        p.drawLine(int(x0), int(y0 + w*0.1), int(x0 + w*0.15), int(y0 + w*0.22))
        p.drawLine(int(x0 + w*0.15), int(y0 + w*0.22), int(x0 + w*0.35), int(y0))

def _uncheck_all(p, c, m, w, s):
    # Dos cajas vacías apiladas
    for dy in (0, w*0.42):
        p.drawRoundedRect(int(m), int(m + dy), int(w), int(w*0.42), 2, 2)

def _remove(p, c, m, w, s):
    # Caja con X
    p.drawRoundedRect(int(m), int(m + w*0.12), int(w), int(w*0.75), 2, 2)
    p.drawLine(int(m + w*0.25), int(m + w*0.35), int(m + w*0.75), int(m + w*0.72))
    p.drawLine(int(m + w*0.75), int(m + w*0.35), int(m + w*0.25), int(m + w*0.72))
