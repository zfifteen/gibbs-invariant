"""Demo package for the Gibbs Regime Switcher."""

from .engine import (
    ArtifactSnapshot,
    CounterfactualMetrics,
    FrameMetrics,
    compute_disruption_index,
    compute_policy_timeline_hash,
    generate_signal,
    load_artifacts,
    load_scenarios,
    run_counterfactual,
    scene_order,
    simulate_policy_timeline,
)

__all__ = [
    "ArtifactSnapshot",
    "CounterfactualMetrics",
    "FrameMetrics",
    "compute_disruption_index",
    "compute_policy_timeline_hash",
    "generate_signal",
    "load_artifacts",
    "load_scenarios",
    "run_counterfactual",
    "scene_order",
    "simulate_policy_timeline",
]
