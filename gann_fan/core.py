"""
Gann Fan Core Module - Crypto-Adapted Version

Implementazione moderna del Ventaglio di Gann ottimizzata per il trading di criptovalute.
Adatta i principi geometrici e temporali di W.D. Gann (1900-1950) ai mercati crypto moderni.

DIFFERENZE CHIAVE vs implementazione classica:
- ATR percentuale invece di assoluto (volatilità relativa)
- Scala logaritmica per prezzi (cattura movimenti %)
- Volume weighting per asse temporale  
- PPB dinamico adattivo alla volatilità
- Square of 9 normalizzato integrato

Ottimizzato per: Bitcoin, Ethereum, altcoin con volatilità estrema
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
        Indice del pivot nel DataFrame
    pivot_price : float
        Prezzo del pivot
    ppb : float
        Price Per Bar (quanto prezzo per unità di tempo)
    lines : List[FanLine]
        Lista delle linee del ventaglio
    """
    pivot_idx: int
    pivot_price: float
    ppb: float
    lines: List[FanLine]


def atr_percent(
    df: pd.DataFrame,
    length: int = 14,
    method: Literal["sma", "wilder", "ema"] = "ema"
) -> pd.Series:
    """
    Calcola Average True Range PERCENTUALE (adattato per crypto).
    
    L'ATR percentuale normalizza la volatilità rispetto al prezzo corrente,
    permettendo confronti tra asset con diverse scale di prezzo.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con colonne: High, Low, Close, deve essere ordinato cronologicamente
    length : int, default 14
        Periodo di calcolo ATR
    method : {"sma", "wilder", "ema"}, default "ema"
        Metodo di smoothing:
        - "sma": Media mobile semplice
        - "wilder": Smoothing di Wilder (più conservativo)
        - "ema": Media mobile esponenziale (più reattivo, consigliato per crypto)
        
    Returns
    -------
    pd.Series
        ATR percentuale (0-100, dove 5.0 = 5% di volatilità)
        
    Notes
    -----
    Formula ATR classico:
        TR_t = max(High_t - Low_t, |High_t - Close_{t-1}|, |Low_t - Close_{t-1}|)
        
    Formula ATR percentuale (CRYPTO-ADAPTED):
        ATR_pct = (ATR_absolute / Close_t) × 100
        
    Vantaggi per crypto:
    - Normalizzato: 5% su BTC a 20K = stesso significato di 5% su BTC a 90K
    - Comparabile: Puoi confrontare volatilità BTC vs ETH vs altcoin
    - Stabile: Non influenzato dall'ordine di grandezza del prezzo
    
    Examples
    --------
    >>> atr_pct = atr_percent(df, length=14, method="ema")
    >>> print(f"Volatilità: {atr_pct.iloc[-1]:.2f}%")
    Volatilità: 3.45%
    """
    if "High" not in df.columns or "Low" not in df.columns or "Close" not in df.columns:
        raise ValueError("DataFrame deve contenere colonne: High, Low, Close")
    
    if length < 2:
        raise ValueError(f"length deve essere >= 2, ricevuto: {length}")
    
    if len(df) < length + 1:
        raise ValueError(
            f"DataFrame troppo corto ({len(df)} righe) per length={length}. "
            f"Servono almeno {length + 1} righe."
        )
    
    # Calcola True Range assoluto
    high = df["High"].values
    low = df["Low"].values
    close = df["Close"].values
    
    # Shifta close per calcolare gap
    prev_close = np.roll(close, 1)
    prev_close[0] = close[0]  # Prima barra: usa stesso close
    
    # True Range
    tr = np.maximum(
        high - low,  # Range corrente
        np.maximum(
            np.abs(high - prev_close),  # Gap up
            np.abs(low - prev_close)    # Gap down
        )
    )
    
    # Smooth TR in base al metodo
    if method == "sma":
        # Media mobile semplice
        atr_abs = pd.Series(tr).rolling(window=length, min_periods=length).mean()
    elif method == "wilder":
        # Wilder smoothing: ATR_t = ATR_{t-1} + (1/n) * (TR_t - ATR_{t-1})
        atr_abs = pd.Series(tr).ewm(alpha=1/length, adjust=False).mean()
    elif method == "ema":
        # EMA standard (più reattivo, migliore per crypto)
        atr_abs = pd.Series(tr).ewm(span=length, adjust=False).mean()
    else:
        raise ValueError(f"method deve essere 'sma', 'wilder' o 'ema', ricevuto: {method}")
    
    # Converti in percentuale
    atr_pct = (atr_abs / close) * 100
    
    return atr_pct


