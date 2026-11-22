"""Audit the 3,600-question bank and build a leakage-resistant V2 dataset."""

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

from regulation_finder.preprocessing import content_tokens, tokens

REQUIRED_COLUMNS = {
    "id",
    "pregunta",
    "articulo_esperado",
    "tipo",
    "pagina_pdf",
    "fuente",
    "grupo_id",
    "variacion",
    "tema",
    "intencion_id",
    "observaciones",
}
SEED = "utch-v2-grouped-intent-split-2026-11-18"
EXPECTED_SOURCE = "data/real/experiments/banco_3600/BIS_ReglamentoIA_3600_preguntas_2.csv"

# Manual review against the 49 held-out article+intention families. These rows remain
# untouched in Week 3; they are excluded only from the assembled V2 training corpus.
CONFIRMED_HISTORICAL_OVERLAPS = {
    "Q9001": "A1/I8",
    "Q9002": "A1/I8",
    "Q9003": "A1/I8",
    "Q9008": "A4/I1",
    "Q9010": "A6/I2",
    "Q9011": "A6/I2",
    "Q9012": "A6/I2",
    "Q9022": "A10/I1+I6",
    "Q9023": "A10/I1+I6",
    "Q9024": "A10/I1+I6",
    "Q9025": "A10 BIS/I1",
    "Q9026": "A10 BIS/I1",
    "Q9027": "A10 BIS/I1",
    "Q9028": "A13/I2",
    "Q9029": "A13/I2",
    "Q9030": "A13/I2",
    "Q9033": "A16/I8+I10",
    "Q9034": "A18/I9",
    "Q9035": "A18/I9",
    "Q9036": "A18/I9",
    "Q9043": "A21/I1",
    "Q9044": "A21/I6",
    "Q9045": "A21/I1",
    "Q9046": "A30/I8",
    "Q9047": "A30/I8",
    "Q9048": "A30/I8",
    "Q9054": "A43/I9",
    "Q9067": "A4/I8",
    "Q9070": "A6/I4",
    "Q9073": "A7/I9",
    "Q9077": "A8/I3",
    "Q9078": "A8/I6",
    "Q9088": "A13/I6",
    "Q9089": "A13/I6",
    "Q9090": "A13/I2",
    "Q9091": "A16/I8+I10",
    "Q9092": "A16/I8+I10",
    "Q9096": "A18/I9",
    "Q9097": "A19/I8",
    "Q9101": "A20/I6",
    "Q9102": "A20/I7",
    "Q9105": "A21/I6",
    "Q9106": "A30/I5",
    "Q9109": "A33/I2",
    "Q9112": "A43/I9",
    "Q9116": "A47/I8",
    "Q9119": "A48/I16",
}

REVIEW_HISTORICAL_OVERLAPS = {
    "Q9007": "A4/I1",
    "Q9009": "A4/I1",
    "Q9013": "A7/I5",
    "Q9093": "A16/I8+I10",
    "Q9107": "A30/I8",
}

OUT_OF_SCOPE_QUESTIONS = [
    "¿Cuál será el clima mañana en Chihuahua?",
    "¿Qué menú sirve hoy la cafetería del campus?",
    "¿Cuál es la contraseña de la red wifi para visitantes?",
    "¿A qué hora pasa la ruta de transporte escolar?",
    "¿Cuánto cuesta el estacionamiento para visitantes?",
    "¿Dónde puedo imprimir un mapa de los edificios del campus?",
    "¿Cuál es el número telefónico personal del rector?",
    "¿Cuándo juega el equipo de fútbol de la universidad?",
    "¿Qué libros nuevos llegaron esta semana a la biblioteca?",
    "¿La cafetería ofrece opciones vegetarianas?",
    "¿Dónde se tramita una vacuna contra la influenza?",
    "¿Qué modelo de computadora venden en la tienda universitaria?",
    "¿Cuánto cuesta rentar el auditorio para una fiesta?",
    "¿Qué películas proyectarán este viernes en el campus?",
    "¿Dónde puedo reportar un automóvil mal estacionado?",
    "¿Cuál es el horario de la alberca universitaria?",
    "¿Qué proveedor surte los uniformes deportivos?",
    "¿Hay cajeros automáticos dentro de la universidad?",
    "¿Qué estación de radio se escucha mejor en Chihuahua?",
    "¿Cuánto cuesta un desayuno cerca de la UTCH?",
    "¿Puedo reservar una cancha para el fin de semana?",
    "¿Qué autobús público llega al campus?",
    "¿Dónde se compran boletos para el concierto universitario?",
    "¿Cuál es la marca del mobiliario de los salones?",
    "¿Hay servicio de paquetería dentro de la universidad?",
    "¿Qué red social publica las fotografías de los eventos?",
    "¿Cuál es el horario de atención de la papelería?",
    "¿Dónde puedo cargar un vehículo eléctrico?",
    "¿Qué hoteles están cerca de la universidad?",
    "¿Se permiten mascotas en las áreas verdes del campus?",
]


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized_question(value: str) -> str:
    return " ".join(tokens(value))


