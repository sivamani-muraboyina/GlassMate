from dataclasses import dataclass
from typing import Iterable

from app.models import RequirementMatchStatus


@dataclass(frozen=True)
class BinaryMetrics:
    precision: float
    recall: float
    f1: float
    support: int


def binary_metrics(expected: Iterable[bool], predicted: Iterable[bool]) -> BinaryMetrics:
    expected_values = list(expected)
    predicted_values = list(predicted)
    if len(expected_values) != len(predicted_values):
        raise ValueError("Expected and predicted labels must have the same length")
    true_positive = sum(actual and guess for actual, guess in zip(expected_values, predicted_values))
    false_positive = sum(not actual and guess for actual, guess in zip(expected_values, predicted_values))
    false_negative = sum(actual and not guess for actual, guess in zip(expected_values, predicted_values))
    precision = true_positive / (true_positive + false_positive) if true_positive + false_positive else 0.0
    recall = true_positive / (true_positive + false_negative) if true_positive + false_negative else 0.0
    f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
    return BinaryMetrics(precision, recall, f1, sum(expected_values))


def requirement_accuracy(
    expected: Iterable[RequirementMatchStatus],
    predicted: Iterable[RequirementMatchStatus],
) -> float:
    expected_values = list(expected)
    predicted_values = list(predicted)
    if len(expected_values) != len(predicted_values):
        raise ValueError("Expected and predicted labels must have the same length")
    if not expected_values:
        return 0.0
    return sum(actual == guess for actual, guess in zip(expected_values, predicted_values)) / len(expected_values)