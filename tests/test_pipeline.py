import json
import shutil
from dataclasses import replace

import numpy as np
import pytest

from regulation_finder.classifier import TopicClassifier
from regulation_finder.cli import main
from regulation_finder.config import FALLBACK, Settings
from regulation_finder.evaluation import evaluate
from regulation_finder.measurements import measure
from regulation_finder.retrieval import Retriever
from regulation_finder.schemas import Article, EvaluationExample, TrainingExample, load_dataset
from regulation_finder.web import create_app


def test_naive_bayes_counts_and_serialization(tmp_path):
    examples = [
        TrainingExample("1", "red red blue", "a", "synthetic"),
        TrainingExample("2", "green", "b", "synthetic"),
    ]
    model = TopicClassifier().fit(examples)
    # Sorted vocabulary: blue, green, red. Laplace counts for a: 2, 1, 3.
    np.testing.assert_allclose(np.exp(model.log_likelihood[0]), [2 / 6, 1 / 6, 3 / 6])
    np.testing.assert_allclose(np.exp(model.log_prior), [0.5, 0.5])
    assert model.predict("red")[0] == "a"
    assert "unseen" not in model.vocabulary
    path = tmp_path / "model.json"
    model.save(path, "fixture")
    loaded = TopicClassifier.load(path, "fixture")
    assert loaded.predict("red red") == model.predict("red red")
    with pytest.raises(ValueError, match="fingerprint"):
        TopicClassifier.load(path, "different")


def test_ranking_exact_text_and_top_three(retriever):
    result = retriever.search("library books return receipt")
    assert result.articles[0].article_id == "SYN-L2"
    assert result.articles[0].text.endswith("desk.\nKeep the receipt.")
    assert len(result.articles) == 3
    tied = retriever.search("library books")
    assert [a.article_id for a in tied.articles] == ["SYN-L1", "SYN-L2", "SYN-L3"]
    assert all(a.topic == "library" for a in result.articles)


@pytest.mark.parametrize("question", ["", "   ", "!?", "orbital banana spaceship"])
def test_empty_and_unsupported(retriever, question):
    result = retriever.search(question)
    assert result.articles == []
    assert result.message


def test_gates_and_small_candidate_pool(dataset, retriever):
    strict = Retriever(dataset, retriever.model, Settings(1.0, 1.0))
    assert strict.search("library books").message == FALLBACK
    # High topic probability is insufficient when there is no lexical match.
    changed = replace(dataset, articles=[replace(a, text="unrelated") for a in dataset.articles])
    assert Retriever(changed, retriever.model).search("library books").message == FALLBACK
    assert len(retriever.search("laboratory experiments").articles) == 2
    assert retriever.search("laboratory goggles").articles[0].article_id == "SYN-C1"
    with pytest.raises(ValueError):
        Settings(-0.1, 0.2)


def test_evaluation_denominator_and_abstentions(retriever):
    rows = [
        EvaluationExample("a", "library books return receipt", ["SYN-L2"], "synthetic"),
        EvaluationExample("b", "spaceship", ["SYN-L1"], "synthetic"),
    ]
    report = evaluate(retriever, rows, retriever.dataset.out_of_scope)
    assert report["eligible_questions"] == 2
    assert report["top_three_hits"] == 1
    assert report["top_three_hit_rate"] == 0.5
    assert report["answerable_abstentions"] == 1
    assert report["out_of_scope_questions"] == 2
    assert report["out_of_scope_abstentions"] == 2
    assert evaluate(retriever, [], [])["top_three_hit_rate"] is None


