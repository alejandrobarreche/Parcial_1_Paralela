# Guía de Uso - Simulador y Procesador de Imágenes Satelitales

(Está en rama Master)

Este repositorio contiene un sistema completo que simula la generación de imágenes satelitales y su procesamiento usando Python y programación concurrente.

Incluye:
- Un **simulador de satélite** que genera archivos con metadatos de imágenes.
- Un **servidor multiproceso** que recolecta, procesa y guarda dichas imágenes.

---

## Estructura del Proyecto

```
Parcial-1/
├── database/                # Entrada de imágenes (generadas por el satélite)
├── database_2/              # Salida de imágenes procesadas
├── main.py                  # Servidor de procesamiento multiproceso
├── satellite_simulator.py   # Simulador de satélite independiente
```

---

## Requisitos

Este proyecto está basado en Python 3. Se recomienda usar un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate  # En Linux/macOS
venv\Scripts\activate     # En Windows
```

Instala dependencias si fueran necesarias (aunque este proyecto no tiene externas).

---

## Ejecución del Proyecto

### 1. Ejecutar el servidor (main)

Este script lanza:
- Receptor de imágenes (subproceso)
- Procesador de imágenes con `multiprocessing.Pool`
- Escritor de imágenes procesadas

```bash
python main.py
```

### 2. Ejecutar el simulador de satélite (por separado)

Este script genera archivos de imágenes en la carpeta `database/`:

```bash
python satellite_simulator.py
```

Puedes iniciar primero el servidor y luego el simulador (o viceversa).

---

## Descripción Técnica del Sistema

### Multiprocessing

El servidor principal (`main.py`) utiliza `multiprocessing` de Python para paralelizar las tareas:

#### Objetos utilizados:

| Elemento | Descripción |
|---------|-------------|
| `multiprocessing.Process` | Permite crear procesos independientes para el receptor, procesador y escritor. |
| `multiprocessing.Queue`   | Colas de comunicación entre procesos. Sirven como espacio de memoria compartida. |
| `multiprocessing.Event`   | Permite notificar entre procesos que deben detenerse. |
| `multiprocessing.Pool`    | Crea un clúster de procesos para procesar imágenes en paralelo. |

#### Ventajas:
- Aprovecha varios núcleos de CPU.
- Evita el GIL (Global Interpreter Lock).
- Alta escalabilidad.

### Threading (implícito)

Aunque no se usan `threading.Thread` directamente, el diseño sigue el patrón de **división de tareas**:
- Cada `Process` actúa como un hilo pesado que ejecuta tareas específicas.
- El `Pool` divide el trabajo internamente con procesos (no hilos), pero la idea de concurrencia sigue vigente.

---

## Ajustes Importantes

### Volumen de Datos
- Puedes configurar cuántas imágenes se generan cambiando `min_images` y `max_images` en `satellite_simulator.py`

### Tiempo de procesamiento
- Simulado con `time.sleep()` en `process_image()` para representar tareas costosas (por ejemplo, clasificación, análisis de nubes, etc.)

---

## Futuras Mejoras
- Uso de una base de datos NoSQL (MongoDB) para almacenamiento en vez de archivos `.txt`.
- Balanceo de carga entre workers.
- Interfaz de monitoreo (API REST o Dashboard).

---

## Autor
Este proyecto fue generado como una simulación de un sistema distribuido usando procesamiento concurrente en Python. Cualquier mejora, sugerencia o issue es bienvenida en este repositorio.

