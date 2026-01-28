from __future__ import annotations

import argparse
import json
import sys

from .market_data import MarketSentiment, build_market_sentiment
from .simulation import EventFactors, SimulationConfig, SocietyState, simulate, summarize


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Simule des indicateurs socio-économiques après des événements (modèle heuristique)."
        )
    )
    parser.add_argument("--years", type=int, default=5, help="Horizon de simulation en années")
    parser.add_argument("--steps-per-year", type=int, default=4, help="Nombre de pas par an")
    parser.add_argument("--seed", type=int, default=None, help="Graine aléatoire")

    parser.add_argument("--gdp", type=float, default=0.6, help="Indice PIB initial (0-1)")
    parser.add_argument(
        "--unemployment", type=float, default=0.3, help="Taux chômage initial (0-1)"
    )
    parser.add_argument(
        "--inequality", type=float, default=0.4, help="Indice d'inégalités initial (0-1)"
    )
    parser.add_argument("--health", type=float, default=0.7, help="Indice santé (0-1)")
    parser.add_argument("--cohesion", type=float, default=0.6, help="Cohésion sociale (0-1)")
    parser.add_argument(
        "--stability", type=float, default=0.65, help="Stabilité politique (0-1)"
    )
    parser.add_argument("--trust", type=float, default=0.6, help="Confiance institutionnelle (0-1)")

    parser.add_argument(
        "--epidemic", type=float, default=0.2, help="Sévérité épidémie (0-1)"
    )
    parser.add_argument(
        "--social", type=float, default=0.3, help="Disruption sociale (0-1)"
    )
    parser.add_argument(
        "--political", type=float, default=0.3, help="Instabilité politique (0-1)"
    )
    parser.add_argument(
        "--conflict", type=float, default=0.1, help="Conflit externe (0-1)"
    )
    parser.add_argument(
        "--tech", type=float, default=0.4, help="Changement technologique (0-1)"
    )
    parser.add_argument(
        "--fear-factor",
        type=float,
        default=0.3,
        help="Facteur de peur (0-1) influençant la propension à investir",
    )
    parser.add_argument(
        "--fetch-market-data",
        action="store_true",
        help="Récupère le VIX et le Doomsday Clock pour estimer la panique des marchés",
    )

    parser.add_argument(
        "--output",
        choices=("summary", "timeline"),
        default="summary",
        help="Type de sortie",
    )
    return parser


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    state = SocietyState(
        gdp_index=args.gdp,
        unemployment_rate=args.unemployment,
        inequality_index=args.inequality,
        health_index=args.health,
        social_cohesion=args.cohesion,
        political_stability=args.stability,
        institutional_trust=args.trust,
    )
    market_sentiment: MarketSentiment | None = None
    effective_fear = args.fear_factor
    if args.fetch_market_data:
        try:
            market_sentiment = build_market_sentiment()
            effective_fear = (effective_fear + market_sentiment.market_panic_index) / 2.0
        except Exception as exc:  # noqa: BLE001
            print(
                f"Impossible de récupérer les données de marché: {exc}",
                file=sys.stderr,
            )
    factors = EventFactors(
        time_horizon_years=args.years,
        epidemic_severity=args.epidemic,
        social_disruption=args.social,
        political_instability=args.political,
        external_conflict=args.conflict,
        technological_change=args.tech,
        fear_factor=effective_fear,
    )
    config = SimulationConfig(steps_per_year=args.steps_per_year, random_seed=args.seed)

    result = simulate(state=state, factors=factors, config=config)

    if args.output == "timeline":
        payload = [snapshot.__dict__ for snapshot in result.snapshots]
    else:
        payload = summarize(result)
    if market_sentiment:
        payload = {
            "market_data": {
                "vix": market_sentiment.vix,
                "doomsday_seconds_to_midnight": market_sentiment.doomsday_seconds_to_midnight,
                "market_panic_index": market_sentiment.market_panic_index,
            },
            "simulation": payload,
        }

    print(json.dumps(payload, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
