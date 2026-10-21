# Data contracts and permission

**School regulation permission: PENDING**, to be confirmed with the instructor by Karen. Regulation source/version, authorized text, collection date and redistribution terms: PENDING. Software licensing: team decision pending. No real regulation is included. Never copy material without resolved permission. Keep personal information out of committed data; use non-identifying author/team references.

Each dataset directory contains UTF-8 JSON files. Each table is an array of objects; unknown/missing fields, blank text and duplicate IDs are rejected. Identifiers are strings (preserve numbering and leading zeros). CLI: `uv run --frozen regulation-finder --data data/synthetic validate`.

| File | Required object fields |
| --- | --- |
| articles.json | article_id: string; text: exact original string; topic: string; source: source reference string |
| training.json | example_id: string; question: string; topic: string; provenance: author/source string |
| development.json | question_id: string; question: string; accepted_article_ids: nonempty array of strings; provenance: string |
| evaluation.json | Same as development; real questions require another team's provenance |
| out_of_scope.json | Same fields, but accepted_article_ids must be an empty array |
| metadata.json | dataset_id: string; synthetic: boolean; permission_status: string; evaluation_origin: string |

Training labels must cover exactly the article topics; unknown topics and unknown accepted article IDs are invalid. Question IDs must be unique across splits and normalized duplicate questions are rejected, including train/holdout leakage. Empty development/test arrays are permitted for collection work; their metrics are null, not zero. This structural check cannot prove external authorship, semantic independence, permission or absence of paraphrase leakage: human review is mandatory.

Karen records full source title, version/date, page/article location and permission evidence separately before collecting the real article table. Put specific source locators in each article's source field. Keep one row per article; retain punctuation, spacing and line breaks in text. Search tokenization never overwrites text. Review transcriptions against the source, agree topic definitions, and resolve ambiguous labels with the team before freezing the dataset.

Collect training/development questions separately; split and review before tuning. Only training questions fit the vocabulary and classifier. Another team writes at least 60 independent answerable evaluation questions, with one or more accepted IDs, plus separate out-of-scope cases. Emanuel checks provenance, independence and relevance without using test results for tuning. Freeze the files and hashes before final evaluation. Do not commit names/emails or sensitive records. Real local work can use ignored data/real until permission and privacy review allows redistribution.

The supplied synthetic dataset has six invented articles, eight training questions, two development questions, three evaluation questions and two out-of-scope questions. All were written as smoke fixtures; none count toward external evaluation. No official article numbering or rules are implied.