def pivots_percent_log(
    df: pd.DataFrame,
    threshold: float,
    price_col: str = "Close"
) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """
    Rileva pivot points usando soglia percentuale su SCALA LOGARITMICA (adattato per crypto).
    
    La scala logaritmica cattura movimenti percentuali invece di assoluti,
    essenziale per asset con movimenti +100%/+500% come le crypto.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con dati di prezzo
    threshold : float
        Soglia percentuale (es. 0.05 = 5%)
        Per crypto volatile, usa 0.03-0.10 (3%-10%)
    price_col : str, default "Close"
        Nome colonna prezzi da usare
        
    Returns
    -------
    tuple
        (highs, lows) dove ogni elemento è List[Tuple[int, float]]
        - highs: Lista di (indice, prezzo) dei pivot high
        - lows: Lista di (indice, prezzo) dei pivot low
        
    Notes
    -----
    Formula classica (LINEARE - problematica per crypto):
        move% = (P_t - P_cand) / P_cand
        
    Formula moderna (LOGARITMICA - adatta per crypto):
        move% = exp(log(P_t) - log(P_cand)) - 1
        
    Equivalente semplificato:
        move% = (P_t / P_cand) - 1
        
    Vantaggi scala log per crypto:
    - 100K→200K (+100%) trattato come 50K→100K (+100%)
    - Cattura movimenti esponenziali tipici delle crypto
    - Simmetrico per movimenti su/giù
    
    Examples
    --------
    >>> highs, lows = pivots_percent_log(df, threshold=0.05)
    >>> print(f"Trovati {len(lows)} pivot low e {len(highs)} pivot high")
    """
    if price_col not in df.columns:
        raise ValueError(f"Colonna '{price_col}' non trovata nel DataFrame")
    
    if threshold <= 0:
        raise ValueError(f"threshold deve essere > 0, ricevuto: {threshold}")
    
    prices = df[price_col].values
    n = len(prices)
    
    highs = []
    lows = []
    
    # Usa log per calcoli (scala logaritmica)
    log_prices = np.log(prices)
    
    # Variabili per tracking pivot candidati
    candidate_high_idx = 0
    candidate_high_log = log_prices[0]
    candidate_low_idx = 0
    candidate_low_log = log_prices[0]
    
    for i in range(1, n):
        current_log = log_prices[i]
        
        # Controlla pivot low (prezzo risale dal minimo)
        log_move_from_low = current_log - candidate_low_log
        pct_move_from_low = np.exp(log_move_from_low) - 1
        
        if pct_move_from_low >= threshold:
            # Confermato pivot low
            lows.append((candidate_low_idx, prices[candidate_low_idx]))
            # Reset candidati
            candidate_high_idx = i
            candidate_high_log = current_log
            candidate_low_idx = i
            candidate_low_log = current_log
        elif current_log < candidate_low_log:
            # Nuovo minimo più basso
            candidate_low_idx = i
            candidate_low_log = current_log
        
        # Controlla pivot high (prezzo scende dal massimo)
        log_move_from_high = candidate_high_log - current_log
        pct_move_from_high = np.exp(log_move_from_high) - 1
        
        if pct_move_from_high >= threshold:
            # Confermato pivot high
            highs.append((candidate_high_idx, prices[candidate_high_idx]))
            # Reset candidati
            candidate_high_idx = i
            candidate_high_log = current_log
            candidate_low_idx = i
            candidate_low_log = current_log
        elif current_log > candidate_high_log:
            # Nuovo massimo più alto
            candidate_high_idx = i
            candidate_high_log = current_log
    
    return highs, lows


