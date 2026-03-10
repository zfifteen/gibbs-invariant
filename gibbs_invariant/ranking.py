"""Candidate software ranking for integration readiness."""

from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional


WEIGHTS = {
    "fft_dependency": 0.35,
    "spectral_processing_intensity": 0.25,
    "discontinuity_frequency": 0.20,
    "artifact_sensitivity": 0.20,
}


@dataclass
class CandidateScore:
    name: str
    repo_url: str
    fft_dependency: float
    spectral_processing_intensity: float
    discontinuity_frequency: float
    artifact_sensitivity: float

    @property
    def total(self) -> float:
        return (
            self.fft_dependency * WEIGHTS["fft_dependency"]
            + self.spectral_processing_intensity * WEIGHTS["spectral_processing_intensity"]
            + self.discontinuity_frequency * WEIGHTS["discontinuity_frequency"]
            + self.artifact_sensitivity * WEIGHTS["artifact_sensitivity"]
        )


def _keyword_score(text: str, keywords: List[str], base: float = 0.10) -> float:
    lower = text.lower()
    hits = sum(1 for token in keywords if token in lower)
    score = base + min(0.90, 0.18 * hits)
    return float(max(0.0, min(1.0, score)))


def _component_scores(description: str) -> Dict[str, float]:
    return {
        "fft_dependency": _keyword_score(
            description,
            ["fft", "dct", "mdct", "k-space", "spectral", "transform", "harmonic", "codec"],
        ),
        "spectral_processing_intensity": _keyword_score(
            description,
            ["reconstruction", "compression", "encoder", "solver", "spectral", "signal"],
        ),
        "discontinuity_frequency": _keyword_score(
            description,
            ["edge", "transient", "shock", "boundary", "discontinu", "ringing", "artifact"],
        ),
        "artifact_sensitivity": _keyword_score(
            description,
            ["quality", "artifact", "ringing", "pre-echo", "diagnostic", "perceptual", "denoising"],
        ),
    }


def _parse_candidates(candidate_file: Path) -> List[Dict[str, str]]:
    lines = candidate_file.read_text(encoding="utf-8").splitlines()
    items: List[Dict[str, str]] = []

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        m = re.match(r"^- \*\*(.+?)\*\*", line)
        if not m:
            i += 1
            continue

        name = m.group(1).strip()
        repo_url = ""
        why = ""
        j = i + 1
        while j < len(lines) and not lines[j].strip().startswith("- **"):
            current = lines[j].strip()
            if current.startswith("- Repo:"):
                repo_url = current.replace("- Repo:", "").strip()
                repo_url = re.sub(r"\[\^[0-9]+\]", "", repo_url).strip()
            elif current.startswith("- Why good:"):
                why = current.replace("- Why good:", "").strip()
            j += 1

        items.append({"name": name, "repo_url": repo_url, "description": why})
        i = j

    return items


def rank_candidates(
    candidate_file: str = "docs/industry/github_candidate_software_list.md",
    output_dir: str = "results",
    gate_report_path: str = "results/gates_report.json",
    constrained_report_path: str = "results/constrained_metrics.json",
) -> Dict[str, object]:
    candidate_path = Path(candidate_file)
    out_dir = Path(output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    phase2b_pass = False
    phase3_pass = False

    gate_path = Path(gate_report_path)
    if gate_path.exists():
        gate = json.loads(gate_path.read_text(encoding="utf-8"))
        phase2b_pass = bool(gate.get("all_pass", False))

    constrained_path = Path(constrained_report_path)
    if constrained_path.exists():
        constrained = json.loads(constrained_path.read_text(encoding="utf-8"))
        phase3_pass = bool(constrained.get("pass", False))

    parsed = _parse_candidates(candidate_path)
    scored: List[CandidateScore] = []
    for item in parsed:
        components = _component_scores(item["description"])
        scored.append(
            CandidateScore(
                name=item["name"],
                repo_url=item["repo_url"],
                fft_dependency=components["fft_dependency"],
                spectral_processing_intensity=components["spectral_processing_intensity"],
                discontinuity_frequency=components["discontinuity_frequency"],
                artifact_sensitivity=components["artifact_sensitivity"],
            )
        )

    scored.sort(key=lambda row: row.total, reverse=True)
    csv_path = out_dir / "candidate_rankings.csv"
    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "rank",
                "name",
                "repo_url",
                "total",
                "fft_dependency",
                "spectral_processing_intensity",
                "discontinuity_frequency",
                "artifact_sensitivity",
            ],
        )
        writer.writeheader()
        for idx, row in enumerate(scored, start=1):
            writer.writerow(
                {
                    "rank": idx,
                    "name": row.name,
                    "repo_url": row.repo_url,
                    "total": f"{row.total:.4f}",
                    "fft_dependency": f"{row.fft_dependency:.4f}",
                    "spectral_processing_intensity": f"{row.spectral_processing_intensity:.4f}",
                    "discontinuity_frequency": f"{row.discontinuity_frequency:.4f}",
                    "artifact_sensitivity": f"{row.artifact_sensitivity:.4f}",
                }
            )

    shortlist = [
        {"name": row.name, "repo_url": row.repo_url, "score": round(row.total, 4)}
        for row in scored[:3]
    ]

    selected_target: Optional[Dict[str, object]] = shortlist[0] if (phase2b_pass and phase3_pass and shortlist) else None
    result = {
        "weights": WEIGHTS,
        "phase2b_pass": phase2b_pass,
        "phase3_pass": phase3_pass,
        "shortlist": shortlist,
        "selected_target": selected_target,
        "selection_unblocked": bool(phase2b_pass and phase3_pass),
        "output_csv": str(csv_path),
    }

    json_path = out_dir / "candidate_ranking_report.json"
    json_path.write_text(json.dumps(result, indent=2), encoding="utf-8")

    markdown_path = Path("docs/industry/candidate_ranking_v1.md")
    markdown_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# Candidate Ranking (v1)",
        "",
        f"- Phase 2b pass: `{phase2b_pass}`",
        f"- Phase 3 pass: `{phase3_pass}`",
        f"- Selection unblocked: `{result['selection_unblocked']}`",
        "",
        "| Rank | Candidate | Score | Repo |",
        "|---|---|---:|---|",
    ]
    for idx, row in enumerate(shortlist, start=1):
        lines.append(f"| {idx} | {row['name']} | {row['score']:.4f} | {row['repo_url']} |")

    if selected_target:
        lines.extend(
            [
                "",
                f"Selected PoC target: **{selected_target['name']}** ({selected_target['repo_url']})",
            ]
        )
    else:
        lines.extend(
            [
                "",
                "Selected PoC target: **blocked** until Phase 2b and Phase 3 pass.",
            ]
        )

    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    return result
