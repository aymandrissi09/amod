from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Optional
from urllib.request import urlopen


@dataclass(frozen=True)
class MarketSentiment:
    vix: float
    doomsday_seconds_to_midnight: int
    market_panic_index: float


def _clamp(value: float, minimum: float = 0.0, maximum: float = 1.0) -> float:
    return max(minimum, min(maximum, value))


def _fetch_vix() -> float:
    url = "https://stooq.com/q/l/?s=%5Evix&f=sd2t2ohlcv&h&e=csv"
    with urlopen(url, timeout=10) as response:
        payload = response.read().decode("utf-8").strip().splitlines()
    if len(payload) < 2:
        raise ValueError("VIX payload missing data rows.")
    columns = payload[1].split(",")
    if len(columns) < 7:
        raise ValueError("VIX payload missing columns.")
    return float(columns[6])


def _fetch_doomsday_seconds() -> int:
    url = "https://thebulletin.org/doomsday-clock/"
    with urlopen(url, timeout=10) as response:
        html = response.read().decode("utf-8")
    match = re.search(r"(\d+)\s+seconds\s+to\s+midnight", html, re.IGNORECASE)
    if match:
        return int(match.group(1))
    match = re.search(r"(\d+)\s+minutes\s+to\s+midnight", html, re.IGNORECASE)
    if match:
        minutes = int(match.group(1))
        return minutes * 60
    raise ValueError("Could not locate Doomsday Clock time.")


def build_market_sentiment() -> MarketSentiment:
    vix = _fetch_vix()
    doomsday_seconds = _fetch_doomsday_seconds()

    vix_component = _clamp((vix - 10.0) / 50.0)
    doomsday_component = _clamp((120.0 - float(doomsday_seconds)) / 120.0)
    market_panic = _clamp(0.6 * vix_component + 0.4 * doomsday_component)

    return MarketSentiment(
        vix=vix,
        doomsday_seconds_to_midnight=doomsday_seconds,
        market_panic_index=market_panic,
    )


def market_sentiment_as_json(sentiment: MarketSentiment) -> str:
    return json.dumps(
        {
            "vix": sentiment.vix,
            "doomsday_seconds_to_midnight": sentiment.doomsday_seconds_to_midnight,
            "market_panic_index": sentiment.market_panic_index,
        },
        ensure_ascii=False,
    )
