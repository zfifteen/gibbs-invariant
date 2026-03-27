"""Dash application for the Gibbs Regime Switcher demo."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Mapping, Tuple

import dash
import numpy as np
import plotly.graph_objects as go
from dash import Input, Output, State, callback_context, dcc, html

from gibbs_invariant.metrics import compute_jump_indices, fft_partial_sum, uniform_grid, zone_mask_from_jumps

from .engine import (
    ArtifactSnapshot,
    analyze_signal,
    compute_disruption_index,
    generate_signal,
    load_artifacts,
    load_scenarios,
    run_counterfactual,
    scenario_to_config,
)

SCENE_DURATION_SEC = 10

STORY_SCENES: Tuple[Dict[str, str], ...] = (
    {"label": "Invariant Convergence", "scenario_id": "invariant_convergence"},
    {"label": "N1 Crossover", "scenario_id": "n1_crossover"},
    {"label": "Noise/Jitter Stress", "scenario_id": "noisy_discontinuity"},
    {"label": "Closure-Matched Smooth Control", "scenario_id": "bandlimited_edge"},
    {"label": "Codec Routing Economics", "scenario_id": "step_function"},
    {"label": "Deployment Bridge (mozjpeg)", "scenario_id": "nonuniform_sampling"},
)

MODULE_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = MODULE_DIR.parent
DEFAULT_SCENARIO_DIR = MODULE_DIR / "scenarios"
DEFAULT_RESULTS_DIR = PROJECT_ROOT / "results"


def _bootstrap_data() -> Tuple[Dict[str, Dict[str, Any]], ArtifactSnapshot | None, str | None]:
    scenarios = load_scenarios(DEFAULT_SCENARIO_DIR)
    try:
        artifacts = load_artifacts(str(DEFAULT_RESULTS_DIR))
        return scenarios, artifacts, None
    except Exception as exc:  # pragma: no cover - exercised by runtime state
        return scenarios, None, str(exc)


SCENARIOS, ARTIFACTS, ARTIFACT_ERROR = _bootstrap_data()


def _status_chip(ok: bool) -> str:
    return "status-pass" if ok else "status-fail"


def _status_label(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def _build_reconstruction_figure(signal: np.ndarray, n_values: Tuple[int, ...]) -> go.Figure:
    x = uniform_grid(signal.size)
    n_low = max(4, min(n_values))
    n_high = max(n_values)

    recon_low = fft_partial_sum(signal, n_harmonics=n_low)
    recon_high = fft_partial_sum(signal, n_harmonics=n_high)

    jump_indices = compute_jump_indices(signal, top_k=2)
    zone_mask = zone_mask_from_jumps(signal.size, jump_indices, n_harmonics=n_high, alpha=1.0)

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=x, y=signal, name="Observed", line={"color": "#42e9f5", "width": 2}))
    fig.add_trace(
        go.Scatter(
            x=x,
            y=recon_low,
            name=f"Smooth Path (N={n_low})",
            line={"color": "#9cc9ff", "width": 1.6, "dash": "dot"},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=recon_high,
            name=f"Expensive Path (N={n_high})",
            line={"color": "#ff8c42", "width": 2},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=x,
            y=np.where(zone_mask, np.max(signal) * 1.12, np.nan),
            mode="markers",
            name="Edge Routing Zone",
            marker={"size": 3.2, "color": "#ff5d5d", "opacity": 0.6},
        )
    )
    fig.update_layout(
        margin={"l": 12, "r": 12, "t": 24, "b": 28},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(3,13,24,0.55)",
        font={"family": "IBM Plex Mono, monospace", "color": "#dce6ff", "size": 11},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0.0},
        xaxis_title="x",
        yaxis_title="Amplitude",
    )
    fig.update_xaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    fig.update_yaxes(showgrid=True, gridcolor="rgba(255,255,255,0.08)")
    return fig


def _build_regime_map(signal: np.ndarray, scenario: Mapping[str, Any], frame: Any) -> go.Figure:
    n_values = [int(v) for v in scenario["n_values"]]
    jump_scores: List[float] = []
    energy_vals: List[float] = []

    for n in n_values:
        cfg = {"n_values": (n,), "alpha": float(scenario["alpha"]), "jump_threshold": float(scenario["jump_threshold"]), "noise_policy": "robust"}
        frame = analyze_signal(signal, cfg)
        jump_scores.append(frame.jump_score)
        energy_vals.append(frame.energy_redistribution)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=n_values,
            y=jump_scores,
            mode="lines+markers",
            name="Jump Score",
            line={"color": "#42e9f5", "width": 2},
            marker={"size": 7},
        )
    )
    fig.add_trace(
        go.Scatter(
            x=n_values,
            y=energy_vals,
            mode="lines+markers",
            name="Energy Redistribution",
            line={"color": "#ffb347", "width": 2},
            marker={"size": 7},
            yaxis="y2",
        )
    )
    fig.add_hline(y=float(scenario["jump_threshold"]), line_dash="dot", line_color="#8fffd6", annotation_text="jump threshold")
    fig.update_layout(
        margin={"l": 14, "r": 16, "t": 24, "b": 28},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(3,13,24,0.55)",
        font={"family": "IBM Plex Mono, monospace", "color": "#dce6ff", "size": 11},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0.0},
        annotations=[
            {
                "x": 0.99,
                "y": 1.16,
                "xref": "paper",
                "yref": "paper",
                "xanchor": "right",
                "showarrow": False,
                "font": {"size": 12, "color": "#a9ffe2"},
                "text": f"closure_ratio={frame.closure_ratio:.3f}",
            }
        ],
        xaxis={"title": "Harmonic Budget N", "showgrid": True, "gridcolor": "rgba(255,255,255,0.08)"},
        yaxis={"title": "Jump Score", "showgrid": True, "gridcolor": "rgba(255,255,255,0.08)"},
        yaxis2={
            "title": "Energy Redistribution",
            "overlaying": "y",
            "side": "right",
            "range": [0.0, 1.0],
            "showgrid": False,
        },
    )
    return fig


def _build_counterfactual_figure(counter: Any, disruption_index: float) -> go.Figure:
    fig = go.Figure()
    labels = ["Edge MSE", "Smooth MSE", "Compute Cost"]
    baseline = [counter.baseline_edge_mse, counter.baseline_smooth_mse, counter.baseline_cost]
    routed = [counter.routed_edge_mse, counter.routed_smooth_mse, counter.routed_cost]
    fig.add_trace(go.Bar(name="Baseline", x=labels, y=baseline, marker_color="#5d7eff"))
    fig.add_trace(go.Bar(name="Routed", x=labels, y=routed, marker_color="#ff8c42"))
    fig.update_layout(
        barmode="group",
        margin={"l": 14, "r": 12, "t": 24, "b": 28},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(3,13,24,0.55)",
        font={"family": "IBM Plex Mono, monospace", "color": "#dce6ff", "size": 11},
        legend={"orientation": "h", "yanchor": "bottom", "y": 1.02, "x": 0.0},
        xaxis={"showgrid": False},
        yaxis={"title": "Magnitude (lower is better)", "showgrid": True, "gridcolor": "rgba(255,255,255,0.08)"},
        annotations=[
            {
                "x": 0.99,
                "y": 1.16,
                "xref": "paper",
                "yref": "paper",
                "xanchor": "right",
                "showarrow": False,
                "font": {"size": 12, "color": "#a9ffe2"},
                "text": f"Disruption Index: {disruption_index:.1f}/100",
            }
        ],
    )
    return fig


def _validated_items(snapshot: ArtifactSnapshot | None) -> List[html.Li]:
    if snapshot is None:
        return [html.Li("Artifacts unavailable: validated section disabled.")]

    phase2b = bool(snapshot.pipeline_summary["phase2"]["phase2b_gates"]["all_pass"])
    phase3 = bool(snapshot.pipeline_summary["phase3"]["pass"])
    phase4 = bool(snapshot.pipeline_summary["phase4"]["selection_unblocked"])
    selected = snapshot.pipeline_summary["phase4"]["selected_target"]["name"]
    mean_drift = snapshot.pipeline_summary["phase2"]["phase2b_gates"]["noise_robustness"]["production_mean_score_drift"]
    top = snapshot.candidate_rankings[0]

    return [
        html.Li(f"Phase 2b falsification gates: {_status_label(phase2b)}"),
        html.Li(f"Phase 3 constrained prototype: {_status_label(phase3)}"),
        html.Li(f"Phase 4 selection unblocked: {_status_label(phase4)}"),
        html.Li(f"Selected target from ranking: {selected} (top score={top['score']:.3f})"),
        html.Li(f"Noise robustness production mean drift: {mean_drift:.4f}"),
    ]


def _roadmap_items() -> List[html.Li]:
    return [
        html.Li("Wire the proxy router into mozjpeg block decision hooks behind a feature flag."),
        html.Li("Calibrate thresholds on domain corpora before any production-quality claims."),
        html.Li("Add external A/B benchmarking gates (runtime + perceptual metrics)."),
    ]


def _evidence_ledger(snapshot: ArtifactSnapshot | None, error: str | None) -> html.Div:
    if error:
        return html.Div(
            className="ledger-error",
            children=[
                html.Div("Artifact Validation Error", className="ledger-title"),
                html.P(error),
                html.P("Expected files: pipeline_summary.json, gates_report.json, constrained_metrics.json, candidate_rankings.csv"),
            ],
        )

    assert snapshot is not None
    statuses = [
        html.Div(
            className="artifact-row",
            children=[
                html.Span(s.name, className="artifact-name"),
                html.Span(_status_label(s.ok), className=f"artifact-chip {_status_chip(s.ok)}"),
                html.Span(s.timestamp_utc, className="artifact-ts"),
            ],
        )
        for s in snapshot.statuses
    ]
    phase2b = bool(snapshot.pipeline_summary["phase2"]["phase2b_gates"]["all_pass"])
    phase3 = bool(snapshot.pipeline_summary["phase3"]["pass"])
    phase4 = bool(snapshot.pipeline_summary["phase4"]["selection_unblocked"])

    return html.Div(
        children=[
            html.Div(
                className="artifact-gates",
                children=[
                    html.Div(["Phase 2b ", html.Span(_status_label(phase2b), className=f"artifact-chip {_status_chip(phase2b)}")]),
                    html.Div(["Phase 3 ", html.Span(_status_label(phase3), className=f"artifact-chip {_status_chip(phase3)}")]),
                    html.Div(["Phase 4 ", html.Span(_status_label(phase4), className=f"artifact-chip {_status_chip(phase4)}")]),
                ],
            ),
            html.Div(statuses, className="artifact-list"),
            html.H4("Validated"),
            html.Ul(_validated_items(snapshot)),
            html.H4("Roadmap"),
            html.Ul(_roadmap_items()),
        ]
    )


def _scene_caption(mode: str, scene_label: str, scenario: Mapping[str, Any], frame: Any, counter: Any, disruption_index: float) -> str:
    if mode == "story":
        return (
            f"{scene_label} | closure_ratio={frame.closure_ratio:.3f} | "
            f"jump_score={frame.jump_score:.3f} (threshold={frame.threshold_used:.3f}) | energy={frame.energy_redistribution:.3f} | "
            f"quality_gain={counter.quality_gain:.5f} | speed_gain={counter.speed_gain:.2%} | "
            f"disruption_index={disruption_index:.1f}"
        )
    return (
        f"Explore: {scenario['title']} | closure_ratio={frame.closure_ratio:.3f} | jump_active={frame.jump_active} | "
        f"smooth_penalty={counter.smooth_penalty:.6f} | routed_cost={counter.routed_cost:.2f}"
    )


def create_app() -> dash.Dash:
    app = dash.Dash(
        __name__,
        title="Gibbs Regime Switcher",
        external_stylesheets=[
            "https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=IBM+Plex+Mono:wght@400;500;700&display=swap"
        ],
    )

    default_scenario = STORY_SCENES[0]["scenario_id"]
    app.layout = html.Div(
        className="app-root",
        children=[
            dcc.Store(id="playback-store", data={"playing": True, "scene_idx": 0, "scene_t": 0.0, "global_t": 0.0}),
            dcc.Interval(id="story-timer", interval=1000, n_intervals=0),
            html.Div(
                className="hero",
                children=[
                    html.Div("GIBBS REGIME SWITCHER", className="hero-kicker"),
                    html.H1("From Spectral Ringing to Real-Time Routing Decisions"),
                    html.P(
                        "Hybrid story + live controls. Evidence-first diagnostics converted into quality-speed policy outputs."
                    ),
                ],
            ),
            html.Div(
                className="control-bar",
                children=[
                    html.Div(
                        className="control-group",
                        children=[
                            html.Label("Mode", className="control-label"),
                            dcc.RadioItems(
                                id="mode-selector",
                                options=[
                                    {"label": "Story", "value": "story"},
                                    {"label": "Explore", "value": "explore"},
                                ],
                                value="story",
                                className="mode-radio",
                                inline=True,
                            ),
                        ],
                    ),
                    html.Div(
                        className="control-group",
                        children=[
                            html.Label("Replay", className="control-label"),
                            html.Div(
                                className="button-row",
                                children=[
                                    html.Button("Play", id="btn-play", n_clicks=0),
                                    html.Button("Pause", id="btn-pause", n_clicks=0),
                                    html.Button("Step", id="btn-step", n_clicks=0),
                                    html.Button("Reset", id="btn-reset", n_clicks=0),
                                ],
                            ),
                        ],
                    ),
                    html.Div(
                        className="control-group",
                        children=[
                            html.Label("Explore Scenario", className="control-label"),
                            dcc.Dropdown(
                                id="explore-scenario",
                                options=[{"label": v["title"], "value": k} for k, v in SCENARIOS.items()],
                                value=default_scenario,
                                clearable=False,
                            ),
                        ],
                    ),
                    html.Div(
                        className="control-group time-slider-group",
                        children=[
                            html.Label("Explore Time", className="control-label"),
                            dcc.Slider(
                                id="explore-time",
                                min=0.0,
                                max=20.0,
                                step=0.5,
                                value=0.0,
                                tooltip={"placement": "bottom", "always_visible": False},
                            ),
                        ],
                    ),
                ],
            ),
            html.Div(id="scene-caption", className="scene-caption"),
            html.Div(
                className="panel-grid",
                children=[
                    html.Div(
                        className="panel panel-recon",
                        children=[html.H3("Reconstruction Theater"), dcc.Graph(id="fig-reconstruction", config={"displayModeBar": False})],
                    ),
                    html.Div(
                        className="panel panel-regime",
                        children=[html.H3("Regime Map"), dcc.Graph(id="fig-regime", config={"displayModeBar": False})],
                    ),
                    html.Div(
                        className="panel panel-score",
                        children=[
                            html.H3("Counterfactual Scoreboard"),
                            dcc.Graph(id="fig-counterfactual", config={"displayModeBar": False}),
                            html.Div(id="policy-breakdown", className="policy-breakdown"),
                        ],
                    ),
                    html.Div(
                        className="panel panel-ledger",
                        children=[html.H3("Evidence Ledger"), html.Div(id="evidence-ledger")],
                    ),
                ],
            ),
        ],
    )

    @app.callback(
        Output("playback-store", "data"),
        [
            Input("story-timer", "n_intervals"),
            Input("btn-play", "n_clicks"),
            Input("btn-pause", "n_clicks"),
            Input("btn-step", "n_clicks"),
            Input("btn-reset", "n_clicks"),
            Input("mode-selector", "value"),
        ],
        [State("playback-store", "data")],
    )
    def update_playback(
        _tick: int,
        _play_clicks: int,
        _pause_clicks: int,
        _step_clicks: int,
        _reset_clicks: int,
        mode: str,
        current: Mapping[str, Any] | None,
    ) -> Dict[str, Any]:
        state = dict(current or {"playing": True, "scene_idx": 0, "scene_t": 0.0, "global_t": 0.0})
        trigger = callback_context.triggered[0]["prop_id"].split(".")[0] if callback_context.triggered else ""

        if trigger == "btn-play":
            state["playing"] = True
            return state
        if trigger == "btn-pause":
            state["playing"] = False
            return state
        if trigger == "btn-step":
            state["scene_idx"] = (int(state["scene_idx"]) + 1) % len(STORY_SCENES)
            state["scene_t"] = 0.0
            state["global_t"] = float(state["scene_idx"]) * SCENE_DURATION_SEC
            state["playing"] = False
            return state
        if trigger == "btn-reset":
            return {"playing": mode == "story", "scene_idx": 0, "scene_t": 0.0, "global_t": 0.0}
        if trigger == "mode-selector" and mode == "explore":
            state["playing"] = False
            return state

        if mode == "story" and bool(state.get("playing", False)):
            scene_t = float(state.get("scene_t", 0.0)) + 1.0
            scene_idx = int(state.get("scene_idx", 0))
            if scene_t >= SCENE_DURATION_SEC:
                scene_t = 0.0
                scene_idx = (scene_idx + 1) % len(STORY_SCENES)
            state["scene_t"] = scene_t
            state["scene_idx"] = scene_idx
            state["global_t"] = float(state.get("global_t", 0.0)) + 1.0
        return state

    @app.callback(
        [
            Output("fig-reconstruction", "figure"),
            Output("fig-regime", "figure"),
            Output("fig-counterfactual", "figure"),
            Output("policy-breakdown", "children"),
            Output("scene-caption", "children"),
            Output("evidence-ledger", "children"),
        ],
        [
            Input("playback-store", "data"),
            Input("mode-selector", "value"),
            Input("explore-scenario", "value"),
            Input("explore-time", "value"),
        ],
    )
    def render_dashboard(
        state: Mapping[str, Any],
        mode: str,
        explore_scenario_id: str,
        explore_time: float,
    ) -> Tuple[go.Figure, go.Figure, go.Figure, html.Div, str, html.Div]:
        if mode == "story":
            idx = int(state.get("scene_idx", 0)) % len(STORY_SCENES)
            scene = STORY_SCENES[idx]
            scenario = SCENARIOS[scene["scenario_id"]]
            t = float(state.get("scene_t", 0.0))
            scene_label = scene["label"]
        else:
            scenario = SCENARIOS.get(explore_scenario_id, SCENARIOS[next(iter(SCENARIOS))])
            t = float(explore_time)
            scene_label = f"Explore | {scenario['title']}"

        signal = generate_signal(scenario, t=t)
        cfg = scenario_to_config(scenario)
        frame = analyze_signal(signal, config=cfg)
        counter = run_counterfactual(
            signal,
            policy={"alpha": scenario["alpha"], "cost_model": scenario["cost_model"]},
        )
        disruption_index = compute_disruption_index(counter)

        reconstruction = _build_reconstruction_figure(signal, n_values=tuple(cfg.n_values))
        regime_map = _build_regime_map(signal, scenario=scenario, frame=frame)
        counter_plot = _build_counterfactual_figure(counter, disruption_index)
        caption = _scene_caption(mode, scene_label, scenario, frame, counter, disruption_index)
        policy = html.Div(
            children=[
                html.Div(f"closure_ratio: {frame.closure_ratio:.3f}"),
                html.Div(f"edge_fraction: {counter.edge_fraction:.2%}"),
                html.Div(f"mixed_fraction: {counter.mixed_fraction:.2%}"),
                html.Div(f"smooth_fraction: {counter.smooth_fraction:.2%}"),
                html.Div(f"quality_gain: {counter.quality_gain:.6f}"),
                html.Div(f"smooth_penalty: {counter.smooth_penalty:.6f}"),
                html.Div(f"speed_gain: {counter.speed_gain:.2%}"),
            ]
        )
        ledger = _evidence_ledger(ARTIFACTS, ARTIFACT_ERROR)
        return reconstruction, regime_map, counter_plot, policy, caption, ledger

    return app


def main() -> None:
    app = create_app()
    app.run(debug=False, host="127.0.0.1", port=8050)


if __name__ == "__main__":
    main()
