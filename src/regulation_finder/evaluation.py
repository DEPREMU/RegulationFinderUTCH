"""Headline denominator includes all answerable questions, including abstentions."""

from dataclasses import asdict


def evaluate(retriever, examples, out_of_scope):
    hits, abstentions = 0, 0
    details = []
    for example in examples:
        result = retriever.search(example.question)
        displayed = [a.article_id for a in result.articles]
        hit = bool(set(displayed[:3]) & set(example.accepted_article_ids))
        hits += hit
        abstentions += not displayed
        details.append({**asdict(example), "displayed_article_ids": displayed, "hit": hit})
    oos_abstentions = sum(not retriever.search(e.question).articles for e in out_of_scope)
    total, oos_total = len(examples), len(out_of_scope)
    return {
        "eligible_questions": total,
        "top_three_hits": hits,
        "top_three_hit_rate": hits / total if total else None,
        "answerable_abstentions": abstentions,
        "answerable_abstention_rate": abstentions / total if total else None,
        "out_of_scope_questions": oos_total,
        "out_of_scope_abstentions": oos_abstentions,
        "out_of_scope_abstention_rate": oos_abstentions / oos_total if oos_total else None,
        "details": details,
    }
