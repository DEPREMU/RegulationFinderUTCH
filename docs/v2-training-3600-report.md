# RegulationFinderUTCH V2 — entrenamiento con banco de 3,600 preguntas

Fecha de ejecución: 18 de noviembre de 2026 (America/Mexico_City). Rama local:
`feature/v2-entrenamiento-3600`. No se hizo push, merge, reset ni modificación directa de
`main`.

Corrección y validación final: 21 de noviembre de 2026. El equipo confirmó expresamente la
autorización para publicar y redistribuir el reglamento, el banco de 3,600 preguntas, los datos
preparados, modelos y artefactos derivados en el repositorio del proyecto.

El campo `permission_status` de `data/real/v2-prepared/metadata.json` conserva el estado previo
a esa confirmación porque forma parte del fingerprint congelado del dataset. La autorización
posterior se registra en este informe, README y `artifacts/training/v2/test-results.json`.

## 1. Auditoría inicial

- Estado inicial: árbol limpio en `main`, sincronizado con `origin/main`.
- Commit inicial: `23b6c381b213a8626192fb0e806f3d71bd0957bb`.
- Los datasets, modelos y evaluaciones de Semana 3 estaban versionados y no fueron
  sobrescritos.
- La ruta definitiva y versionada del banco es
  `data/real/experiments/banco_3600/BIS_ReglamentoIA_3600_preguntas_2.csv`, SHA-256
  `261bf4303a391f504d655f70d5950989f5f3360037c56c3247e4124d8caa1d67`.
- La copia encontrada tiene exactamente 3,600 filas, las 11 columnas requeridas, 1,200
  `grupo_id`, tres variaciones por grupo, 20 artículos y 247 familias semánticas válidas
  artículo+intención.

El fingerprint histórico fallaba inicialmente en Windows por CRLF/LF, no por diferencias de
contenido. El cargador ahora canonicaliza saltos de línea. El dataset Semana 3 vuelve a
producir `80f42de0...` tanto en Windows como en Linux, y el modelo congelado coincide
exactamente con un reentrenamiento determinista (vocabulario, priors y likelihoods).

## 2. Auditoría y preparación del banco

Resultado de las 3,600 preguntas candidatas:

| Estado | Preguntas | Uso |
| --- | ---: | --- |
| Válidas | 3,582 | Candidatas para split agrupado |
| Pendientes de revisión | 18 | Excluidas de entrenamiento y desarrollo |
| Rechazadas objetivamente | 0 | Ninguna |

Las 18 pendientes corresponden al artículo 13, intención 3. Preguntan la duración explícita
del periodo “cuatrimestral”; el texto almacenado usa esa palabra, pero no declara literalmente
“cuatro meses”. Deben adjudicarse contra la fuente institucional antes de incorporarlas.

Se detectó que la histórica `Q9028` cubría la misma necesidad que la familia retenida A13/I2.
Para preservar el holdout se excluyó `Q9028` únicamente de V2 y se conservó intacta en Semana 3;
la familia del banco permanece en desarrollo. No hay duplicados normalizados dentro del banco.

El split no solo mantiene juntas las tres variaciones de cada `grupo_id`: también mantiene
juntos todos los grupos del mismo par artículo+`intencion_id`. Esto evita que reformulaciones
del mismo intento aparezcan simultáneamente en entrenamiento y desarrollo.

- Banco usado en entrenamiento: 2,874.
- Preguntas históricas recibidas: 120.
- Preguntas históricas incluidas en V2: 68.
- Preguntas históricas excluidas de V2 por solapamiento: 52 (47 confirmadas y 5 pendientes
  de adjudicación humana).
- Entrenamiento total V2: 2,942.
- Desarrollo agrupado: 708 preguntas, 49 familias artículo+intención.
- Regresión fuera de alcance: 30 preguntas locales; no es evaluación independiente.
- Fuga por `grupo_id`: ninguna.
- Fuga por artículo+intención: ninguna.

