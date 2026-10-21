"""Server-rendered, autoescaped article display; no generated answers."""

from flask import Flask, render_template, request

from .config import NOTICE


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

    return app
