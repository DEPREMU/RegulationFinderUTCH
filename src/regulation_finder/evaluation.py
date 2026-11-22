"""Headline denominator includes all answerable questions, including abstentions."""

from dataclasses import asdict


def evaluate(retriever, examples, out_of_scope):
    top_one_hits, hits, abstentions = 0, 0, 0
    details = []
    for example in examples:
        result = retriever.search(example.question)
        displayed = [a.article_id for a in result.articles]
        hit = bool(set(displayed[:3]) & set(example.accepted_article_ids))
        top_one_hit = bool(displayed and displayed[0] in example.accepted_article_ids)
        top_one_hits += top_one_hit
        hits += hit
        abstentions += not displayed
        details.append(
            {
                **asdict(example),
                "predicted_topic": result.topic,
                "topic_probability": result.topic_probability,
                "displayed_article_ids": displayed,
                "abstained": not displayed,
                "top_one_hit": top_one_hit,
                "hit": hit,
            }
        )
    oos_details = []
    for example in out_of_scope:
        result = retriever.search(example.question)
        displayed = [article.article_id for article in result.articles]
        oos_details.append(
            {
                **asdict(example),
                "predicted_topic": result.topic,
                "topic_probability": result.topic_probability,
                "displayed_article_ids": displayed,
                "abstained": not displayed,
            }
        )
    oos_abstentions = sum(row["abstained"] for row in oos_details)
    total, oos_total = len(examples), len(out_of_scope)
    return {
        "eligible_questions": total,
        "top_one_hits": top_one_hits,
        "top_one_hit_rate": top_one_hits / total if total else None,
        "top_three_hits": hits,
        "top_three_hit_rate": hits / total if total else None,
        "answerable_abstentions": abstentions,
        "answerable_abstention_rate": abstentions / total if total else None,
        "out_of_scope_questions": oos_total,
        "out_of_scope_abstentions": oos_abstentions,
        "out_of_scope_abstention_rate": oos_abstentions / oos_total if oos_total else None,
        "out_of_scope_false_returns": oos_total - oos_abstentions,
        "details": details,
        "out_of_scope_details": oos_details,
    }
