# Dataset preparado

Este directorio cumple el esquema que consume el CLI. Contiene 60 preguntas de entrenamiento, 20 preguntas de desarrollo y 22 artículos. El conjunto de evaluación final no se incluye.

Reproducir desde la raíz del repositorio:

```sh
uv sync --frozen
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json validate
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json train
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json calibrate --steps 21
uv run --frozen regulation-finder --data data/real/prepared --model artifacts/training/real-model.json evaluate --split development
```

La calibración eligió los umbrales guardados en `artifacts/training/selected-settings.json` usando únicamente `development.json`. Cambios a `metadata.json`, `articles.json` o `training.json` requieren reentrenar el modelo.
