"""Stateless tokenization; learned vocabulary is fit only on training questions."""

import re
import unicodedata

SPANISH_STOPWORDS = frozenset(
    """
    a al algo ante bajo con contra cual cuando de del desde donde el ella ellas ellos en entre
    era es esa ese eso esta este esto fue ha hay la las le les lo los mas me mi mis no nos o
    para pero por porque que se ser si sin sobre son su sus te tu tus un una uno unas unos y ya
    como quien quienes
    """.split()
)


def tokens(text: str) -> list[str]:
    normalized = unicodedata.normalize("NFKD", text.casefold())
    normalized = "".join(c for c in normalized if not unicodedata.combining(c))
    return re.findall(r"[^\W_]+", normalized, flags=re.UNICODE)


def content_tokens(text: str) -> list[str]:
    """Return lightweight Spanish content tokens for optional lexical profiles."""
    return [token for token in tokens(text) if token not in SPANISH_STOPWORDS]


def character_features(words: list[str] | set[str]) -> list[str]:
    """Return prefixed character four-grams for light morphological matching."""
    return [
        f"char4={word[index : index + 4]}"
        for word in words
        if len(word) >= 5
        for index in range(len(word) - 3)
    ]


def morphological_features(words: list[str] | set[str]) -> list[str]:
    """Add conservative suffix features for common Spanish inflections."""
    features = []
    for word in words:
        if len(word) >= 5 and word[-1] in "aeo":
            features.append(f"stem={word[:-1]}")
        if len(word) >= 6 and word.endswith("s"):
            features.append(f"stem={word[:-1]}")
    return features


def classification_features(text: str, mode: str = "word") -> list[str]:
    words = tokens(text)
    if mode == "word":
        return words
    if mode == "word_stem":
        return [*words, *morphological_features(content_tokens(text))]
    if mode == "word_char4":
        return [*words, *character_features(content_tokens(text))]
    raise ValueError(f"Unknown feature mode: {mode}")