Los reportes auditables están en `artifacts/training/v2/valid_questions.csv`,
`pending_review.csv`, `rejected_questions.csv`, `article_topic_mapping.csv` y
`data_audit_summary.json`. Las exclusiones históricas y su familia equivalente están en
`excluded_historical_overlaps.csv`. Los archivos congelados de Semana 3 no se modificaron.

### Corrección de fuga semántica

La verificación posterior a la primera V2 encontró preguntas históricas equivalentes a
familias retenidas, entre ellas `Q9022` frente a artículo 10/intención 1. Se revisaron las 120
preguntas históricas contra las 49 familias de desarrollo. V2 excluye 52 preguntas históricas:
47 equivalencias confirmadas y 5 coincidencias conservadoras que permanecen pendientes de
revisión humana. Las 708 preguntas de desarrollo no se eliminaron ni movieron.

Después de las exclusiones quedan 68 preguntas históricas incluidas. No hay duplicados exactos
ni intersección artículo+intención del banco. La revisión léxica posterior no encontró
coincidencias incluidas con Jaccard morfológico de 0.50 o superior. Dos candidatos superiores a
0.40 fueron revisados como intenciones distintas (autoridad frente a disponibilidad y porcentaje
de asistencia frente a consecuencia por incumplimiento). Debido a las 5 exclusiones pendientes,
no se afirma una adjudicación semántica humana completa; se afirma únicamente que no quedan
fugas conocidas en el corpus incluido.

## 3. Artículos y temas conservados

No se agregaron artículos ni temas. El catálogo sigue teniendo 22 artículos y 20 temas:

| Artículo | Tema canónico |
| --- | --- |
| 1 | Alcance del reglamento |
| 2, 21 | Calificación mínima aprobatoria |
| 3 | Clasificación de estudiantes |
| 4, 5 | Examen de ingreso |
| 6 | Documentación de admisión |
| 7 | Estudios en el extranjero |
| 8 | Cambio de carrera de nuevo ingreso |
| 9 | Cambio de carrera y turno |
| 10 | Acreditación de asignaturas |
| 10 BIS | Certificación de inglés BIS |
| 13 | Periodos escolares |
| 16 | Inscripción simultánea |
| 18 | Reincorporación académica |
| 19 | Baja temporal y repetición |
| 20 | Evaluación académica |
| 30 | Requisitos para aprobar una asignatura |
| 33 | Derecho a evaluación ordinaria |
| 43 | Servicio social y estadía |
| 47 | Derecho a revisión de evaluaciones |
| 48 | Obligaciones de pago |

El banco no contiene preguntas para los artículos 2 y 5, pero sus temas y artículos se
conservan mediante las 68 preguntas históricas incluidas y el catálogo original. Las etiquetas `tema`
del CSV que usan otra redacción se mapearon por `articulo_esperado` al tema canónico; no se
inventaron equivalencias.

## 4. Cambios técnicos

- Adaptador y auditor reproducible para el CSV de 3,600 preguntas.
- Split determinista por artículo+intención y reportes de válidas/pendientes/rechazadas.
- Perfiles léxicos opcionales por artículo, derivados exclusivamente del split de
  entrenamiento.
- Rasgos morfológicos ligeros `word_stem` para variantes como
  `mínima/mínimo` y `aprobatoria/aprobatorio`; sin modelos preentrenados ni servicios.
- Ranking con cobertura ponderada por IDF sobre el texto original y el perfil de artículo.
- Configuración V1 preservada: el peso de perfil por defecto es cero.
- Evaluación ampliada con Top-1, Top-3, abstenciones, falsos retornos OOS y detalles por
  pregunta.
- Fingerprints portables entre CRLF y LF.
- Medición de memoria compatible con Windows mediante `GetProcessMemoryInfo`; Linux/Pi sigue
  usando `resource`.
- La API Flask conserva el contrato existente; las nuevas opciones son parámetros de
  inicialización del retriever/CLI.

## 5. Modelo y configuración V2

