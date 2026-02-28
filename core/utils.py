# core/utils.py
# Manejo de configuracion — usa JSON limpio en lugar de INI
# Separacion estricta: este modulo no sabe nada de PyQt6

import os
import json
import shutil

# ── Rutas base ────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH  = os.path.join(os.path.expanduser("~"), ".localocr_config.json")
DEFAULT_PATH = os.path.join(BASE_DIR, "assets", "config_default.json")

# ── Carpeta Descargas real ────────────────────────────────────────
def get_downloads_dir() -> str:
    try:
        import winreg
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders")
        val, _ = winreg.QueryValueEx(
            key, "{374DE290-123F-4565-9164-39C4925E467B}")
        return val
    except Exception:
        return os.path.join(os.path.expanduser("~"), "Downloads")


# ── Carga / Guardado ─────────────────────────────────────────────
def load_config() -> dict:
    """Carga la config del usuario. Si no existe, crea desde defaults."""
    defaults = load_defaults()
    if not os.path.exists(CONFIG_PATH):
        # Primera vez — rellenar output_dir con Descargas reales
        if not defaults.get("output_dir"):
            defaults["output_dir"] = get_downloads_dir()
        save_config(defaults)
        return defaults

    try:
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        # Rellenar claves faltantes con defaults (por si se agrego nueva clave)
        for k, v in defaults.items():
            cfg.setdefault(k, v)
        if not cfg.get("output_dir"):
            cfg["output_dir"] = get_downloads_dir()
        return cfg
    except Exception:
        return defaults


def save_config(cfg: dict):
    """Guarda la config activa del usuario en disco."""
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=4, ensure_ascii=False)


def load_defaults() -> dict:
    """Lee config_default.json — nunca se modifica."""
    try:
        with open(DEFAULT_PATH, "r", encoding="utf-8") as f:
            d = json.load(f)
        if not d.get("output_dir"):
            d["output_dir"] = get_downloads_dir()
        return d
    except Exception:
        return {
            "tema":           "Oscuro",
            "output_dir":     get_downloads_dir(),
            "tesseract_path": r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            "poppler_path":   r"C:\Program Files\ChuyOCR\poppler-25.12.0\Library\bin",
            "lang":           "spa+eng",
            "dpi":            "300",
            "modo_salida":    "ambos", # Cambiado a minúscula para coincidir con el combo
            "abrir_carpeta":  True,
        }   


def reset_to_defaults() -> dict:
    """
    Copia config_default.json -> config activa del usuario.
    Devuelve el dict resultante.
    """
    defaults = load_defaults()
    save_config(defaults)
    return defaults


# ── Helpers ──────────────────────────────────────────────────────
EXTENSIONES_VALIDAS = {".pdf", ".png", ".jpg", ".jpeg", ".tiff", ".bmp"}

def es_archivo_valido(ruta: str) -> bool:
    return os.path.splitext(ruta)[1].lower() in EXTENSIONES_VALIDAS


def nombre_salida(outdir: str, base: str) -> str:
    """Genera ruta _001, _002... sin sobreescribir."""
    n = 1
    while True:
        path = os.path.join(outdir, f"{base}_{n:03d}.pdf")
        if not os.path.exists(path):
            return path
        n += 1