def _write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def _write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def _review_reason(row: dict) -> str | None:
    if row["articulo_esperado"] == "13" and row["intencion_id"] == "3":
        return (
            "La pregunta solicita la duración explícita del periodo; el artículo 13 usa "
            "'cuatrimestral' pero no declara textualmente 'cuatro meses'. Requiere adjudicación."
        )
    return None


def _split_intentions(rows: list[dict]) -> set[tuple[str, str]]:
    by_article = defaultdict(set)
    for row in rows:
        by_article[row["articulo_esperado"]].add(row["intencion_id"])
    development = set()
    for article_id, intentions in by_article.items():
        ordered = sorted(
            intentions,
            key=lambda intention: hashlib.sha256(
                f"{SEED}|{article_id}|{intention}".encode()
            ).hexdigest(),
        )
        development_count = max(2, round(len(ordered) * 0.2))
        development.update((article_id, intention) for intention in ordered[:development_count])
    return development


def prepare(source: Path, base_dir: Path, output_dir: Path, report_dir: Path) -> dict:
    if output_dir.exists() or report_dir.exists():
        raise ValueError("Refusing to overwrite an existing V2 output or report directory")
    if not source.is_file():
        raise ValueError(f"Question bank does not exist: {source}")

    with source.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        columns = set(reader.fieldnames or [])
    if columns != REQUIRED_COLUMNS:
        raise ValueError("Question bank columns do not match the required schema")
    if len(rows) != 3600:
        raise ValueError(f"Expected 3,600 rows, found {len(rows)}")

    articles = json.loads((base_dir / "articles.json").read_text(encoding="utf-8"))
    legacy_training_source = json.loads((base_dir / "training.json").read_text(encoding="utf-8"))
    legacy_development = json.loads((base_dir / "development.json").read_text(encoding="utf-8"))
    articles_by_id = {row["article_id"]: row for row in articles}
    catalog_topics = {row["topic"] for row in articles}

    overlap_ids = set(CONFIRMED_HISTORICAL_OVERLAPS) | set(REVIEW_HISTORICAL_OVERLAPS)
    legacy_ids = {row["example_id"] for row in legacy_training_source}
    if overlap_ids - legacy_ids:
        raise ValueError("Historical overlap policy references unknown Week 3 identifiers")
    historical_overlap_rows = []
    legacy_training = []
    for row in legacy_training_source:
        identifier = row["example_id"]
        if identifier in overlap_ids:
            confirmed = identifier in CONFIRMED_HISTORICAL_OVERLAPS
            family = (
                CONFIRMED_HISTORICAL_OVERLAPS.get(identifier)
                or REVIEW_HISTORICAL_OVERLAPS[identifier]
            )
            historical_overlap_rows.append(
                {
                    **row,
                    "matched_development_family": family,
                    "review_status": "confirmed" if confirmed else "review_pending",
                    "reason": (
                        "Manual semantic review found the same information need in the held-out "
                        "family. Excluded from V2 only; Week 3 remains unchanged."
                        if confirmed
                        else "Conservative V2 exclusion: likely equivalent to the held-out family; "
                        "human adjudication remains pending. Week 3 remains unchanged."
                    ),
                }
            )
        else:
            legacy_training.append(row)

    identifiers = Counter(row["id"] for row in rows)
    normalized_questions = Counter(_normalized_question(row["pregunta"]) for row in rows)
    groups = defaultdict(list)
    for row in rows:
        groups[row["grupo_id"]].append(row)

    valid, pending, rejected = [], [], []
    for row in rows:
        reasons = []
        blank = sorted(column for column in REQUIRED_COLUMNS if not row[column].strip())
        if blank:
            reasons.append("blank fields: " + ", ".join(blank))
        if identifiers[row["id"]] != 1:
            reasons.append("duplicate id")
        if normalized_questions[_normalized_question(row["pregunta"])] != 1:
            reasons.append("duplicate normalized question")
        if row["articulo_esperado"] not in articles_by_id:
            reasons.append("unknown expected article")
        if row["tipo"] != "respondible":
            reasons.append("unsupported question type")
        group = groups[row["grupo_id"]]
        if len(group) != 3 or {item["variacion"] for item in group} != {"1", "2", "3"}:
            reasons.append("group must contain variations 1, 2 and 3")
        if len({item["articulo_esperado"] for item in group}) != 1:
            reasons.append("group mixes expected articles")
        if len({item["intencion_id"] for item in group}) != 1:
            reasons.append("group mixes intentions")

        enriched = {
            **row,
            "canonical_topic": articles_by_id.get(row["articulo_esperado"], {}).get("topic", ""),
        }
        if reasons:
            rejected.append({**enriched, "status": "rejected", "reason": "; ".join(reasons)})
        elif reason := _review_reason(row):
            pending.append({**enriched, "status": "pending_review", "reason": reason})
        else:
            valid.append({**enriched, "status": "valid", "reason": ""})

    rejected_groups = {row["grupo_id"] for row in rejected}
    pending_groups = {row["grupo_id"] for row in pending}
    if rejected_groups & {row["grupo_id"] for row in valid}:
        raise ValueError("A rejected group was only partially rejected")
    if pending_groups & {row["grupo_id"] for row in valid}:
        raise ValueError("A pending group was only partially held out")

    development_intentions = _split_intentions(valid)
    bank_training = []
    bank_development = []
    legacy_question_norms = {
        _normalized_question(row["question"]): row["example_id"] for row in legacy_training
    }
    legacy_duplicates = []
    for row in valid:
        split = (
            "development"
            if (row["articulo_esperado"], row["intencion_id"]) in development_intentions
            else "training"
        )
        row["split"] = split
        if split == "training":
            normalized = _normalized_question(row["pregunta"])
            if normalized in legacy_question_norms:
                row["split"] = "excluded_legacy_duplicate"
                row["reason"] = (
                    "Exact question already preserved from Week 3 as "
                    f"{legacy_question_norms[normalized]}"
                )
                legacy_duplicates.append(row)
                continue
            bank_training.append(
                {
                    "example_id": f"V2-{row['id']}",
                    "question": row["pregunta"],
                    "topic": row["canonical_topic"],
                    "provenance": (
                        f"3,600-question bank; article {row['articulo_esperado']}; "
                        f"group {row['grupo_id']}; variation {row['variacion']}"
                    ),
                }
            )
        else:
            bank_development.append(
                {
                    "question_id": f"V2-{row['id']}",
                    "question": row["pregunta"],
                    "accepted_article_ids": [row["articulo_esperado"]],
                    "provenance": (
                        f"Grouped-intention V2 development holdout; group {row['grupo_id']}"
                    ),
                }
            )

    training_questions = {_normalized_question(row["question"]) for row in legacy_training}
    bank_training_questions = {_normalized_question(row["question"]) for row in bank_training}
    development_questions = {_normalized_question(row["question"]) for row in bank_development}
    if training_questions & development_questions:
        raise ValueError("Legacy training leaks exact questions into V2 development")
    if bank_training_questions & development_questions:
        raise ValueError("V2 bank training leaks exact questions into development")

    training = [*legacy_training, *bank_training]
    if {row["topic"] for row in training} != catalog_topics:
        raise ValueError("Prepared V2 training does not cover exactly the catalog topics")

    profile_tokens = defaultdict(set)
    training_ids = {row["example_id"] for row in bank_training}
    for source_row in valid:
        if f"V2-{source_row['id']}" in training_ids:
            profile_tokens[source_row["articulo_esperado"]].update(
                content_tokens(source_row["pregunta"])
            )
    profiles = {
        article_id: sorted(values)
        for article_id, values in sorted(profile_tokens.items())
        if values
    }

    out_of_scope = [
        {
            "question_id": f"V2-OOS-{index:03d}",
            "question": question,
            "accepted_article_ids": [],
            "provenance": (
                "V2 development regression; locally authored; not independent final evaluation"
            ),
        }
        for index, question in enumerate(OUT_OF_SCOPE_QUESTIONS, start=1)
    ]
    metadata = {
        "dataset_id": "utch-v2-bank3600-grouped-intent-v1.1",
        "synthetic": False,
        # This historical audit field is part of the frozen dataset fingerprint.
        # Publication authorization was confirmed later and is recorded in release docs.
        "permission_status": (
            "User-authorized local experiment; external redistribution status remains unverified"
        ),
        "evaluation_origin": (
            "Development holds out complete article+intention families from the 3,600 bank. "
            "Known historical-training semantic overlaps were excluded from V2 only. "
            "Historical final evaluation is excluded and was not used for tuning."
        ),
        "source_sha256": _sha256(source),
        "split_seed": SEED,
    }

    output_dir.mkdir(parents=True)
    report_dir.mkdir(parents=True)
    payloads = {
        "articles.json": articles,
        "training.json": training,
        "development.json": bank_development,
        "evaluation.json": [],
        "out_of_scope.json": out_of_scope,
        "metadata.json": metadata,
        "retrieval_profiles.json": profiles,
        "week3-development-regression.json": legacy_development,
    }
    for name, payload in payloads.items():
        _write_json(output_dir / name, payload)

    mapping_rows = []
    bank_article_ids = {row["articulo_esperado"] for row in rows}
    for article in articles:
        source_topics = sorted(
            {row["tema"] for row in rows if row["articulo_esperado"] == article["article_id"]}
        )
        mapping_rows.append(
            {
                "article_id": article["article_id"],
                "canonical_topic": article["topic"],
                "bank_topics": " | ".join(source_topics),
                "bank_question_count": sum(
                    row["articulo_esperado"] == article["article_id"] for row in rows
                ),
                "coverage": "covered"
                if article["article_id"] in bank_article_ids
                else "legacy_only",
                "mapping_method": "article_esperado -> existing article catalog",
            }
        )

    audit_fields = [*sorted(REQUIRED_COLUMNS), "canonical_topic", "status", "reason", "split"]
    _write_csv(report_dir / "valid_questions.csv", valid, audit_fields)
    _write_csv(report_dir / "pending_review.csv", pending, audit_fields)
    _write_csv(report_dir / "rejected_questions.csv", rejected, audit_fields)
    _write_csv(
        report_dir / "excluded_historical_overlaps.csv",
        historical_overlap_rows,
        [
            "example_id",
            "question",
            "topic",
            "provenance",
            "matched_development_family",
            "review_status",
            "reason",
        ],
    )
    _write_csv(
        report_dir / "article_topic_mapping.csv",
        mapping_rows,
        list(mapping_rows[0]),
    )

    semantic_families = {(row["articulo_esperado"], row["intencion_id"]) for row in valid}
    training_families = {
        (row["articulo_esperado"], row["intencion_id"])
        for row in valid
        if row["split"] == "training"
    }
    development_families = semantic_families - training_families
    summary = {
        "source_requested_path": EXPECTED_SOURCE,
        "source_requested_path_exists": Path(EXPECTED_SOURCE).is_file(),
        "source_used": str(source),
        "source_sha256": _sha256(source),
        "rows_received": len(rows),
        "valid_questions": len(valid),
        "pending_review_questions": len(pending),
        "rejected_questions": len(rejected),
        "groups_received": len(groups),
        "valid_semantic_families": len(semantic_families),
        "training_semantic_families": len(training_families),
        "development_semantic_families": len(development_families),
        "group_id_leakage": False,
        "article_intention_leakage": bool(training_families & development_families),
        "bank_training_questions": len(bank_training),
        "bank_questions_excluded_as_legacy_duplicates": len(legacy_duplicates),
        "historical_training_questions_received": len(legacy_training_source),
        "legacy_training_questions_preserved": len(legacy_training),
        "historical_semantic_overlap_exclusions": len(historical_overlap_rows),
        "historical_overlap_exclusions_confirmed": len(CONFIRMED_HISTORICAL_OVERLAPS),
        "historical_overlap_exclusions_pending_review": len(REVIEW_HISTORICAL_OVERLAPS),
        "total_training_questions": len(training),
        "development_questions": len(bank_development),
        "development_out_of_scope_questions": len(out_of_scope),
        "catalog_articles": len(articles),
        "catalog_topics": len(catalog_topics),
        "bank_articles": len(bank_article_ids),
        "catalog_articles_without_bank_questions": sorted(set(articles_by_id) - bank_article_ids),
        "unknown_bank_articles": sorted(bank_article_ids - set(articles_by_id)),
        "normalized_duplicate_questions": sum(
            count - 1 for count in normalized_questions.values() if count > 1
        ),
        "profiled_articles": len(profiles),
        "split_seed": SEED,
        "review_policy": (
            "Objective structural failures are rejected. Questions whose answer is not explicit "
            "in the stored article are held for human review. Canonical labels come from the "
            "existing article catalog, never directly from the bank's tema column. Historical "
            "questions equivalent to held-out intentions are excluded from V2 only; conservative "
            "review-pending matches are also excluded and prevent a claim of complete semantic "
            "adjudication."
        ),
    }
    _write_json(report_dir / "data_audit_summary.json", summary)
    _write_json(
        output_dir / "source_manifest.json",
        {
            **summary,
            "base_articles_sha256": _sha256(base_dir / "articles.json"),
            "base_training_sha256": _sha256(base_dir / "training.json"),
            "base_development_sha256": _sha256(base_dir / "development.json"),
        },
    )
    return summary


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--base-data", type=Path, default=Path("data/real/week3-prepared"))
    parser.add_argument("--output", type=Path, default=Path("data/real/v2-prepared"))
    parser.add_argument("--reports", type=Path, default=Path("artifacts/training/v2"))
    args = parser.parse_args(argv)
    try:
        print(
            json.dumps(
                prepare(args.source, args.base_data, args.output, args.reports),
                ensure_ascii=False,
                indent=2,
            )
        )
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(2, f"Error: {error}\n")


if __name__ == "__main__":
    main()
