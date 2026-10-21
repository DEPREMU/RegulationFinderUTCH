"""Defaults are demonstration settings, pending development-set calibration."""

from dataclasses import dataclass

FALLBACK = "I don't find this in the regulation"
NOTICE = "Informational only. This application is not an official university source."


@dataclass(frozen=True)
class Settings:
    min_topic_probability: float = 0.55
    min_lexical_score: float = 0.15

    def __post_init__(self):
        for value in (self.min_topic_probability, self.min_lexical_score):
            if not 0 <= value <= 1:
                raise ValueError("Confidence thresholds must be between 0 and 1")
