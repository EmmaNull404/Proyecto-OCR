## README.md

```markdown
# Proyecto OCR Local en Python

Aplicación de **Reconocimiento Óptico de Caracteres (OCR)** que funciona de forma
local, con interfaz gráfica, diseñada con una arquitectura modular y escalable.

El proyecto separa claramente la lógica de OCR, la interfaz gráfica y los recursos,
facilitando el mantenimiento y futuras mejoras.

---

## ?? Objetivo del proyecto
- Extraer texto desde imágenes de forma local
- No depender de servicios en la nube
- Ofrecer una interfaz gráfica clara y configurable
- Permitir evolución por fases

---

## ?? Arquitectura general

El proyecto sigue una estructura por capas:

- **Core**: lógica de negocio y OCR
- **GUI**: interfaz gráfica y eventos
- **Assets**: recursos, temas y configuración
- **Main**: punto de entrada y orquestación

---

## ??? Estructura del proyecto

```

assets/
+- config_default.json    Configuración base (solo lectura)
+- themes/
+- themes.py           Gestión de temas visuales

core/
+- utils.py               Utilidades generales
+- ocr_engine.py          Motor OCR y procesamiento principal

gui/
+- icons.py               Iconos vectoriales dinámicos
+- config_dialog.py       Ventana de configuración
+- main_window.py         Ventana principal de la aplicación

main.py                    Punto de entrada del sistema

````

---

## ?? Descripción de módulos clave

### `main.py`
- Inicializa la aplicación
- Carga configuración y tema
- Lanza la ventana principal

### `core/ocr_engine.py`
- Ejecuta el proceso OCR
- Emite señales de:
  - progreso
  - resultado
  - error
  - término de proceso
- Preparado para ejecución en segundo plano (fase 2)

### `gui/main_window.py`
- Ventana principal
- Gestión visual del flujo OCR
- Actualización dinámica de iconos y estado

### `gui/config_dialog.py`
- Preferencias del sistema
- Tema, rutas, DPI, idioma
- Emite señales al actualizar configuración

---

## ?? Señales y comunicación
El sistema usa un modelo de **señales** para desacoplar lógica y GUI:

- `progreso(int)`
- `resultado(str)`
- `error(str)`
- `tema_cambiado(str)`
- `config_guardada(dict)`

Esto permite escalar sin romper la interfaz.

---

## ?? Estado del proyecto
- **Fase 1**: Arquitectura base y GUI ? ? Completa
- **Fase 2**: OCR real, threading y mejoras ? ?? Planeada

---

## ?? Ejecución
```bash
python main.py
````

---

## ??? Tecnologías

* Python
* OCR local (Tesseract u otro motor)
* Qt / PyQt (interfaz gráfica)
* JSON para configuración

---

## ?? Autor

Emmanuel

```

---

