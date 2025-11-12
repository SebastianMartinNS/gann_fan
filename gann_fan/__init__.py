"""
Gann Fan - Modulo Python per calcolo e visualizzazione del ventaglio di Gann.

Questo modulo fornisce strumenti per:
- Calcolare l'Average True Range (ATR)
- Rilevare pivot points con metodi percentuali o basati su ATR
- Costruire ventagli di Gann con ratios configurabili
- Visualizzare i risultati
- Acquisire dati da exchange pubblici (Coinbase)
"""

__version__ = "1.0.0"
__author__ = "Gann Fan Project"

from gann_fan.core import (
    atr,
    pivots_percent,
    pivots_atr,
    compute_ppb,
    gann_fan,
    FanLine,
    FanResult,
)

from gann_fan.data import (
    get_coinbase_candles,
    get_available_coinbase_products,
    validate_dataframe,
)

__all__ = [
    "atr",
    "pivots_percent",
    "pivots_atr",
    "compute_ppb",
    "gann_fan",
    "FanLine",
    "FanResult",
    "get_coinbase_candles",
    "get_available_coinbase_products",
    "validate_dataframe",
]
