#!/usr/bin/env python3
"""
validate_dataset.py
Automated validation script for RegulationFinderUTCH training/development dataset.
Checks:
  - Missing or duplicate IDs / article numbers
  - Empty or null text fields
  - Invalid topic labels & article reference syntax
  - Split distribution (train / dev)
"""

import json
import re
import sys
import os

VALID_TOPICS = {
    "Definiciones operativas y académicas",
    "Circunstancias para presentar el examen de ingreso",
    "Requisito de examen de ingreso",
    "Requisitos de documentación para admisión",
    "Revalidación de estudios en el extranjero",
    "Cambio de carrera para nuevo ingreso",
    "Cambio de carrera y turno",
    "Criterios generales de acreditación",
    "Requisito de inglés para modelo BIS",
    "Períodos escolares cuatrimestrales",
    "Restricción de inscripción simultánea",
    "Reincorporación académica",
    "Baja temporal y límite de cursado",
    "Definición de evaluación académica",
    "Calificación mínima aprobatoria",
    "Requisito de aprobación de asignatura",
    "Requisitos para evaluación ordinaria (asistencia)",
    "Servicio social y estadía profesional",
    "Derechos de los estudiantes",
    "Obligaciones de los estudiantes"
}

ARTICLE_PATTERN = re.compile(r"^Artículo\s+\d+(\s+BIS)?$")

def validate_dataset(filepath):
    print(f"=== INICIANDO VALIDACIÓN DE DATASET: {os.path.basename(filepath)} ===")
    
    if not os.path.exists(filepath):
        print(f"ERROR: No se encontró el archivo {filepath}")
        return False

    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)

    errors = []
    warnings = []
    
    seen_ids = set()
    seen_articles = set()
    split_counts = {"train": 0, "dev": 0}

    for idx, item in enumerate(data, start=1):
        prefix = f"[Registro #{idx}]"

        # 1. Check required fields exist and are non-empty
        required_fields = ["id", "article_number", "topic", "user_query", "original_text", "source_version", "split"]
        for field in required_fields:
            if field not in item:
                errors.append(f"{prefix} Campo requerido faltante: '{field}'")
            elif not str(item[field]).strip():
                errors.append(f"{prefix} Campo vacío detectado en '{field}'")

        # 2. Check duplicate / invalid IDs
        rec_id = item.get("id", "")
        if rec_id:
            if rec_id in seen_ids:
                errors.append(f"{prefix} ID duplicado detectado: '{rec_id}'")
            seen_ids.add(rec_id)

        # 3. Check duplicate / invalid article numbers
        art_num = item.get("article_number", "")
        if art_num:
            if art_num in seen_articles:
                errors.append(f"{prefix} Número de artículo duplicado: '{art_num}'")
            seen_articles.add(art_num)
            
            if not ARTICLE_PATTERN.match(art_num):
                errors.append(f"{prefix} Sintaxis de artículo inválida: '{art_num}'")

        # 4. Check topic validity
        topic = item.get("topic", "")
        if topic and topic not in VALID_TOPICS:
            errors.append(f"{prefix} Etiqueta de tema no reconocida: '{topic}'")

        # 5. Check text length / quality
        text = item.get("original_text", "")
        if text and len(text.strip()) < 20:
            warnings.append(f"{prefix} El texto del artículo es inusualmente corto ({len(text)} caracteres)")

        # 6. Check split validity
        split = item.get("split", "")
        if split in split_counts:
            split_counts[split] += 1
        else:
            errors.append(f"{prefix} Valor de split inválido: '{split}'. Debe ser 'train' o 'dev'.")

    # Summary Report
    print(f"\n--- RESUMEN DE COMPROBACIONES ---")
    print(f"Total de registros evaluados: {len(data)}")
    print(f"Distribución de splits: Train={split_counts['train']} (80%), Dev={split_counts['dev']} (20%)")
    print(f"IDs únicos comprobados: {len(seen_ids)}")
    print(f"Artículos únicos comprobados: {len(seen_articles)}")
    
    if warnings:
        print(f"\n⚠️  ADVERTENCIAS ({len(warnings)}):")
        for w in warnings:
            print(f"  - {w}")

    if errors:
        print(f"\n❌ ERRORES DETECTADOS ({len(errors)}):")
        for e in errors:
            print(f"  - {e}")
        print("\nresultado: VALIDACIÓN FALLIDA ❌")
        return False

    print("\n✅ resultado: TODAS LAS PRUEBAS DE VALIDACIÓN PASARON EXITOSAMENTE (0 errores).")
    return True

if __name__ == "__main__":
    dataset_file = sys.argv[1] if len(sys.argv) > 1 else "/workspace/scratch/dataset_v1.0_train_dev.json"
    success = validate_dataset(dataset_file)
    sys.exit(0 if success else 1)
