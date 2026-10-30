"""Finite-calendar counterexamples for the verification budget.

Time is measured in available reviewer minutes. Late reviews remain queued
and eventually complete; a missed deadline is not an unverified approval.
"""

from __future__ import annotations

import argparse
import csv
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal


@dataclass(frozen=True)
class Review:
    identifier: int
    decision_class: str
    arrival: int
    service: int
    deadline: int


@dataclass(frozen=True)
class Completion:
    review: Review
    start: int
    finish: int


def schedule(
    reviews: list[Review], discipline: Literal["fifo", "class_priority"]
) -> list[Completion]:
    """One qualified reviewer, non-preemptive service, unlimited waiting room."""
    remaining = list(reviews)
    completed = []
    now = 0
    priority = {"C": 0, "B": 1}
    while remaining:
        now = max(now, min(review.arrival for review in remaining))
        ready = [review for review in remaining if review.arrival <= now]
        order = lambda review: (review.arrival, review.identifier)
        if discipline == "class_priority":
            order = lambda review: (
                priority[review.decision_class], review.arrival, review.identifier
            )
        review = min(ready, key=order)
        completed.append(Completion(review, now, now + review.service))
        now += review.service
        remaining.remove(review)
    return completed


def summarise(completed: list[Completion], horizon: int) -> dict:
    reviews = [event.review for event in completed]
    return {
        "reviews": len(reviews),
        "offered_minutes": sum(review.service for review in reviews),
        "available_minutes": horizon,
        "offered_load": sum(review.service for review in reviews) / horizon,
        "late_reviews": sum(event.finish > event.review.deadline for event in completed),
        "late_class_c": sum(
            event.review.decision_class == "C" and event.finish > event.review.deadline
            for event in completed
        ),
        "unfinished_minutes_at_deadline": sum(
            max(0, event.finish - max(event.start, horizon)) for event in completed
        ),
        "last_completion": max(event.finish for event in completed),
    }


def reference_cases() -> dict[str, list[Review]]:
    smooth = [Review(i, "C", 120 * i, 96, 2400) for i in range(20)]
    burst = [Review(i, "C", 1920, 96, 2400) for i in range(20)]
    mixed = [Review(i, "B", 1920, 30, 2400) for i in range(32)]
    mixed += [Review(i, "C", 1920, 120, 2400) for i in range(32, 40)]
    return {"smooth": smooth, "burst": burst, "mixed_burst": mixed}


def containment_accounting() -> dict:
    easy = [15] * 80
    hard = [120] * 20
    original = easy + hard
    containment_fraction = len(easy) / len(original)
    return {
        "original_reviews": len(original),
        "contained_reviews": len(easy),
        "original_mean_minutes": sum(original) / len(original),
        "residual_mean_minutes": sum(hard) / len(hard),
        "original_work_minutes": sum(original),
        "residual_work_minutes": sum(hard),
        "constant_mean_estimate_minutes": (1 - containment_fraction) * sum(original),
    }


def build(output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    cases = reference_cases()
    summaries = {}
    traces = []
    for name, reviews in cases.items():
        for discipline in ("fifo", "class_priority"):
            completed = schedule(reviews, discipline)
            summaries[f"{name}/{discipline}"] = summarise(completed, 2400)
            traces.extend(
                {"case": name, "discipline": discipline, **asdict(event)}
                for event in completed
            )
    (output / "reference_results.json").write_text(
        json.dumps({"cases": summaries, "containment": containment_accounting()}, indent=2) + "\n"
    )
    (output / "reference_traces.jsonl").write_text(
        "".join(json.dumps(event) + "\n" for event in traces)
    )
    rows = []
    for service in (30, 60, 90, 114):
        for arrival in (0, 1200, 1920, 2280, 2399):
            reviews = [Review(i, "C", arrival, service, 2400) for i in range(20)]
            completed = schedule(reviews, "fifo")
            rows.append({"arrival_minute": arrival, **summarise(completed, 2400)})
    with (output / "burst_sensitivity.csv").open("w", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path)
    build(parser.parse_args().output)
