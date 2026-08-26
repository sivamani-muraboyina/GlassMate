import json
from pathlib import Path

from app.evaluation.metrics import binary_metrics, requirement_accuracy
from app.models import RequirementMatchStatus


DATASET = Path(__file__).parent / "fixtures" / "evaluation" / "requirement_matches.json"


def test_binary_metrics_report_matching_scores() -> None:
    metrics = binary_metrics([True, True, False, False], [True, False, True, False])

    assert metrics.precision == 0.5
    assert metrics.recall == 0.5
    assert metrics.f1 == 0.5
    assert metrics.support == 2


def test_requirement_accuracy_evaluates_labelled_dataset() -> None:
    rows = json.loads(DATASET.read_text(encoding="utf-8"))
    expected = [RequirementMatchStatus(row["expected"]) for row in rows]
    predicted = [RequirementMatchStatus(row["predicted"]) for row in rows]

    assert requirement_accuracy(expected, predicted) == 0.75