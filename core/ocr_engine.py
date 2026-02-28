# core/ocr_engine.py
# Motor OCR — Fase 1: simulacion con worker real de QThread
# ─────────────────────────────────────────────────────────────────
# FASE 2: Reemplaza el bloque marcado SIMULACION con:
#
# Tesseract:
#   import pytesseract
#   from pdf2image import convert_from_path
#   pytesseract.pytesseract.tesseract_cmd = cfg["tesseract_path"]
#   imgs = convert_from_path(ruta, dpi=int(cfg["dpi"]),
#                            poppler_path=cfg["poppler_path"])
#   texto = "\n\n".join(
#       pytesseract.image_to_string(img, lang=cfg["lang"])
#       for img in imgs)
#
# EasyOCR:
#   import easyocr
#   reader = easyocr.Reader(["es", "en"])
#   resultado = reader.readtext(ruta, detail=0)
#   texto = "\n".join(resultado)
# ─────────────────────────────────────────────────────────────────

import time
from PyQt6.QtCore import QThread, pyqtSignal


class OCRWorker(QThread):
    """
    Worker que corre en hilo separado para no congelar la UI.

    Senales:
        progreso  (int)   — porcentaje 0-100
        resultado (str)   — texto extraido (o simulado en Fase 1)
        error     (str)   — mensaje de error
        terminado (float) — segundos totales que tomo el proceso
    """
    progreso  = pyqtSignal(int)
    resultado = pyqtSignal(str)
    error     = pyqtSignal(str)
    terminado = pyqtSignal(float)   # emite duracion en segundos

    def __init__(self, ruta_archivo: str, cfg: dict):
        super().__init__()
        self.ruta_archivo = ruta_archivo
        self.cfg          = cfg
        self._detener     = False

    def detener(self):
        self._detener = True

    def run(self):
        t0 = time.time()
        try:
            nombre = os.path.basename(self.ruta_archivo)

            # ═══════════════════════════════════════════════════
            #  SIMULACION — Reemplazar en Fase 2
            # ═══════════════════════════════════════════════════
            pasos = 10
            for i in range(pasos):
                if self._detener:
                    self.error.emit("Proceso detenido por el usuario.")
                    return
                time.sleep(0.3)
                self.progreso.emit(int((i + 1) / pasos * 100))

            texto = (
                f"[ Texto extraido de: {nombre} ]\n\n"
                "Lorem ipsum dolor sit amet, consectetur adipiscing elit.\n"
                "Sed do eiusmod tempor incididunt ut labore et dolore magna.\n"
                "Ut enim ad minim veniam, quis nostrud exercitation.\n\n"
                "-- Fase 2: aqui aparecera el texto real de Tesseract/EasyOCR --"
            )
            # ═══════════════════════════════════════════════════
            #  FIN SIMULACION
            # ═══════════════════════════════════════════════════

            self.resultado.emit(texto)

        except Exception as e:
            self.error.emit(f"Error inesperado: {e}")
        finally:
            duracion = time.time() - t0
            self.terminado.emit(duracion)


# import faltante dentro del metodo run
import os