@pytest.mark.parametrize(
    "mutation",
    [
        "missing",
        "duplicate",
        "topic",
        "reference",
        "leakage",
        "numeric_id",
        "empty_accepted",
        "oos_accepted",
        "metadata",
        "bad_list",
        "duplicate_cross_id",
        "empty_articles",
    ],
)
def test_validation_rejects_bad_data(data_path, tmp_path, mutation):
    directory = tmp_path / "data"
    shutil.copytree(data_path, directory)
    filename = "articles"
    rows = json.loads((directory / "articles.json").read_text())
    if mutation == "missing":
        del rows[0]["source"]
    elif mutation == "duplicate":
        rows.append(rows[0])
    elif mutation == "numeric_id":
        rows[0]["article_id"] = 1
    elif mutation == "empty_articles":
        rows = []
    else:
        filename = "training" if mutation == "topic" else "evaluation"
        rows = json.loads((directory / f"{filename}.json").read_text())
        if mutation == "topic":
            rows[0]["topic"] = "unknown"
        elif mutation == "reference":
            rows[0]["accepted_article_ids"] = ["UNKNOWN"]
        elif mutation == "empty_accepted":
            rows[0]["accepted_article_ids"] = []
        elif mutation == "bad_list":
            rows[0]["accepted_article_ids"] = "SYN-L1"
        elif mutation == "leakage":
            rows[0]["question"] = "How can I borrow library books?"
        elif mutation == "duplicate_cross_id":
            rows[0]["question_id"] = "SYN-T1"
        elif mutation == "oos_accepted":
            filename = "out_of_scope"
            rows = json.loads((directory / "out_of_scope.json").read_text())
            rows[0]["accepted_article_ids"] = ["SYN-L1"]
        else:
            filename, rows = "metadata", {"synthetic": "yes"}
    (directory / f"{filename}.json").write_text(json.dumps(rows))
    with pytest.raises(ValueError):
        load_dataset(directory)


def test_web_notices_search_empty_fallback_and_escaping(dataset, retriever):
    client = create_app(retriever).test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert b"Informational only" in response.data
    assert b"SYNTHETIC DEMO DATA" in response.data
    result = client.post("/", data={"question": "library books return receipt"})
    assert b"Article SYN-L2" in result.data
    assert b"desk.\nKeep the receipt." in result.data
    assert b"Enter a question" in client.post("/", data={"question": ""}).data
    assert b"I don&#39;t find" in client.post("/", data={"question": "spaceship"}).data
    altered = replace(
        dataset, articles=[Article("X", "library <script>bad()</script>", "library", "synthetic")]
    )

    class FixedModel:
        labels = ["library"]

        def predict(self, question):
            return "library", 1.0

    safe_client = create_app(Retriever(altered, FixedModel())).test_client()
    assert b"&lt;script&gt;" in safe_client.post("/", data={"question": "library"}).data


def test_cli_end_to_end_and_missing_artifact(data_path, tmp_path, capsys):
    model = str(tmp_path / "model.json")
    prefix = ["--data", str(data_path), "--model", model]
    with pytest.raises(SystemExit) as error:
        main([*prefix, "search", "library"])
    assert error.value.code == 2
    assert "train the model first" in capsys.readouterr().err
    for command in (
        ["validate"],
        ["train"],
        ["search", "library books"],
        ["evaluate"],
        ["evaluate", "--split", "development"],
        ["measure", "--iterations", "3", "--hardware-label", "test host"],
    ):
        assert main([*prefix, *command]) == 0
        assert json.loads(capsys.readouterr().out)["synthetic"] is True


def test_model_rejects_corrupt_parameters(tmp_path, dataset):
    path = tmp_path / "model.json"
    TopicClassifier().fit(dataset.training).save(path, dataset.fingerprint)
    raw = json.loads(path.read_text())
    raw["log_prior"] = [0]
    path.write_text(json.dumps(raw))
    with pytest.raises(ValueError, match="dimensions"):
        TopicClassifier.load(path, dataset.fingerprint)


def test_training_excludes_holdout_vocabulary(dataset):
    model = TopicClassifier().fit(dataset.training)
    assert "receipt" not in model.vocabulary  # Present only in article/evaluation text.
    assert "goggles" in model.vocabulary


def test_measurement_validation(retriever):
    with pytest.raises(ValueError):
        measure(retriever, [], "unused", 0, "test")