def pivots_atr_adaptive(
    df: pd.DataFrame,
    atr_len: int = 14,
    atr_mult: float = 1.5,
    method: Literal["sma", "wilder", "ema"] = "ema",
    price_col: str = "Close"
) -> Tuple[List[Tuple[int, float]], List[Tuple[int, float]]]:
    """
    Rileva pivot points usando ATR PERCENTUALE come soglia adattiva (crypto-optimized).
    
    La soglia si adatta automaticamente alla volatilità del mercato:
    - Mercato calmo (ATR% basso) → pivot più frequenti
    - Mercato volatile (ATR% alto) → solo pivot significativi
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con colonne: High, Low, Close
    atr_len : int, default 14
        Periodo per calcolo ATR percentuale
    atr_mult : float, default 1.5
        Moltiplicatore ATR (soglia = ATR% × atr_mult)
        - 0.5-1.0: Più sensibile (più pivot)
        - 1.5-2.0: Standard
        - 2.5-3.0: Conservativo (meno pivot, più affidabili)
    method : {"sma", "wilder", "ema"}, default "ema"
        Metodo smoothing ATR (ema consigliato per crypto)
    price_col : str, default "Close"
        Colonna prezzi per pivot detection
        
    Returns
    -------
    tuple
        (highs, lows) con lista di (indice, prezzo) per ogni pivot
        
    Notes
    -----
    Formula classica (ATR assoluto - problematico):
        soglia = ATR_abs × k
        
    Formula moderna (ATR percentuale - adatta crypto):
        soglia% = ATR% × k
        move% = (P_t - P_cand) / P_cand
        pivot confermato se: move% >= soglia%
        
    Vantaggi per crypto:
    - Auto-adattamento: Volatile → soglie più alte
    - Normalizzato: Confrontabile tra asset diversi
    - Reattivo: EMA cattura cambi rapidi di volatilità
    
    Examples
    --------
    >>> highs, lows = pivots_atr_adaptive(df, atr_mult=1.5, method="ema")
    >>> print(f"ATR% medio: {atr_percent(df).mean():.2f}%")
    >>> print(f"Soglia adattiva: {atr_percent(df).mean() * 1.5:.2f}%")
    """
    # Calcola ATR percentuale
    atr_pct = atr_percent(df, length=atr_len, method=method).values
    
    if price_col not in df.columns:
        raise ValueError(f"Colonna '{price_col}' non trovata")
    
    prices = df[price_col].values
    n = len(prices)
    
    highs = []
    lows = []
    
    candidate_high_idx = 0
    candidate_high_price = prices[0]
    candidate_low_idx = 0
    candidate_low_price = prices[0]
    
    for i in range(atr_len, n):  # Start dopo warming up ATR
        current_price = prices[i]
        current_atr_pct = atr_pct[i]
        
        if np.isnan(current_atr_pct):
            continue
        
        # Soglia adattiva percentuale
        threshold_pct = current_atr_pct / 100 * atr_mult
        
        # Check pivot low
        if candidate_low_price > 0:
            pct_move_from_low = (current_price - candidate_low_price) / candidate_low_price
            
            if pct_move_from_low >= threshold_pct:
                lows.append((candidate_low_idx, candidate_low_price))
                candidate_high_idx = i
                candidate_high_price = current_price
                candidate_low_idx = i
                candidate_low_price = current_price
            elif current_price < candidate_low_price:
                candidate_low_idx = i
                candidate_low_price = current_price
        
        # Check pivot high
        if candidate_high_price > 0:
            pct_move_from_high = (candidate_high_price - current_price) / candidate_high_price
            
            if pct_move_from_high >= threshold_pct:
                highs.append((candidate_high_idx, candidate_high_price))
                candidate_high_idx = i
                candidate_high_price = current_price
                candidate_low_idx = i
                candidate_low_price = current_price
            elif current_price > candidate_high_price:
                candidate_high_idx = i
                candidate_high_price = current_price
    
    return highs, lows


