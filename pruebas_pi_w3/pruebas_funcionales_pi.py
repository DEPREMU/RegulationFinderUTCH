#!/usr/bin/env python3
"""Week 3 Raspberry Pi smoke/development checks; never runs sealed final evaluation."""

import argparse
import csv
import hashlib
import json
import platform
import sys
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter_ns

from regulation_finder.classifier import TopicClassifier
from regulation_finder.config import Settings
from regulation_finder.retrieval import Retriever
from regulation_finder.schemas import load_dataset


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def rss_current_mb():
    """Current Linux VmRSS; not process peak memory and not model-only memory."""
    try:
        for line in Path('/proc/self/status').read_text().splitlines():
            if line.startswith('VmRSS:'):
                return round(int(line.split()[1]) / 1024, 4)
    except OSError:
        pass
    return None


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--data', type=Path, required=True)
    p.add_argument('--model', type=Path, required=True)
    p.add_argument('--topic-threshold', type=float, default=0.35)
    p.add_argument('--lexical-threshold', type=float, default=0.25)
    p.add_argument('--output', type=Path, required=True, help='Folder for the smoke-test results')
    args = p.parse_args()
    if args.output.exists() and any(args.output.iterdir()):
        p.error('Output folder must be new or empty; existing evidence will not be overwritten.')
    try:
        dataset = load_dataset(args.data, include_development=True, include_evaluation=False)
        model = TopicClassifier.load(args.model, dataset.fingerprint)
        retriever = Retriever(dataset, model, Settings(args.topic_threshold, args.lexical_threshold))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        p.exit(2, f'Model/dataset could not be loaded (no retraining attempted): {exc}\n')

    ids = {a.article_id: a for a in dataset.articles}
    if not dataset.development:
        p.exit(2, 'No development questions available for smoke tests.\n')
    cases = [
        ('desarrollo', e.question_id, e.question, list(e.accepted_article_ids))
        for e in dataset.development
    ]
    cases += [
        ('entrada_vacia', 'SMOKE-EMPTY', '', []),
        ('solo_espacios', 'SMOKE-SPACES', '   ', []),
        ('solo_signos', 'SMOKE-PUNCT', '???', []),
        ('fuera_de_alcance', 'SMOKE-CAFETERIA', '¿Qué platillo sirve mañana la cafetería?', []),
        ('fuera_de_alcance', 'SMOKE-CLIMA', '¿Qué temperatura hará mañana en la ciudad?', []),
        ('repetibilidad', 'SMOKE-REPEAT', dataset.development[0].question, list(dataset.development[0].accepted_article_ids)),
    ]
    records = []
    structural_failures = []
    known_results = {}
    for kind, test_id, question, accepted in cases:
        try:
            start = perf_counter_ns()
            result = retriever.search(question)
            elapsed_ms = round((perf_counter_ns() - start) / 1_000_000, 6)
            returned_ids = [a.article_id for a in result.articles]
            bad_ids = [x for x in returned_ids if x not in ids]
            changed_text = [a.article_id for a in result.articles if a.article_id in ids and a.text != ids[a.article_id].text]
            too_many = len(returned_ids) > 3
            duplicate = len(returned_ids) != len(set(returned_ids))
            if bad_ids or changed_text or too_many or duplicate:
                structural_failures.append(test_id)
            if kind in ('entrada_vacia', 'solo_espacios', 'solo_signos') and returned_ids:
                structural_failures.append(test_id + ': should abstain on empty/invalid input')
            if kind == 'desarrollo':
                known_results[test_id] = returned_ids
            if kind == 'repetibilidad' and returned_ids != known_results[dataset.development[0].question_id]:
                structural_failures.append(test_id + ': non-deterministic results')
            records.append({
                'tipo': kind, 'id': test_id, 'pregunta': question,
                'articulos_esperados': '|'.join(accepted),
                'articulos_obtenidos': '|'.join(returned_ids),
                'acierto_top3': int(any(x in accepted for x in returned_ids)) if accepted else '',
                'se_abstuvo': int(not returned_ids),
                'tema': result.topic or '',
                'probabilidad_tema': round(result.topic_probability, 9),
                'mensaje': result.message,
                'latencia_ms': elapsed_ms,
                'rss_actual_mb': rss_current_mb(),
                'error_tecnico': '',
            })
        except Exception as exc:
            structural_failures.append(test_id + ': exception')
            records.append({
                'tipo': kind, 'id': test_id, 'pregunta': question,
                'articulos_esperados': '|'.join(accepted), 'articulos_obtenidos': '',
                'acierto_top3': '', 'se_abstuvo': '', 'tema': '', 'probabilidad_tema': '',
                'mensaje': '', 'latencia_ms': '', 'rss_actual_mb': rss_current_mb(),
                'error_tecnico': f'{type(exc).__name__}: {exc}',
            })

    dev = [r for r in records if r['tipo'] == 'desarrollo']
    hits = sum(r['acierto_top3'] == 1 for r in dev)
    misses = len(dev) - hits
    summary = {
        'prueba': 'desarrollo + smoke (NO evaluación final independiente)',
        'fecha_utc': datetime.now(timezone.utc).isoformat(),
        'plataforma': platform.platform(),
        'python': sys.version.split()[0],
        'dataset_id': dataset.metadata.get('dataset_id'),
        'dataset_fingerprint': dataset.fingerprint,
        'modelo_sha256': sha256(args.model),
        'umbrales': {'tema': args.topic_threshold, 'lexico': args.lexical_threshold},
        'preguntas_desarrollo': len(dev),
        'aciertos_top3_desarrollo': hits,
        'top3_desarrollo_pct': round(100 * hits / len(dev), 4),
        'fallos_top3_desarrollo': misses,
        'abstenciones_desarrollo': sum(r['se_abstuvo'] == 1 for r in dev),
        'fallos_tecnicos': sum(bool(r['error_tecnico']) for r in records),
        'fallos_estructurales': structural_failures,
        'observaciones_fuera_de_alcance': [
            {'id': r['id'], 'se_abstuvo': bool(r['se_abstuvo']), 'articulos': r['articulos_obtenidos']}
            for r in records if r['tipo'] == 'fuera_de_alcance'
        ],
        'metodo': 'perf_counter_ns alrededor de Retriever.search; RSS actual de /proc/self/status en Linux; sin HTTP ni arranque',
        'advertencia': 'Development is for functional checks, not a new independent headline. No retraining or calibration.',
    }
    args.output.mkdir(parents=True, exist_ok=True)
    cols = [
        'tipo', 'id', 'pregunta', 'articulos_esperados', 'articulos_obtenidos',
        'acierto_top3', 'se_abstuvo', 'tema', 'probabilidad_tema', 'mensaje',
        'latencia_ms', 'rss_actual_mb', 'error_tecnico',
    ]
    with (args.output / 'detalle_funcional.csv').open('w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(records)
    (args.output / 'resumen_funcional.json').write_text(json.dumps(summary, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('observaciones_fuera_de_alcance',)}, indent=2, ensure_ascii=False))
    if structural_failures:
        return 2
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
