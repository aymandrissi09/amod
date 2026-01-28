from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Dict, List


@dataclass(frozen=True)
class SocietyState:
    """Baseline state of a society on normalized scales."""

    gdp_index: float
    unemployment_rate: float
    inequality_index: float
    health_index: float
    social_cohesion: float
    political_stability: float
    institutional_trust: float


@dataclass(frozen=True)
class EventFactors:
    """Exogenous shocks to the society for the simulation horizon."""

    time_horizon_years: int
    epidemic_severity: float
    social_disruption: float
    political_instability: float
    external_conflict: float
    technological_change: float
    fear_factor: float


@dataclass(frozen=True)
class SimulationConfig:
    """Configuration details for the simulation."""

    steps_per_year: int = 4
    random_seed: int | None = None
    noise_scale: float = 0.02


@dataclass(frozen=True)
class SimulationSnapshot:
    step: int
    gdp_index: float
    unemployment_rate: float
    inequality_index: float
    health_index: float
    social_cohesion: float
    political_stability: float
    institutional_trust: float


@dataclass(frozen=True)
class SimulationResult:
    snapshots: List[SimulationSnapshot]

    def latest(self) -> SimulationSnapshot:
        return self.snapshots[-1]


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def simulate(
    state: SocietyState,
    factors: EventFactors,
    config: SimulationConfig | None = None,
) -> SimulationResult:
    """Simulate macro-socioeconomic trajectories based on inputs.

    This is a heuristic model intended for scenario exploration, not prediction.
    """

    config = config or SimulationConfig()
    rng = random.Random(config.random_seed)

    steps = max(1, factors.time_horizon_years * config.steps_per_year)
    snapshots: List[SimulationSnapshot] = []

    gdp = state.gdp_index
    unemployment = state.unemployment_rate
    inequality = state.inequality_index
    health = state.health_index
    cohesion = state.social_cohesion
    stability = state.political_stability
    trust = state.institutional_trust

    for step in range(steps):
        shock = (
            0.35 * factors.epidemic_severity
            + 0.25 * factors.social_disruption
            + 0.3 * factors.political_instability
            + 0.2 * factors.external_conflict
        )
        tech = factors.technological_change
        fear = factors.fear_factor
        noise = rng.uniform(-config.noise_scale, config.noise_scale)

        investment_propensity = 1.0 - fear
        gdp = _clamp(gdp + 0.12 * tech * investment_propensity - 0.18 * shock + noise)
        unemployment = _clamp(unemployment + 0.15 * shock - 0.08 * tech + 0.06 * fear + noise)
        inequality = _clamp(inequality + 0.1 * shock + 0.05 * unemployment - 0.04 * cohesion)
        health = _clamp(health - 0.22 * factors.epidemic_severity + 0.08 * tech + noise)
        cohesion = _clamp(cohesion - 0.18 * shock - 0.05 * fear + 0.06 * stability + noise)
        stability = _clamp(stability - 0.2 * factors.political_instability - 0.05 * fear + 0.07 * cohesion)
        trust = _clamp(trust - 0.15 * shock - 0.06 * fear + 0.05 * cohesion + noise)

        snapshots.append(
            SimulationSnapshot(
                step=step + 1,
                gdp_index=gdp,
                unemployment_rate=unemployment,
                inequality_index=inequality,
                health_index=health,
                social_cohesion=cohesion,
                political_stability=stability,
                institutional_trust=trust,
            )
        )

    return SimulationResult(snapshots=snapshots)


def summarize(result: SimulationResult) -> Dict[str, float]:
    latest = result.latest()
    return {
        "gdp_index": latest.gdp_index,
        "unemployment_rate": latest.unemployment_rate,
        "inequality_index": latest.inequality_index,
        "health_index": latest.health_index,
        "social_cohesion": latest.social_cohesion,
        "political_stability": latest.political_stability,
        "institutional_trust": latest.institutional_trust,
    }
