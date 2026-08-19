"""Single entrypoint: vb budget | classify | metrics | drift | gates.

Text output by default, ``--json`` for anything downstream. Every command that
reads a bundle prints the synthetic warning if the bundle says it is synthetic,
because a number that gets screenshotted should carry its own caveat.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path
from typing import Any, Callable, Sequence

from . import __version__
from ._io import BundleError, load_bundle
from .budget import (
    BudgetError,
    ClassInputs,
    cost_for_target,
    cost_sensitivity,
    evaluate_class,
    reclassification_share,
    reviewers_for_target,
    utilisation_for_target,
)
from .classify import (
    IncompleteAnswers,
    TREE,
    apply_tiebreakers,
    classify,
    describe_tree,
    format_classification,
    walk,
)
from .drift import drift_report
from .gates import contract_gate, load_contract, run_all
from .metrics import approvals_from_events, compute_all, compute_class

__all__ = ["main", "build_parser"]

RULE = "-" * 72
SYNTHETIC_WARNING = (
    "  These numbers are synthetic. They demonstrate that the arithmetic works "
    "and the tooling reproduces. They are not a measurement of anything."
)


def _dump(payload: Any) -> str:
    def default(value: Any) -> Any:
        if dataclasses.is_dataclass(value) and not isinstance(value, type):
            return dataclasses.asdict(value)
        if isinstance(value, Path):
            return str(value)
        if isinstance(value, float) and value != value:  # NaN
            return None
        return str(value)

    return json.dumps(payload, indent=2, default=default, allow_nan=False)


def _fmt(value: float | None, spec: str = ".2f", missing: str = "n/a") -> str:
    if value is None:
        return missing
    if value == float("inf"):
        return "inf"
    return format(value, spec)


# ---------------------------------------------------------------------------
# vb budget
# ---------------------------------------------------------------------------


def _budget_line(entry: Any, period: str) -> list[str]:
    ratio = entry.overdraft_ratio
    status = entry.status.replace("_", " ").upper()
    lines = [
        f"Class {entry.decision_class}",
        f"  VB                    {_fmt(entry.budget, '9.2f')}  decisions/{period}",
        f"  Demand                {_fmt(entry.demand, '9.2f')}  decisions/{period}",
    ]
    if entry.nominal_cost is not None:
        lines.append(f"  c                     {_fmt(entry.nominal_cost, '9.4g')}  h")
        if entry.containment > 0:
            lines.append(f"  c_eff                 {_fmt(entry.effective_cost, '9.4g')}  h  (k = {entry.containment:.3f})")
    if ratio is None:
        lines.append(f"  Overdraft ratio       {'n/a':>9}")
    else:
        lines.append(f"  Overdraft ratio       {_fmt(ratio, '9.2f')}x")
    lines.append(f"  Status                {status:>9}")
    if entry.unverified_decisions > 0:
        lines.append(
            f"  Unverified            {_fmt(entry.unverified_decisions, '9.2f')}  "
            f"decisions/{period} ({entry.unverified_share * 100:.1f}%)"
        )
    return lines


def cmd_budget(args: argparse.Namespace, out: Callable[[str], None]) -> int:
    if args.input:
        return _budget_from_bundle(args, out)
    return _budget_from_flags(args, out)


def _budget_from_bundle(args: argparse.Namespace, out: Callable[[str], None]) -> int:
    bundle = load_bundle(args.input)
    metrics = compute_all(bundle)

    if args.json:
        out(_dump({
            "bundle": metrics.name,
            "synthetic": metrics.synthetic,
            "period": metrics.period_name,
            "periods": metrics.periods,
            "classes": [dataclasses.asdict(c.budget) for c in metrics.classes],
        }))
        return 0

    out(f"VERB budget: {metrics.name}   {metrics.periods} {metrics.period_name}s of decision log")
    if metrics.synthetic:
        out(SYNTHETIC_WARNING)
    out(RULE)
    header = f"{'class':<6}{'R':>5}{'H':>5}{'u':>7}{'c (h)':>10}{'VB':>11}{'demand':>10}{'O':>9}  status"
    out(header)
    out(RULE)
    for entry in metrics.classes:
        settings = bundle.class_config.get(entry.decision_class, {})
        budget = entry.budget
        ratio = "n/a" if budget.overdraft_ratio is None else f"{budget.overdraft_ratio:.2f}x"
        cost = "n/a" if budget.nominal_cost is None else f"{budget.nominal_cost:.4g}"
        out(
            f"{entry.decision_class:<6}"
            f"{settings.get('reviewers', 0):>5}"
            f"{settings.get('hours_per_period', 0):>5}"
            f"{settings.get('utilisation', 0):>7.2f}"
            f"{cost:>10}"
            f"{budget.budget:>11.1f}"
            f"{budget.demand:>10.1f}"
            f"{ratio:>9}  {budget.status.replace('_', ' ')}"
        )
    out(RULE)

    worst = metrics.worst
    if worst is not None and worst.budget.status == "overdraft":
        entry = worst.budget
        out("")
        out(f"Worst position: Class {entry.decision_class} at {entry.overdraft_ratio:.2f}x.")
        out(
            f"  {entry.unverified_decisions:.0f} of {entry.demand:.0f} decisions per "
            f"{metrics.period_name} have no verification capacity."
        )
        settings = bundle.class_config.get(entry.decision_class, {})
        r = float(settings.get("reviewers", 0))
        h = float(settings.get("hours_per_period", 0))
        u = float(settings.get("utilisation", 0))
        target_c = cost_for_target(r, h, u, entry.demand, 1.0, entry.containment, 0.0)
        target_r = reviewers_for_target(h, u, entry.nominal_cost or 1.0, entry.demand, 1.0, entry.containment)
        share = reclassification_share(entry.demand, entry.budget, 1.0)
        out("")
        out("  What would bring it to O = 1.0, each lever alone:")
        if target_c is not None and entry.nominal_cost:
            cut = (1 - target_c / entry.nominal_cost) * 100
            out(f"    c   {entry.nominal_cost:.3f} h  ->  {target_c:.3f} h   (a {cut:.1f}% cut)")
        if target_r is not None:
            out(f"    R   {r:.0f} reviewers  ->  {target_r:.1f} qualified reviewers")
        target_u = utilisation_for_target(r, h, entry.nominal_cost or 1.0, entry.demand, 1.0, entry.containment)
        if target_u is None:
            out("    u   unreachable, even at 100% utilisation")
        else:
            out(f"    u   {u:.2f}  ->  {target_u:.2f}")
        out(f"    D   reclassify {share * 100:.0f}% of demand to a cheaper class")
        out("")
        out("  No single lever closes an overdraft of 3x. Only c and D have real range,")
        out("  and reclassification means making the decision cheaper to check, not")
        out("  relabelling it.")

    for entry in metrics.classes:
        for note in entry.budget.notes:
            if entry.budget.status in ("overdraft", "policy_violation"):
                out("")
                out(f"  Class {entry.decision_class}: {note}")
                break
    return 0


def _budget_from_flags(args: argparse.Namespace, out: Callable[[str], None]) -> int:
    decision_class = args.decision_class
    cost = None if decision_class == "D" else args.cost
    if decision_class != "D" and cost is None:
        raise BudgetError(
            "--cost is required for classes A, B and C. It must be measured, not "
            "estimated: an estimated c produces a budget that restates your assumptions."
        )

    inputs = ClassInputs(
        decision_class=decision_class,
        reviewers=args.reviewers,
        hours_per_period=args.hours,
        utilisation=args.utilisation,
        cost_per_decision=cost,
        demand=args.demand,
        containment=args.containment,
        agent_check_cost=args.agent_check_cost,
    )
    result = evaluate_class(inputs)

    if args.json:
        payload: dict[str, Any] = dataclasses.asdict(result)
        payload["sensitivity"] = [dataclasses.asdict(p) for p in cost_sensitivity(inputs)]
        out(_dump(payload))
        return 0

    for line in _budget_line(result, args.period):
        out(line)

    if result.nominal_cost is not None and result.demand > 0:
        target_c = cost_for_target(
            args.reviewers, args.hours, args.utilisation, args.demand, 1.0,
            args.containment, args.agent_check_cost,
        )
        target_r = reviewers_for_target(
            args.hours, args.utilisation, result.nominal_cost, args.demand, 1.0,
            args.containment, args.agent_check_cost,
        )
        if target_c is not None:
            cut = (1 - target_c / result.nominal_cost) * 100
            out(f"  c needed for O=1.0    {target_c:9.3f}  h   (a {cut:.1f}% reduction)")
        if target_r is not None:
            out(f"  R needed for O=1.0    {target_r:9.1f}  qualified reviewers")
        share = reclassification_share(args.demand, result.budget, 1.0)
        if share > 0:
            out(f"  D reclassification    {share * 100:9.0f}%  of demand to a cheaper class")

    if args.sensitivity and result.nominal_cost is not None:
        out("")
        out("  Effect of reducing c")
        out(f"  {'c (h)':>10}{'c_eff':>10}{'VB':>10}{'O':>9}  status")
        for point in cost_sensitivity(inputs):
            ratio = "n/a" if point.overdraft_ratio is None else f"{point.overdraft_ratio:.2f}x"
            out(
                f"  {point.nominal_cost:>10.4g}{point.effective_cost:>10.4g}"
                f"{point.budget:>10.1f}{ratio:>9}  {point.status.replace('_', ' ')}"
            )

    for note in result.notes:
        out("")
        out(f"  {note}")
    return 0


# ---------------------------------------------------------------------------
# vb classify
# ---------------------------------------------------------------------------


def cmd_classify(args: argparse.Namespace, out: Callable[[str], None]) -> int:
    if args.tree:
        out(describe_tree())
        return 0

    if args.answers:
        answers: dict[str, bool] = {}
        for pair in args.answers:
            if "=" not in pair:
                raise SystemExit(f"answers must look like q0=no, got {pair!r}")
            key, value = pair.split("=", 1)
            answers[key.strip()] = value.strip().lower() in {"y", "yes", "true", "1"}
        try:
            result = classify(answers)
        except IncompleteAnswers as exc:
            out(f"Need an answer for {exc.node_id}: {exc.prompt}")
            return 2
        if args.second_opinion:
            result = apply_tiebreakers(result, second_opinion=args.second_opinion)
        if args.json:
            out(_dump(dataclasses.asdict(result)))
        else:
            out(format_classification(result, args.decision_type))
        return 0

    if not sys.stdin.isatty():
        out("vb classify is interactive. Pass --answers q0=no q1=yes ... for scripted use,")
        out("or --tree to print the questions.")
        return 2

    result = walk(decision_type=args.decision_type)
    if args.json:
        out(_dump(dataclasses.asdict(result)))
    return 0


# ---------------------------------------------------------------------------
# vb metrics
# ---------------------------------------------------------------------------


def cmd_metrics(args: argparse.Namespace, out: Callable[[str], None]) -> int:
    bundle = load_bundle(args.input)
    metrics = compute_all(bundle)

    if args.json:
        out(_dump({
            "bundle": metrics.name,
            "synthetic": metrics.synthetic,
            "periods": metrics.periods,
            "period": metrics.period_name,
            "classes": [dataclasses.asdict(c) for c in metrics.classes],
        }))
        return 0

    selected = [c for c in metrics.classes if not args.decision_class or c.decision_class == args.decision_class]
    if not selected:
        out(f"No class {args.decision_class} in this bundle.")
        return 2

    out(f"VERB metrics: {metrics.name}   {metrics.periods} {metrics.period_name}s")
    if metrics.synthetic:
        out(SYNTHETIC_WARNING)

    for entry in selected:
        budget = entry.budget
        out("")
        out(RULE)
        out(f"  Class {entry.decision_class}")
        out(RULE)
        out(f"  VB                  {budget.budget:9.2f}  decisions/{metrics.period_name}")
        out(f"  Demand              {budget.demand:9.2f}  decisions/{metrics.period_name}")
        ratio = "n/a" if budget.overdraft_ratio is None else f"{budget.overdraft_ratio:.2f}x"
        out(f"  Overdraft O         {ratio:>9}                 {budget.status.replace('_', ' ').upper()}")
        if budget.unverified_decisions > 0:
            out(f"  Unverified          {budget.unverified_decisions:9.2f}  decisions/{metrics.period_name}")

        if entry.drift:
            drift = entry.drift
            trend = f"{drift.trend.upper()} ({drift.slope:+.3f}/{metrics.period_name})"
            out(f"  SDR                 {drift.drift_rate:9.3f}    excess {drift.excess_drift:.3f}   {trend}")
            out(
                f"  Floor               {drift.floor.hours:9.3f}  h "
                f"({drift.floor.binding_term}, P{drift.floor.percentile_rank:.0f}, n={drift.floor.sample_size})"
            )
        else:
            out("  SDR                       n/a    no approvals or no calibrated floor")

        out(f"  Containment k       {entry.containment.budget_value:9.3f}    {entry.containment.reportable}")
        ep = entry.escalation.precision
        out(f"  Escalation prec.    {_fmt(ep, '9.3f')}    {entry.escalation.escalations} escalations")
        rl = entry.reversal
        if rl.median_hours is None:
            out("  Reversal latency          n/a    no reversals in the window")
        else:
            out(
                f"  Reversal latency    {rl.median_hours:9.1f}  h  (P90 {rl.p90_hours:.1f})"
                f"   breach rate {_fmt(rl.breach_rate, '.2f')}"
            )
        if entry.cost:
            cost = entry.cost
            low, high = cost.interquartile_range
            out(
                f"  c-hat               {cost.hours:9.3f}  h  IQR [{low:.2f}, {high:.2f}]  "
                f"n={cost.sample_size}  measured {cost.measured_at or 'undated'}"
            )
            if cost.discarded_not_genuine:
                out(f"                                 {cost.discarded_not_genuine} observations discarded as not genuine")
        if entry.drift:
            sec = entry.drift.secondary
            out(
                f"  Secondary           CV {sec.coefficient_of_variation:.2f}"
                f"{' COLLAPSED' if sec.variance_collapsed else ' (ok)'}"
                f"   bursts {sec.burst_count} ({sec.burst_share * 100:.1f}% of approvals)"
            )

    out("")
    out("  c-hat is measured under observation. That makes it biased low, which makes")
    out("  VB biased high, which means real overdraft is worse than reported here.")
    out("  Say so when you present these numbers. It costs nothing and it is the")
    out("  difference between a model people trust and a model people trust once.")
    out("  SDR is never used for individual performance management.")
    return 0


# ---------------------------------------------------------------------------
# vb drift
# ---------------------------------------------------------------------------


def cmd_drift(args: argparse.Namespace, out: Callable[[str], None]) -> int:
    bundle = load_bundle(args.input)
    target = args.decision_class
    entry = compute_class(bundle, target)

    if entry.drift is None:
        out(f"No drift report for class {target}: no approvals or no calibrated floor.")
        return 2

    report = entry.drift
    if args.json:
        out(_dump(dataclasses.asdict(report)))
        return 0

    out(f"VERB silent drift: {bundle.name}   class {target}")
    if bundle.synthetic:
        out(SYNTHETIC_WARNING)
    out("")
    floor = report.floor
    out(f"  floor f_{target}          {floor.hours:.4f} h  ({floor.minutes:.1f} min)")
    out(f"    baseline P{floor.percentile_rank:.0f}      {floor.baseline_percentile_hours:.4f} h  (n = {floor.sample_size})")
    out(f"    reading floor    {floor.reading_floor_hours:.4f} h")
    out(f"    binding term     {floor.binding_term}")
    out(f"  baseline drift     {floor.baseline_drift_rate:.2f}  (a P{floor.percentile_rank:.0f} floor yields this when nothing is wrong)")
    out("")
    out(f"  {'period':<10}{'n':>6}{'drift':>8}{'SDR':>9}{'excess':>9}{'median h':>11}{'CV':>7}")
    out(RULE)
    for period in report.periods:
        out(
            f"  {str(period.period):<10}{period.n:>6}{period.drift_count:>8}"
            f"{period.drift_rate:>9.3f}{period.excess_drift:>9.3f}"
            f"{period.median_duration_hours:>11.3f}{period.coefficient_of_variation:>7.2f}"
        )
    out(RULE)
    out(f"  {'overall':<10}{report.n:>6}{report.drift_count:>8}{report.drift_rate:>9.3f}{report.excess_drift:>9.3f}")
    out("")
    out(f"  slope   {report.slope:+.4f} per period")
    out(f"  trend   {report.trend.upper()}")
    out("")
    sec = report.secondary
    out("  Secondary signals, reported alongside, never used as the metric:")
    out(f"    coefficient of variation  {sec.coefficient_of_variation:.3f}"
        f"{'  COLLAPSED, reviews have become uniform' if sec.variance_collapsed else '  (ok)'}")
    out(f"    batch bursts              {sec.burst_count}  covering {sec.approvals_in_bursts} approvals "
        f"({sec.burst_share * 100:.1f}%)")

    if report.diagnostic_signature:
        out("")
        out("  Rising drift. Read this next to the overdraft ratio. The overdraft becomes")
        out("  backlog first, then late nights, then drift, which is why drift lags the")
        out("  overdraft by a month or two and why people conclude it was harmless.")
    out("")
    out("  SDR is never used for individual performance management. Report by class,")
    out("  not by person. A corrupted metric is worse than a missing one.")
    return 0


# ---------------------------------------------------------------------------
# vb gates
# ---------------------------------------------------------------------------


def cmd_gates(args: argparse.Namespace, out: Callable[[str], None]) -> int:
    if args.contract:
        contract = load_contract(args.contract)
        result = contract_gate(contract)
        if args.json:
            out(_dump(dataclasses.asdict(result)))
        else:
            out(result.format())
        return 0 if result.passed else 1

    if not args.input:
        out("vb gates needs --input BUNDLE or --contract FILE.")
        return 2

    bundle = load_bundle(args.input)
    suite = run_all(bundle, only=args.gate)

    if args.json:
        out(_dump({"bundle": bundle.name, "synthetic": bundle.synthetic,
                   "results": [dataclasses.asdict(r) for r in suite.results]}))
        return 0 if suite.passed else 1

    out(f"VERB eval gates: {bundle.name}")
    if bundle.synthetic:
        out(SYNTHETIC_WARNING)
    out("")
    out(suite.format())
    out("")
    if suite.skipped:
        names = ", ".join(f"gate {r.gate}" for r in suite.skipped)
        out(f"  Skipped for want of data: {names}. A skipped gate is not a pass.")
    if suite.blocking_failures:
        names = ", ".join(f"gate {r.gate}" for r in suite.blocking_failures)
        out(f"  Blocking failures: {names}. Gates 1, 2 and 4 block deployment.")
        out("  Gate 3 does not block: a failing verifier keeps running as an advisory")
        out("  annotation and is assigned k = 0.")
    elif suite.passed:
        out("  All gates passed.")
    return 0 if suite.passed else 1


# ---------------------------------------------------------------------------
# Parser
# ---------------------------------------------------------------------------


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vb",
        description=(
            "VERB. The verification budget. Agents are constrained by how many "
            "decisions an organisation can genuinely review, not by model capability."
        ),
        epilog="Specification: https://github.com/hotragn/verb",
    )
    parser.add_argument("--version", action="version", version=f"vb {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    # budget
    p = sub.add_parser("budget", help="verification budget and overdraft, per class")
    p.add_argument("--input", metavar="BUNDLE", help="bundle directory, for example examples/pmo40")
    p.add_argument("--decision-class", default="C", choices=["A", "B", "C", "D"],
                   help="class to size when not reading a bundle")
    p.add_argument("--reviewers", type=float, default=0.0, metavar="R", help="qualified reviewers")
    p.add_argument("--hours", type=float, default=0.0, metavar="H", help="review hours per reviewer per period")
    p.add_argument("--utilisation", type=float, default=0.0, metavar="u", help="0 to 1, measured not chosen")
    p.add_argument("--cost", type=float, default=None, metavar="c", help="measured verification cost per decision, hours")
    p.add_argument("--demand", type=float, default=0.0, metavar="D", help="decisions produced per period")
    p.add_argument("--containment", type=float, default=0.0, metavar="k",
                   help="agentic containment, CI lower bound only, 0 if uncalibrated")
    p.add_argument("--agent-check-cost", type=float, default=0.0, metavar="c_a",
                   help="human hours per decision spent on the verifier's own output")
    p.add_argument("--period", default="period", help="label for the period, for example week")
    p.add_argument("--sensitivity", action="store_true", help="show the effect of reducing c")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_budget)

    # classify
    p = sub.add_parser("classify", help="walk a decision through the A/B/C/D tree")
    p.add_argument("--decision-type", help="name of the decision type being classified")
    p.add_argument("--answers", nargs="*", metavar="qN=yes|no", help="scripted answers, for example q0=no q1=yes")
    p.add_argument("--second-opinion", choices=["A", "B", "C", "D"],
                   help="another classifier's answer, for tie-breaker T2")
    p.add_argument("--tree", action="store_true", help="print the tree and stop")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_classify)

    # metrics
    p = sub.add_parser("metrics", help="all six operating metrics from an event log")
    p.add_argument("--input", required=True, metavar="BUNDLE")
    p.add_argument("--decision-class", choices=["A", "B", "C", "D"], help="limit to one class")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_metrics)

    # drift
    p = sub.add_parser("drift", help="silent drift rate, floor, trend and secondary signals")
    p.add_argument("--input", required=True, metavar="BUNDLE")
    p.add_argument("--decision-class", default="C", choices=["A", "B", "C", "D"])
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_drift)

    # gates
    p = sub.add_parser("gates", help="run the four eval gates")
    p.add_argument("--input", metavar="BUNDLE")
    p.add_argument("--contract", metavar="FILE", help="validate an agent role contract, JSON")
    p.add_argument("--gate", choices=["classification", "evidence", "verifier", "calibration", "replay"],
                   help="run one gate only")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_gates)

    return parser


def main(argv: Sequence[str] | None = None, out: Callable[[str], None] = print) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args, out))
    except (BudgetError, BundleError, ValueError) as exc:
        out(f"error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
