"""Stateless tokenization; learned vocabulary is fit only on training questions."""

import re
import unicodedata


def tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)
