
"""Server-rendered and JSON article search; no generated answers."""

from flask import Flask, jsonify, render_template, request

from .config import FALLBACK, NOTICE


def create_app(retriever):
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = 16384

    @app.route("/", methods=["GET", "POST"])
    def index():
        question = request.form.get("question", "") if request.method == "POST" else ""
        result = retriever.search(question) if request.method == "POST" else None
        return render_template(
            "index.html",
            question=question,
            result=result,
            notice=NOTICE,
            synthetic=retriever.dataset.metadata["synthetic"],
        )

    @app.route("/api/search", methods=["POST"])
    def api_search():
        data = request.get_json(silent=True)

        if not isinstance(data, dict):
            return jsonify({"error": "A JSON object is required."}), 400

        question = data.get("question")

        if not isinstance(question, str) or not question.strip():
            return jsonify({"error": "A nonempty question is required."}), 400

        result = retriever.search(question.strip())

        if result.articles:
            status = "ok"
        elif result.topic_probability < retriever.settings.min_topic_probability:
            status = "low_match"
        else:
            status = "empty"

        return jsonify({
            "status": status,
            "suggestion": FALLBACK if status == "low_match" else "",
            "articles": [
                {
                    "article_id": article.article_id,
                    "text": article.text,
                    "topic": article.topic,
                    "source": article.source,
                }
                for article in result.articles[:3]
            ],
        })

    return app