- Dataset: `data/real/v2-prepared/`.
- Modelo: `artifacts/training/v2/v2-model.json`.
- Configuración: `artifacts/training/v2/v2-settings.json`.
- Fingerprint: `305544dbd1d6e245737f411490a10161815223bb52ea6f032b8e7447b24d83ec`.
- SHA-256 del modelo:
  `ac9ed0964a570e5f011915362389d0e2d50dfc43b947dbb0f1b3481ffa3d2c7e`.
- Tamaño: 634,932 bytes.
- Vocabulario: 1,140 rasgos.
- Umbrales seleccionados: tema `0.55`, léxico `0.45`, perfil `1.0`.

La cuadrícula utilizó solo desarrollo agrupado y los 30 casos OOS locales. Exigió no superar
los 3 falsos retornos de V1 y después maximizó Top-3, Top-1, abstención OOS y estrictitud. La
evaluación final histórica no participó en la selección.

## 6. Comparación V1 contra V2

Comparación primaria sobre las mismas 708 preguntas agrupadas:

| Métrica | V1 | V2 | Cambio |
| --- | ---: | ---: | ---: |
| Top-1 | 319/708 (45.06 %) | 439/708 (62.01 %) | +16.95 pp |
| Top-3 | 330/708 (46.61 %) | 439/708 (62.01 %) | +15.40 pp |
| Abstenciones respondibles | 264 | 110 | -154 |
| OOS rechazadas | 27/30 (90.00 %) | 27/30 (90.00 %) | igual |
| OOS con retorno incorrecto | 3 | 3 | igual |

En los 20 casos de desarrollo heredados, V1 y V2 obtienen 14/20 Top-3; V2 reduce las
abstenciones de 3 a 2. Esos casos no eligieron la configuración.

Como regresión histórica solamente, V2 obtiene 55/60 (91.67 %) frente a 32/60 de V1. No es
una nueva evaluación independiente, no se utilizó para ajuste y puede existir solapamiento
semántico con el banco generado. No hay solapamiento textual normalizado exacto.

En Windows, sobre 1,000 búsquedas calientes y las mismas 708 consultas:

| Medición | V1 | V2 |
| --- | ---: | ---: |
| Mediana | 0.088 ms | 0.118 ms |
| p95 | 0.114 ms | 0.150 ms |
| Modelo | 275,296 bytes | 634,932 bytes |

El RSS de Windows es un máximo de vida del proceso compartido y debe repetirse en procesos
separados en Raspberry Pi.

## 7. Errores pendientes

De 708 preguntas de desarrollo V2:

- 439 correctas.
- 159 respondidas con artículo incorrecto; todas son errores de clasificación de tema.
- 110 abstenciones: 91 por confianza de tema y 19 por la compuerta léxica.
- No hubo casos donde Top-1 fallara y Top-3 corrigiera; tampoco errores atribuibles al orden
  entre artículos del mismo tema en este holdout.

Las confusiones principales son 10↔30 (acreditación/aprobación de asignaturas), 7→6
(estudios extranjeros/documentación), 8→9 (cambio de carrera), 13→10 y 3→16. Persisten tres
falsos retornos OOS: cajeros automáticos→21, paquetería→43 y red social/fotografías→6.
Los detalles están en `error-analysis.json` y en los CSV individuales.

## 8. Pruebas ejecutadas

- `pytest`: 30 pruebas aprobadas.
- `ruff check .`: aprobado.
- `ruff format --check .`: aprobado.
- `npm --prefix frontend run lint`: aprobado.
- `npm --prefix frontend run build`: aprobado con Vite.
- Validación del dataset y carga de fingerprint/modelo: aprobadas.
- Búsqueda CLI respondible y consulta OOS: aprobadas.
- Compatibilidad Flask/API cubierta por Pytest.

`npm ci` informó tres vulnerabilidades moderadas en dependencias. No se ejecutó
`npm audit fix` porque puede cambiar el lockfile y requiere una revisión separada.

