"""VERB. The verification budget.

An operating model for autonomous AI in project delivery and end to end PMO.

Core claim: AI agents in project management are no longer constrained by model
capability. They are constrained by verification bandwidth, meaning how many agent
decisions an organisation can genuinely review before review becomes rubber-stamping.

    VB = (R * H * u) / c

The README is the specification. This package is a reference implementation of it,
and exists so that nobody has to argue about what the definitions mean.

    from vb.budget import ClassInputs, evaluate_class

    result = evaluate_class(ClassInputs(
        decision_class="C",
        reviewers=6, hours_per_period=8, utilisation=0.55,
        cost_per_decision=1.25, demand=70,
    ))
    result.overdraft_ratio   # 3.31
    result.status            # "overdraft"

Standard library only.
"""

from __future__ import annotations

__version__ = "0.1.0"
__author__ = "Hotragn Pettugani"
__license__ = "Apache-2.0"
__url__ = "https://github.com/hotragn/verb"

__all__ = [
    "__version__",
    "__author__",
    "__license__",
    "__url__",
    "budget",
    "classify",
    "drift",
    "gates",
    "metrics",
]
