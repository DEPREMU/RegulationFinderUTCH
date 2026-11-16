# RegulationFinderUTCH — pruebas de Raspberry Pi (Semana 3)

**Objetivo.** Verificar la versión congelada de Semana 3 y producir evidencia auténtica del funcionamiento en Raspberry Pi. Este paquete **NO reentrena**, **NO calibra** y **NO vuelve a ejecutar las 60 preguntas finales**.

## 1. Preparar los archivos

1. En la Raspberry Pi, entra a la carpeta raíz del repositorio `RegulationFinderUTCH`.
2. Copia esta carpeta `pruebas_pi_w3/` completa dentro de la raíz del repositorio. Debe existir `RegulationFinderUTCH/pruebas_pi_w3/ejecutar_pruebas_pi.sh`.
3. Verifica que existan `data/real/week3-prepared/` y `artifacts/training/week3-real-model.json`.
4. Comprueba que `uv` funcione mediante `uv --version`; la instalación inicial de dependencias puede requerir internet. Usa un sistema Raspberry Pi OS/Linux de 64 bits cuando sea compatible y Python 3.10+.
5. **No ejecutes `train`, `calibrate` ni cambies umbrales.** La configuración congelada es tema `0.35`, coincidencia léxica `0.25`.

## 2. Ejecutar todo lo automatizable

Desde la raíz del repositorio:

```bash
bash pruebas_pi_w3/ejecutar_pruebas_pi.sh
```

Esto ejecuta, en orden:

| Prueba | Qué comprueba | Evidencia |
|---|---|---|
| Instalación | `uv sync --frozen` y dependencias | `01_instalacion.log` |
| Lint/formato | `ruff check` y `ruff format --check` | `02_ruff.log`, `03_formato.log` |
| Tests | `pytest` | `04_pytest.log` |
| Dataset | Validación del dataset Week 3 | `05_validacion.log` |
| Consulta | Búsqueda real con el modelo congelado | `06_busqueda.log` |
| Funcional | 20 preguntas de desarrollo + entradas vacías, signos, fuera de alcance y repetibilidad | `funcionales/detalle_funcional.csv`, `funcionales/resumen_funcional.json` |
| Rendimiento | 3 procesos diferentes, 100 búsquedas por proceso con calentamiento | `medicion_1.json`, `medicion_2.json`, `medicion_3.json` |
| Hardware | Modelo, OS, versión de código, hashes, memoria y CPU | `hardware_y_versiones.txt` |

Los resultados se guardan en una carpeta nueva `pi_resultados/FECHA_UTC/`. Si falla un paso, detén la secuencia, conserva el log y corrige la causa antes de continuar. La ejecución completa no promete ni presupone que todo aprobará.

**Medición:** `measure` registra la mediana y el percentil 95 en ms, y el pico RSS del proceso en bytes. Mide `Retriever.search()` después del calentamiento, sin incluir arranque, web ni pantalla. El script funcional también registra tiempo por pregunta y VmRSS actual, que **no es el pico**. Registrar condiciones de energía, ventilación y carga del equipo.

## 3. Pruebas de interfaz (manuales, con evidencia)

Levanta la aplicación con el modelo congelado:

```bash
uv run --frozen regulation-finder --data data/real/week3-prepared --model artifacts/training/week3-real-model.json --min-topic-probability 0.35 --min-lexical-score 0.25 web
```

En el navegador local, abre `http://127.0.0.1:5000/`. Confirma y registra:

- [ ] **Inicio limpio:** cierra y vuelve a abrir el programa desde una sesión nueva, sin errores.
- [ ] **Consulta válida:** escribe `¿Cuál es la calificación mínima para aprobar?`. Guarda lo que devuelva (no supongas una respuesta correcta).
- [ ] **Cantidad:** nunca se muestran más de tres artículos.
- [ ] **Fuente y contenido:** los resultados muestran número de artículo y texto original sin cambios.
- [ ] **Aviso:** aparece un aviso de herramienta informativa, no oficial.
- [ ] **Entrada vacía:** enviar vacío o espacios no genera error del servidor; observar mensaje.
- [ ] **Sin respuesta / baja confianza:** preguntar `¿Qué platillo sirve mañana la cafetería?`; registrar si el buscador se abstiene o devuelve algo (una respuesta fuera de alcance es un fallo a documentar, no algo que se oculta).
- [ ] **Repetición:** enviar la misma pregunta dos veces; comparar orden y artículos.
- [ ] **Estabilidad:** varias consultas seguidas no bloquean la interfaz; si existe estado de error, registrarlo.

Detener el servidor con `Ctrl+C`. Guardar capturas si el profesor las requiere; no publicar datos privados ni la versión del reglamento sin permiso.

## 4. ¿Y las 60 preguntas de evaluación final?

**No las vuelvas a pasar por el programa para crear otro supuesto resultado independiente.** El repositorio ya documenta un experimento final sobre 60 preguntas (32/60). Si el modelo no cambia, ese resultado puede citarse como **evaluación ya realizada**, con sus limitaciones y procedencia pendiente. Un nuevo resultado principal requiere un conjunto nuevo y genuinamente independiente, autoría/procedencia comprobable y sistema congelado.

Para la Pi, usa este paquete para funcionalidad, reproducibilidad y hardware. Las 20 preguntas de desarrollo son apropiadas para pruebas de funcionamiento, **no para un nuevo porcentaje final**.

## 5. Qué llevar al reporte

- Modelo y RAM de la Raspberry Pi, OS, Python, `git rev-parse HEAD`, SHA-256 del modelo.
- Registro de instalación, pytest, funcionales e interfaz.
- Tres JSON de rendimiento con mediana, p95 y pico RSS; condiciones de cada corrida.
- Cuadro de fallos, con consultas y artículos esperados/obtenidos; **no ajustes el modelo con el banco final**.
- Separar mediciones reales en Pi de resultados previos en Windows.

**Fuentes del proyecto:**

- https://github.com/DEPREMU/RegulationFinderUTCH/blob/main/docs/raspberry-pi.md
- https://github.com/DEPREMU/RegulationFinderUTCH/blob/main/docs/week-3-model-release.md
- https://github.com/DEPREMU/RegulationFinderUTCH/blob/main/docs/evaluation.md