## 9. Reproducción en Windows

Desde PowerShell en la raíz del repositorio:

```powershell
$env:UV_PROJECT_ENVIRONMENT = ".venv-v2"
$env:UV_CACHE_DIR = ".uv-cache-v2"
uv sync --frozen
npm --prefix frontend ci
npm --prefix frontend run build

uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json validate
uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json --min-topic-probability 0.55 --min-lexical-score 0.45 --article-profile-weight 1.0 search "¿Cuál es la calificación mínima aprobatoria?"
uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json --min-topic-probability 0.55 --min-lexical-score 0.45 --article-profile-weight 1.0 web
```

Abrir `http://127.0.0.1:5000`.

Recrear datos, modelo y comparación desde las fuentes:

```powershell
uv run --frozen python scripts/prepare_v2_dataset.py --source data/real/experiments/banco_3600/BIS_ReglamentoIA_3600_preguntas_2.csv
uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json --feature-mode word_stem train
uv run --frozen python scripts/run_v2_experiment.py
uv run --frozen pytest -q
uv run --frozen ruff check .
uv run --frozen ruff format --check .
```

El preparador se niega a sobrescribir `data/real/v2-prepared` y
`artifacts/training/v2`; para una repetición debe usarse un directorio nuevo o retirar
explícitamente los artefactos V2 después de respaldarlos.

## 10. Instalación posterior en Raspberry Pi

Verificar antes:

1. Raspberry Pi OS de 64 bits, Python 3.10 o superior y disponibilidad de un wheel de NumPy
   para la arquitectura/Python elegidos.
2. Transferencia en modo binario o checkout de Git completo de `data/real/v2-prepared`,
   `artifacts/training/v2/v2-model.json`, código y frontend compilado.
3. SHA-256 del modelo igual a
   `ac9ed0964a570e5f011915362389d0e2d50dfc43b947dbb0f1b3481ffa3d2c7e`.
4. Validación del fingerprint portable `305544db...` y una búsqueda de humo.
5. Medición nueva de latencia, RSS y temperatura en el Pi; los valores de Windows no se
   trasladan al dispositivo.
6. Confirmar que los tres falsos OOS conocidos son aceptables para la demostración o ampliar
   primero la regresión OOS sin usar la evaluación final histórica.

Comandos en el Pi:

```sh
export UV_PROJECT_ENVIRONMENT=.venv-v2
export UV_CACHE_DIR=.uv-cache-v2
uv sync --frozen
sha256sum artifacts/training/v2/v2-model.json
uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json validate
uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json --min-topic-probability 0.55 --min-lexical-score 0.45 --article-profile-weight 1.0 search '¿Cuál es la calificación mínima aprobatoria?'
uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json --min-topic-probability 0.55 --min-lexical-score 0.45 --article-profile-weight 1.0 measure --iterations 1000 --hardware-label 'Raspberry Pi; completar modelo, RAM y OS'
uv run --frozen regulation-finder --data data/real/v2-prepared --model artifacts/training/v2/v2-model.json --min-topic-probability 0.55 --min-lexical-score 0.45 --article-profile-weight 1.0 web --host 0.0.0.0 --port 5000
```

Si `frontend/dist` no se transfiere ya compilado, instalar Node.js y ejecutar
`npm --prefix frontend ci && npm --prefix frontend run build` en el Pi.

## 11. Problemas y decisiones pendientes

- Revisar humanamente las 18 preguntas del artículo 13.
- Adjudicar las 5 exclusiones históricas conservadoras marcadas `review_pending`.
- Conservar el registro institucional de la autorización de publicación y redistribución.
- Crear una evaluación independiente nueva para V2; 708 preguntas agrupadas son desarrollo y
  las 60 históricas ya no son independientes.
- Ampliar el conjunto OOS con autoría y adjudicación externas.
- Medir memoria/latencia en Raspberry Pi real.
- Revisar las tres vulnerabilidades moderadas reportadas por npm.
