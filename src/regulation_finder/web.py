"""Flask server for the React frontend and JSON article search."""

from pathlib import Path

from flask import Flask, jsonify, render_template, request, send_from_directory

from .config import FALLBACK


FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"


def create_app(retriever):
    app = Flask(
        __name__,
        static_folder=str(FRONTEND_DIST / "assets"),
        static_url_path="/assets",
        template_folder=str(FRONTEND_DIST),
    )
    app.config["MAX_CONTENT_LENGTH"] = 16384

    @app.route("/", methods=["GET"])
    def index():
        return render_template("index.html")

    @app.route("/favicon.svg", methods=["GET"])
    def favicon():
        return send_from_directory(FRONTEND_DIST, "favicon.svg")

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

        return jsonify(
            {
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
            }
        )

    return app
