"""Train only on the training split; holdouts are never passed to fit."""

from .classifier import TopicClassifier


def train(dataset, path, feature_mode="word"):
    model = TopicClassifier().fit(dataset.training, feature_mode=feature_mode)
    model.save(path, dataset.fingerprint)
    return model
