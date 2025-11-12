"""
Core module per il calcolo del ventaglio di Gann.

Implementa tutte le funzioni matematiche fondamentali per:
- Average True Range (ATR) con metodi SMA e Wilder
- Rilevamento pivot points (percent-based e ATR-based)
- Calcolo Price Per Bar (ppb)
- Costruzione completa del ventaglio di Gann
"""

from dataclasses import dataclass
from typing import List, Literal, Optional, Tuple
import numpy as np
import pandas as pd


@dataclass
class FanLine:
    """
    Rappresenta una singola linea del ventaglio di Gann.
    
    Attributes
    ----------
    ratio : float
        Il ratio della linea (es. 1/8, 1/4, 1, 2, 4, 8)
    direction : str
        Direzione della linea: "up" o "down"
    start_idx : int
        Indice di partenza della linea
    end_idx : int
        Indice di fine della linea
    y0 : float
        Prezzo iniziale (al pivot)
    y1 : float
        Prezzo finale (dopo bars_forward)
    """
    ratio: float
    direction: Literal["up", "down"]
    start_idx: int
    end_idx: int
    y0: float
    y1: float


@dataclass
class FanResult:
    """
    Risultato completo del calcolo del ventaglio di Gann.
    
    Attributes
    ----------
    pivot_idx : int
        Indice del pivot utilizzato come origine
    pivot_price : float
        Prezzo del pivot
    ppb : float
        Price Per Bar calcolato
    lines : List[FanLine]
        Lista di tutte le linee del ventaglio
    """
    pivot_idx: int
    pivot_price: float
    ppb: float
    lines: List[FanLine]