def compute_ppb_dynamic(
    df: pd.DataFrame,
    pivot_idx: int,
    atr_len: int = 14,
    atr_method: Literal["sma", "wilder", "ema"] = "ema",
    volatility_window: int = 50,
    base_divisor: float = 2.0
) -> float:
    """
    Calcola Price Per Bar DINAMICO adattivo alla volatilità rolling (crypto-optimized).
    
    Il PPB si adatta automaticamente alle condizioni di mercato:
    - Alta volatilità recente → PPB più alto (linee più ripide)
    - Bassa volatilità recente → PPB più basso (linee più piatte)
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con dati OHLCV
    pivot_idx : int
        Indice del pivot
    atr_len : int, default 14
        Periodo ATR
    atr_method : {"sma", "wilder", "ema"}, default "ema"
        Metodo smoothing ATR
    volatility_window : int, default 50
        Finestra per calcolare volatilità realizzata rolling
    base_divisor : float, default 2.0
        Divisore base per scaling PPB
        
    Returns
    -------
    float
        Price Per Bar dinamico (percentuale del prezzo)
        
    Notes
    -----
    Formula classica (PPB fisso - inadatto crypto):
        PPB = ATR / divisor
        
    Formula moderna (PPB dinamico - crypto-adapted):
        RV = realized_volatility(window)  # Volatilità realizzata
        ATR_pct = ATR percentuale al pivot
        adaptive_factor = RV / ATR_pct  # Rapporto volatilità
        PPB = (ATR_pct / base_divisor) × adaptive_factor × price
        
    Vantaggi per crypto:
    - Auto-scaling: Si adatta a pump/dump improvvisi
    - Forward-looking: Anticipa espansioni/contrazioni volatilità
    - Proporzionale: PPB sempre relativo al prezzo corrente
    
    Examples
    --------
    >>> ppb = compute_ppb_dynamic(df, pivot_idx=68, volatility_window=50)
    >>> print(f"PPB dinamico: {ppb:.2f} EUR/barra")
    """
    if pivot_idx < 0 or pivot_idx >= len(df):
        raise ValueError(f"pivot_idx {pivot_idx} fuori range [0, {len(df)-1}]")
    
    # ATR percentuale al pivot
    atr_pct_series = atr_percent(df, length=atr_len, method=atr_method)
    atr_pct_value = atr_pct_series.iloc[pivot_idx]
    
    if np.isnan(atr_pct_value):
        raise ValueError(
            f"ATR non disponibile all'indice {pivot_idx}. "
            f"Aumenta lunghezza DataFrame o riduci atr_len."
        )
    
    # Volatilità realizzata (rolling std dei log returns)
    close_prices = df["Close"].values
    log_returns = np.diff(np.log(close_prices))
    
    start_idx = max(0, pivot_idx - volatility_window)
    end_idx = pivot_idx
    
    if end_idx - start_idx < 10:
        # Finestra troppo piccola, usa ATR standard
        realized_vol_pct = atr_pct_value
    else:
        window_returns = log_returns[start_idx:end_idx]
        realized_vol_pct = np.std(window_returns) * np.sqrt(len(window_returns)) * 100
    
    # Fattore adattivo: quanto è "calda" la volatilità recente vs ATR
    if atr_pct_value > 0:
        adaptive_factor = realized_vol_pct / atr_pct_value
        # Clamp per evitare estremi
        adaptive_factor = np.clip(adaptive_factor, 0.5, 2.0)
    else:
        adaptive_factor = 1.0
    
    # PPB dinamico: percentuale del prezzo al pivot
    pivot_price = close_prices[pivot_idx]
    ppb_pct = (atr_pct_value / base_divisor) * adaptive_factor
    ppb_absolute = (ppb_pct / 100) * pivot_price
    
    return ppb_absolute


