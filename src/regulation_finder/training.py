"""Train only on the training split; holdouts are never passed to fit."""

from .classifier import TopicClassifier


def train(dataset, path):
    model = TopicClassifier().fit(dataset.training)
    model.save(path, dataset.fingerprint)
    return model
