# Datos de Week 2

El propietario del proyecto pidió rastrear estos archivos para poder reproducir el entrenamiento desde otro dispositivo. La autorización para redistribución pública del reglamento todavía no está confirmada.

- `train/questions.csv`: 60 preguntas asignadas a `train`.
- `dev/dataset_v1.0_all_dev.json`: 20 pares originales, todos asignados a `dev`.
- `prepared/`: dataset normalizado que consume el CLI.
- `review/`: borrador anterior y notas de revisión; no forma parte del dataset de entrenamiento.
- `artifacts/training/`: modelo, manifiesto, cuadrícula de calibración, configuración elegida y evaluación de desarrollo.

Para incorporar los artículos faltantes al catálogo entrenado, se consolidaron estas etiquetas: Artículo 2 → `Calificación mínima aprobatoria`; Artículo 5 → `Examen de ingreso`. La decisión está reflejada en `prepared/articles.json`.

El archivo de evaluación final permanece aislado: no se incluyó ni se abrió.