def atr(
    df: pd.DataFrame,
    length: int = 14,
    method: Literal["sma", "wilder"] = "sma"
) -> pd.Series:
    """
    Calcola l'Average True Range (ATR).
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con colonne "High", "Low", "Close"
    length : int, default=14
        Periodo per il calcolo dell'ATR
    method : {"sma", "wilder"}, default="sma"
        Metodo di smoothing:
        - "sma": Simple Moving Average
        - "wilder": Wilder's smoothing (EMA-like)
    
    Returns
    -------
    pd.Series
        Serie con valori ATR
    
    Raises
    ------
    ValueError
        Se le colonne richieste non sono presenti o length < 1
    
    Notes
    -----
    True Range è definito come:
    TR_t = max(High_t - Low_t, |High_t - Close_{t-1}|, |Low_t - Close_{t-1}|)
    
    ATR con SMA:
    ATR_t = (1/n) * Σ(TR_i da t-n+1 a t)
    
    ATR con Wilder:
    ATR_t = ((ATR_{t-1}*(n-1)) + TR_t) / n
    """
    # Validazione input
    required_cols = ["High", "Low", "Close"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Colonne mancanti nel DataFrame: {missing}")
    
    if length < 1:
        raise ValueError(f"length deve essere >= 1, ricevuto: {length}")
    
    if len(df) < 2:
        raise ValueError(f"DataFrame troppo corto per calcolare ATR (minimo 2 righe)")
    
    # Calcolo True Range
    high = df["High"].values
    low = df["Low"].values
    close = df["Close"].values
    
    tr = np.zeros(len(df))
    tr[0] = high[0] - low[0]  # Prima barra: solo high-low
    
    for i in range(1, len(df)):
        hl = high[i] - low[i]
        hc = abs(high[i] - close[i-1])
        lc = abs(low[i] - close[i-1])
        tr[i] = max(hl, hc, lc)
    
    # Calcolo ATR
    atr_values = np.full(len(df), np.nan)
    
    if method == "sma":
        # Simple Moving Average
        for i in range(length - 1, len(df)):
            atr_values[i] = np.mean(tr[i-length+1:i+1])
    
    elif method == "wilder":
        # Wilder's smoothing (simile a EMA)
        # Prima ATR è la media semplice
        if len(df) >= length:
            atr_values[length-1] = np.mean(tr[:length])
            
            # Successivi con formula di Wilder
            for i in range(length, len(df)):
                atr_values[i] = ((atr_values[i-1] * (length - 1)) + tr[i]) / length
    
    else:
        raise ValueError(f"Metodo non supportato: {method}. Usa 'sma' o 'wilder'")
    
    return pd.Series(atr_values, index=df.index, name="ATR")


def pivots_percent(
    df: pd.DataFrame,
    threshold: float,
    price_col: str = "Close"
) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """
    Rileva pivot points usando metodo percentuale.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con dati di prezzo
    threshold : float
        Soglia percentuale per rilevare un pivot (es. 0.05 per 5%)
    price_col : str, default="Close"
        Colonna da usare per il prezzo
    
    Returns
    -------
    highs : List[Tuple[int, float]]
        Lista di (indice, prezzo) per pivot highs
    lows : List[Tuple[int, float]]
        Lista di (indice, prezzo) per pivot lows
    
    Raises
    ------
    ValueError
        Se threshold <= 0 o price_col non esiste
    
    Notes
    -----
    Logica:
    - Se (P_t - P_pivot) / P_pivot >= threshold → registra pivot low
    - Se (P_pivot - P_t) / P_pivot >= threshold → registra pivot high
    """
    if price_col not in df.columns:
        raise ValueError(f"Colonna '{price_col}' non trovata nel DataFrame")
    
    if threshold <= 0:
        raise ValueError(f"threshold deve essere > 0, ricevuto: {threshold}")
    
    if len(df) < 2:
        return [], []
    
    prices = df[price_col].values
    highs = []
    lows = []
    
    # Stato iniziale
    direction = None  # "up" o "down"
    pivot_idx = 0
    pivot_price = prices[0]
    
    for i in range(1, len(df)):
        current = prices[i]
        
        if direction is None:
            # Determina direzione iniziale
            if current > pivot_price:
                direction = "up"
            elif current < pivot_price:
                direction = "down"
            pivot_price = current
            pivot_idx = i
            
        elif direction == "up":
            # In trend rialzista, cerchiamo un nuovo high o un reversal
            if current > pivot_price:
                # Nuovo high
                pivot_price = current
                pivot_idx = i
            else:
                # Controlla se è un reversal
                pct_change = (pivot_price - current) / pivot_price
                if pct_change >= threshold:
                    # Registra pivot high e inverti
                    highs.append((pivot_idx, pivot_price))
                    direction = "down"
                    pivot_price = current
                    pivot_idx = i
        
        else:  # direction == "down"
            # In trend ribassista, cerchiamo un nuovo low o un reversal
            if current < pivot_price:
                # Nuovo low
                pivot_price = current
                pivot_idx = i
            else:
                # Controlla se è un reversal
                pct_change = (current - pivot_price) / pivot_price
                if pct_change >= threshold:
                    # Registra pivot low e inverti
                    lows.append((pivot_idx, pivot_price))
                    direction = "up"
                    pivot_price = current
                    pivot_idx = i
    
    return highs, lows


def pivots_atr(
    df: pd.DataFrame,
    atr_len: int = 14,
    atr_mult: float = 1.0,
    method: Literal["sma", "wilder"] = "sma",
    price_col: str = "Close"
) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """
    Rileva pivot points usando ATR come soglia.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con colonne "High", "Low", "Close"
    atr_len : int, default=14
        Periodo per il calcolo dell'ATR
    atr_mult : float, default=1.0
        Moltiplicatore dell'ATR per la soglia
    method : {"sma", "wilder"}, default="sma"
        Metodo per il calcolo dell'ATR
    price_col : str, default="Close"
        Colonna da usare per il prezzo
    
    Returns
    -------
    highs : List[Tuple[int, float]]
        Lista di (indice, prezzo) per pivot highs
    lows : List[Tuple[int, float]]
        Lista di (indice, prezzo) per pivot lows
    
    Raises
    ------
    ValueError
        Se parametri non validi o ATR contiene NaN
    
    Notes
    -----
    Logica:
    - Se P_t - P_pivot >= ATR_t * k → registra low
    - Se P_pivot - P_t >= ATR_t * k → registra high
    """
    if price_col not in df.columns:
        raise ValueError(f"Colonna '{price_col}' non trovata nel DataFrame")
    
    if atr_mult <= 0:
        raise ValueError(f"atr_mult deve essere > 0, ricevuto: {atr_mult}")
    
    # Calcola ATR
    atr_series = atr(df, length=atr_len, method=method)
    
    # Verifica che ATR sia calcolabile
    if atr_series.isna().all():
        raise ValueError(
            f"ATR è completamente NaN. Aumentare la lunghezza del DataFrame "
            f"o ridurre atr_len (attuale: {atr_len})"
        )
    
    prices = df[price_col].values
    atr_vals = atr_series.values
    
    highs = []
    lows = []
    
    # Trova primo indice con ATR valido
    start_idx = np.where(~np.isnan(atr_vals))[0]
    if len(start_idx) == 0:
        return [], []
    start_idx = start_idx[0]
    
    # Stato iniziale
    direction = None
    pivot_idx = start_idx
    pivot_price = prices[start_idx]
    
    for i in range(start_idx + 1, len(df)):
        if np.isnan(atr_vals[i]):
            continue
            
        current = prices[i]
        threshold = atr_vals[i] * atr_mult
        
        if direction is None:
            # Determina direzione iniziale
            if current > pivot_price:
                direction = "up"
            elif current < pivot_price:
                direction = "down"
            pivot_price = current
            pivot_idx = i
            
        elif direction == "up":
            # In trend rialzista
            if current > pivot_price:
                # Nuovo high
                pivot_price = current
                pivot_idx = i
            else:
                # Controlla reversal
                if (pivot_price - current) >= threshold:
                    # Registra pivot high e inverti
                    highs.append((pivot_idx, pivot_price))
                    direction = "down"
                    pivot_price = current
                    pivot_idx = i
        
        else:  # direction == "down"
            # In trend ribassista
            if current < pivot_price:
                # Nuovo low
                pivot_price = current
                pivot_idx = i
            else:
                # Controlla reversal
                if (current - pivot_price) >= threshold:
                    # Registra pivot low e inverti
                    lows.append((pivot_idx, pivot_price))
                    direction = "up"
                    pivot_price = current
                    pivot_idx = i
    
    return highs, lows


def compute_ppb(
    df: pd.DataFrame,
    mode: Literal["ATR", "Fixed"],
    atr_len: int = 14,
    atr_method: Literal["sma", "wilder"] = "sma",
    atr_divisor: float = 1.0,
    fixed_ppb: float = 1.0,
    pivot_idx: int = 0
) -> float:
    """
    Calcola il Price Per Bar (ppb).
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con dati di prezzo
    mode : {"ATR", "Fixed"}
        Modalità di calcolo:
        - "ATR": ppb = ATR_{pivot} / atr_divisor
        - "Fixed": ppb = fixed_ppb
    atr_len : int, default=14
        Periodo ATR (usato solo in modalità ATR)
    atr_method : {"sma", "wilder"}, default="sma"
        Metodo ATR (usato solo in modalità ATR)
    atr_divisor : float, default=1.0
        Divisore per ATR (usato solo in modalità ATR)
    fixed_ppb : float, default=1.0
        Valore fisso ppb (usato solo in modalità Fixed)
    pivot_idx : int, default=0
        Indice del pivot (usato solo in modalità ATR)
    
    Returns
    -------
    float
        Valore di ppb calcolato
    
    Raises
    ------
    ValueError
        Se parametri non validi o ATR non disponibile al pivot
    """
    if mode == "Fixed":
        if fixed_ppb <= 0:
            raise ValueError(f"fixed_ppb deve essere > 0, ricevuto: {fixed_ppb}")
        return fixed_ppb
    
    elif mode == "ATR":
        if atr_divisor <= 0:
            raise ValueError(f"atr_divisor deve essere > 0, ricevuto: {atr_divisor}")
        
        if pivot_idx < 0 or pivot_idx >= len(df):
            raise ValueError(
                f"pivot_idx fuori range: {pivot_idx} (DataFrame ha {len(df)} righe)"
            )
        
        # Calcola ATR
        atr_series = atr(df, length=atr_len, method=atr_method)
        atr_at_pivot = atr_series.iloc[pivot_idx]
        
        if np.isnan(atr_at_pivot):
            raise ValueError(
                f"ATR non disponibile all'indice {pivot_idx}. "
                f"ATR richiede almeno {atr_len} barre di dati precedenti."
            )
        
        ppb = atr_at_pivot / atr_divisor
        return ppb
    
    else:
        raise ValueError(f"Modalità ppb non supportata: {mode}. Usa 'ATR' o 'Fixed'")


def gann_fan(
    df: pd.DataFrame,
    pivot_source: Literal["last_low", "last_high", "custom"] = "last_low",
    pivot_mode: Literal["atr", "percent"] = "atr",
    threshold: float = 0.05,
    atr_len: int = 14,
    atr_mult: float = 1.0,
    atr_method: Literal["sma", "wilder"] = "sma",
    ppb_mode: Literal["ATR", "Fixed"] = "ATR",
    atr_divisor: float = 1.0,
    fixed_ppb: float = 1.0,
    ratios: Optional[List[float]] = None,
    bars_forward: int = 100,
    custom_pivot: Optional[Tuple[int, float]] = None
) -> FanResult:
    """
    Calcola il ventaglio di Gann completo.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con colonne "Date", "Open", "High", "Low", "Close"
    pivot_source : {"last_low", "last_high", "custom"}, default="last_low"
        Sorgente del pivot da usare
    pivot_mode : {"atr", "percent"}, default="atr"
        Modalità di rilevamento pivot (ignorato se pivot_source="custom")
    threshold : float, default=0.05
        Soglia per pivot_mode="percent"
    atr_len : int, default=14
        Periodo ATR
    atr_mult : float, default=1.0
        Moltiplicatore ATR per pivot_mode="atr"
    atr_method : {"sma", "wilder"}, default="sma"
        Metodo calcolo ATR
    ppb_mode : {"ATR", "Fixed"}, default="ATR"
        Modalità calcolo Price Per Bar
    atr_divisor : float, default=1.0
        Divisore ATR per ppb_mode="ATR"
    fixed_ppb : float, default=1.0
        Valore fisso ppb per ppb_mode="Fixed"
    ratios : Optional[List[float]], default=None
        Lista di ratios per il ventaglio. Default: [1/8, 1/4, 1/3, 1/2, 1, 2, 3, 4, 8]
    bars_forward : int, default=100
        Numero di barre di proiezione del ventaglio
    custom_pivot : Optional[Tuple[int, float]], default=None
        Pivot custom come (indice, prezzo)
    
    Returns
    -------
    FanResult
        Risultato completo con pivot e linee del ventaglio
    
    Raises
    ------
    ValueError
        Se parametri non validi, colonne mancanti o pivot non trovato
    
    Notes
    -----
    Equazione delle linee:
    P(t) = P_0 ± r * ppb * (t - t_0)
    
    dove:
    - P_0: prezzo del pivot
    - r: ratio della linea
    - ppb: price per bar
    - t_0: indice del pivot
    """
    # Validazione colonne
    required_cols = ["High", "Low", "Close"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Colonne mancanti nel DataFrame: {missing}")
    
    if len(df) < 2:
        raise ValueError("DataFrame troppo corto (minimo 2 righe richieste)")
    
    # Validazione parametri
    if bars_forward < 1:
        raise ValueError(f"bars_forward deve essere >= 1, ricevuto: {bars_forward}")
    
    # Ratios di default
    if ratios is None:
        ratios = [1/8, 1/4, 1/3, 1/2, 1, 2, 3, 4, 8]
    
    # Rimuovi duplicati e ordina
    ratios = sorted(list(set(ratios)))
    
    if len(ratios) == 0:
        raise ValueError("Lista ratios vuota")
    
    # Determina il pivot
    pivot_idx: int
    pivot_price: float
    
    if pivot_source == "custom":
        if custom_pivot is None:
            raise ValueError("pivot_source='custom' richiede custom_pivot=(idx, price)")
        pivot_idx, pivot_price = custom_pivot
        if pivot_idx < 0 or pivot_idx >= len(df):
            raise ValueError(
                f"custom_pivot idx fuori range: {pivot_idx} (DataFrame ha {len(df)} righe)"
            )
    
    else:
        # Rileva pivot automaticamente
        if pivot_mode == "percent":
            highs, lows = pivots_percent(df, threshold=threshold)
        elif pivot_mode == "atr":
            highs, lows = pivots_atr(
                df, atr_len=atr_len, atr_mult=atr_mult, method=atr_method
            )
        else:
            raise ValueError(f"pivot_mode non supportato: {pivot_mode}")
        
        # Seleziona pivot appropriato
        if pivot_source == "last_low":
            if len(lows) == 0:
                raise ValueError(
                    "Nessun pivot low trovato. Prova a ridurre threshold/atr_mult "
                    "o aumentare la lunghezza del DataFrame"
                )
            pivot_idx, pivot_price = lows[-1]
        
        elif pivot_source == "last_high":
            if len(highs) == 0:
                raise ValueError(
                    "Nessun pivot high trovato. Prova a ridurre threshold/atr_mult "
                    "o aumentare la lunghezza del DataFrame"
                )
            pivot_idx, pivot_price = highs[-1]
        
        else:
            raise ValueError(
                f"pivot_source non supportato: {pivot_source}. "
                f"Usa 'last_low', 'last_high' o 'custom'"
            )
    
    # Calcola ppb
    ppb = compute_ppb(
        df=df,
        mode=ppb_mode,
        atr_len=atr_len,
        atr_method=atr_method,
        atr_divisor=atr_divisor,
        fixed_ppb=fixed_ppb,
        pivot_idx=pivot_idx
    )
    
    # Costruisci le linee del ventaglio
    lines: List[FanLine] = []
    
    # Determina direzione del ventaglio basata sul tipo di pivot
    if pivot_source == "last_low" or (pivot_source == "custom" and custom_pivot):
        # Da un low, le linee vanno verso l'alto
        base_direction = "up"
    else:
        # Da un high, le linee vanno verso il basso
        base_direction = "down"
    
    # Calcola end_idx
    end_idx = min(pivot_idx + bars_forward, len(df) - 1)
    bars_projected = end_idx - pivot_idx
    
    # Crea linee per ogni ratio
    for ratio in ratios:
        if ratio <= 0:
            continue  # Salta ratios non validi
        
        # Linea nella direzione base
        if base_direction == "up":
            y1 = pivot_price + ratio * ppb * bars_projected
            lines.append(FanLine(
                ratio=ratio,
                direction="up",
                start_idx=pivot_idx,
                end_idx=end_idx,
                y0=pivot_price,
                y1=y1
            ))
        else:
            y1 = pivot_price - ratio * ppb * bars_projected
            lines.append(FanLine(
                ratio=ratio,
                direction="down",
                start_idx=pivot_idx,
                end_idx=end_idx,
                y0=pivot_price,
                y1=y1
            ))
    
    return FanResult(
        pivot_idx=pivot_idx,
        pivot_price=pivot_price,
        ppb=ppb,
        lines=lines
    )
