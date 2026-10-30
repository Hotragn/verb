"""Compare the event scheduler with analytic counts and a minute-clock oracle."""

from __future__ import annotations

import random

import pytest

from examples.queueing import (
    Review,
    containment_accounting,
    reference_cases,
    schedule,
    summarise,
)


def minute_clock(reviews: list[Review], discipline: str) -> dict[int, int]:
    waiting = list(reviews)
    completion = {}
    running = None
    remaining = 0
    now = 0
    while waiting or running is not None:
        if running is None:
            ready = [review for review in waiting if review.arrival <= now]
            if ready:
                if discipline == "class_priority":
                    ready.sort(key=lambda review: (review.decision_class != "C", review.arrival, review.identifier))
                else:
                    ready.sort(key=lambda review: (review.arrival, review.identifier))
                running = ready[0]
                waiting.remove(running)
                remaining = running.service
        now += 1
        if running is not None:
            remaining -= 1
            if remaining == 0:
                completion[running.identifier] = now
                running = None
    return completion


def test_equal_load_different_deadline_outcomes():
    cases = reference_cases()
    smooth = summarise(schedule(cases["smooth"], "fifo"), 2400)
    burst = summarise(schedule(cases["burst"], "fifo"), 2400)
    assert smooth["offered_load"] == burst["offered_load"] == 0.8
    assert smooth["late_reviews"] == 0
    assert burst["late_reviews"] == 15
    assert burst["unfinished_minutes_at_deadline"] == 1440


def test_priority_exposes_class_tradeoff():
    reviews = reference_cases()["mixed_burst"]
    fifo = summarise(schedule(reviews, "fifo"), 2400)
    priority = summarise(schedule(reviews, "class_priority"), 2400)
    assert (fifo["late_reviews"], fifo["late_class_c"]) == (24, 8)
    assert (priority["late_reviews"], priority["late_class_c"]) == (36, 4)


def test_containment_reduces_total_work_but_changes_mean():
    result = containment_accounting()
    assert result["original_mean_minutes"] == 36
    assert result["residual_mean_minutes"] == 120
    assert result["original_work_minutes"] == 3600
    assert result["residual_work_minutes"] == 2400
    assert result["constant_mean_estimate_minutes"] == pytest.approx(720)


@pytest.mark.parametrize("discipline", ["fifo", "class_priority"])
def test_scheduler_matches_independent_minute_clock(discipline):
    rng = random.Random(20261030)
    for _ in range(100):
        reviews = [
            Review(i, rng.choice(["B", "C"]), rng.randrange(40), rng.randrange(1, 12), 60)
            for i in range(12)
        ]
        actual = {event.review.identifier: event.finish for event in schedule(reviews, discipline)}
        assert actual == minute_clock(reviews, discipline)


def test_deadline_equality_and_nonpreemption():
    reviews = [Review(0, "B", 0, 10, 10), Review(1, "C", 1, 1, 10)]
    result = schedule(reviews, "class_priority")
    assert [event.finish for event in result] == [10, 11]
    assert summarise(result, 10)["late_reviews"] == 1