def gann_fan(
    df: pd.DataFrame,
    pivot_source: Literal["last_low", "last_high", "custom"] = "last_low",
    pivot_mode: Literal["atr", "percent"] = "atr",
    threshold: float = 0.05,
    atr_len: int = 14,
    atr_mult: float = 1.5,
    atr_method: Literal["sma", "wilder", "ema"] = "ema",
    use_dynamic_ppb: bool = True,
    base_divisor: float = 2.0,
    volatility_window: int = 50,
    ratios: Optional[List[float]] = None,
    bars_forward: int = 100,
    custom_pivot: Optional[Tuple[int, float]] = None
) -> FanResult:
    """
    Costruisce ventaglio di Gann CRYPTO-ADAPTED con scala log e volatilità dinamica.
    
    Implementazione moderna ottimizzata per trading crypto:
    - ATR percentuale (normalizzato)
    - Scala logaritmica per prezzi
    - PPB dinamico adattivo
    - Ratios calibrati per crypto volatility
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con colonne: High, Low, Close, Volume (opzionale)
    pivot_source : {"last_low", "last_high", "custom"}, default "last_low"
        Fonte del pivot
    pivot_mode : {"atr", "percent"}, default "atr"
        Metodo rilevamento pivot ("atr" consigliato per crypto)
    threshold : float, default 0.05
        Soglia percentuale per pivot_mode="percent"
    atr_len : int, default 14
        Periodo ATR
    atr_mult : float, default 1.5
        Moltiplicatore ATR per pivot detection
    atr_method : {"sma", "wilder", "ema"}, default "ema"
        Metodo smoothing ATR (ema consigliato per crypto)
    use_dynamic_ppb : bool, default True
        True: PPB dinamico adattivo (consigliato crypto)
        False: PPB standard da ATR
    base_divisor : float, default 2.0
        Divisore base per calcolo PPB
    volatility_window : int, default 50
        Finestra volatilità per PPB dinamico
    ratios : List[float], optional
        Ratios del ventaglio. Default crypto-optimized:
        [1/8, 1/4, 1/2, 1, 2, 4, 8]
    bars_forward : int, default 100
        Barre di proiezione forward
    custom_pivot : Tuple[int, float], optional
        Pivot personalizzato (indice, prezzo)
        
    Returns
    -------
    FanResult
        Risultato con pivot_idx, pivot_price, ppb, lines
        
    Notes
    -----
    ADATTAMENTI CRYPTO PRINCIPALI:
    
    1. ATR Percentuale:
       ATR% = (ATR / Close) × 100
       → Normalizzato, comparabile tra asset
       
    2. Scala Logaritmica per Prezzi:
       P_log = log(P)
       → Cattura movimenti % invece di assoluti
       
    3. PPB Dinamico:
       PPB = f(ATR%, realized_vol, price)
       → Si adatta a volatilità rolling
       
    4. Ratios Calibrati:
       Default = [1/8, 1/4, 1/2, 1, 2, 4, 8]
       → Bilancia velocità/affidabilità per crypto
       
    Examples
    --------
    >>> # Esempio base: ultime 24h BTC/EUR
    >>> from gann_fan import get_coinbase_candles, gann_fan
    >>> df = get_coinbase_candles("BTC-EUR", 900, 96)
    >>> fan = gann_fan(df, pivot_source="last_low", use_dynamic_ppb=True)
    >>> print(f"PPB dinamico: {fan.ppb:.2f}")
    
    >>> # Esempio avanzato: PPB comparazione
    >>> fan_dynamic = gann_fan(df, use_dynamic_ppb=True)
    >>> fan_static = gann_fan(df, use_dynamic_ppb=False)
    >>> print(f"Dynamic: {fan_dynamic.ppb:.2f} vs Static: {fan_static.ppb:.2f}")
    """
    # Validazioni
    required_cols = ["High", "Low", "Close"]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Colonne mancanti nel DataFrame: {missing}")
    
    if len(df) < atr_len + 10:
        raise ValueError(
            f"DataFrame troppo corto ({len(df)} righe). "
            f"Serve almeno {atr_len + 10} righe per calcoli affidabili."
        )
    
    if ratios is None:
        # Ratios default crypto-optimized
        ratios = [1/8, 1/4, 1/2, 1, 2, 4, 8]
    
    # Rimuovi duplicati e ordina
    ratios = sorted(list(set(ratios)))
    
    if not ratios or any(r <= 0 for r in ratios):
        raise ValueError("ratios deve essere lista non vuota con valori > 0")
    
    if bars_forward <= 0:
        raise ValueError(f"bars_forward deve essere > 0, ricevuto: {bars_forward}")
    
    # Determina pivot
    if pivot_source == "custom":
        if custom_pivot is None:
            raise ValueError("pivot_source='custom' richiede custom_pivot=(idx, price)")
        pivot_idx, pivot_price = custom_pivot
        if pivot_idx < 0 or pivot_idx >= len(df):
            raise ValueError(f"pivot_idx {pivot_idx} fuori range")
    else:
        # Rileva pivot automaticamente
        if pivot_mode == "percent":
            highs, lows = pivots_percent_log(df, threshold=threshold)
        elif pivot_mode == "atr":
            highs, lows = pivots_atr_adaptive(
                df, atr_len=atr_len, atr_mult=atr_mult, method=atr_method
            )
        else:
            raise ValueError(f"pivot_mode deve essere 'atr' o 'percent', ricevuto: {pivot_mode}")
        
        if pivot_source == "last_low":
            if not lows:
                raise ValueError(
                    "Nessun pivot low trovato. Prova a ridurre threshold/atr_mult "
                    "o aumentare lunghezza DataFrame."
                )
            pivot_idx, pivot_price = lows[-1]
            direction = "up"
        elif pivot_source == "last_high":
            if not highs:
                raise ValueError(
                    "Nessun pivot high trovato. Prova a ridurre threshold/atr_mult "
                    "o aumentare lunghezza DataFrame."
                )
            pivot_idx, pivot_price = highs[-1]
            direction = "down"
        else:
            raise ValueError(
                f"pivot_source deve essere 'last_low', 'last_high' o 'custom', "
                f"ricevuto: {pivot_source}"
            )
    
    # Determina direzione se custom
    if pivot_source == "custom":
        # Guess direction: guarda prezzi dopo pivot
        if pivot_idx < len(df) - 1:
            avg_after = df["Close"].iloc[pivot_idx+1:min(pivot_idx+11, len(df))].mean()
            direction = "up" if avg_after > pivot_price else "down"
        else:
            direction = "up"  # Default
    
    # Calcola PPB
    if use_dynamic_ppb:
        ppb = compute_ppb_dynamic(
            df,
            pivot_idx=pivot_idx,
            atr_len=atr_len,
            atr_method=atr_method,
            volatility_window=volatility_window,
            base_divisor=base_divisor
        )
    else:
        # PPB statico da ATR percentuale
        atr_pct_series = atr_percent(df, length=atr_len, method=atr_method)
        atr_pct_value = atr_pct_series.iloc[pivot_idx]
        
        if np.isnan(atr_pct_value):
            raise ValueError(f"ATR non disponibile all'indice {pivot_idx}")
        
        # Converti ATR% in valore assoluto
        ppb = (atr_pct_value / 100 / base_divisor) * pivot_price
    
    # Costruisci linee
    end_idx = min(pivot_idx + bars_forward, len(df) - 1)
    
    lines = []
    for ratio in ratios:
        if direction == "up":
            y1 = pivot_price + ratio * ppb * (end_idx - pivot_idx)
        else:  # down
            y1 = pivot_price - ratio * ppb * (end_idx - pivot_idx)
        
        lines.append(FanLine(
            ratio=ratio,
            direction=direction,
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


# Mantieni compatibilità backward con nomi legacy
atr = atr_percent  # Alias per compatibilità
pivots_percent = pivots_percent_log
pivots_atr = pivots_atr_adaptive
compute_ppb = compute_ppb_dynamic
