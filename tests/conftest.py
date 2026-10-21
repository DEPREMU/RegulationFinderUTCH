from pathlib import Path

import pytest

from regulation_finder.classifier import TopicClassifier
from regulation_finder.retrieval import Retriever
from regulation_finder.schemas import load_dataset


@pytest.fixture
def data_path():
    return Path(__file__).resolve().parents[1] / "data" / "synthetic"


@pytest.fixture
def dataset(data_path):
    return load_dataset(data_path)


@pytest.fixture
def retriever(dataset):
    return Retriever(dataset, TopicClassifier().fit(dataset.training))
