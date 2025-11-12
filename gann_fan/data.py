"""
Modulo per acquisizione dati da exchange pubblici.

Questo modulo fornisce funzioni per scaricare dati OHLCV da exchange
come Coinbase Pro, utili per testare e utilizzare il Gann Fan su dati reali.
"""

import time
from typing import Optional, Tuple
import pandas as pd
import requests


def get_coinbase_candles(
    product_id: str = "BTC-EUR",
    granularity: int = 3600,
    num_candles: int = 300
) -> pd.DataFrame:
    """
    Scarica dati storici OHLCV da Coinbase Public API.
    
    Parameters
    ----------
    product_id : str, default "BTC-EUR"
        Coppia di trading (es. "BTC-EUR", "ETH-USD", "BTC-USD")
    granularity : int, default 3600
        Granularità in secondi:
        - 60: 1 minuto
        - 300: 5 minuti
        - 900: 15 minuti
        - 3600: 1 ora
        - 21600: 6 ore
        - 86400: 1 giorno
    num_candles : int, default 300
        Numero di candele da scaricare (max ~300 per richiesta)
        
    Returns
    -------
    pd.DataFrame
        DataFrame con colonne: Date, Open, High, Low, Close, Volume
        
    Raises
    ------
    ValueError
        Se product_id o granularity non sono validi
    requests.RequestException
        Se ci sono problemi di rete o API
        
    Examples
    --------
    >>> # Scarica 1 ora di BTC/EUR
    >>> df = get_coinbase_candles("BTC-EUR", granularity=3600, num_candles=100)
    >>> print(df.head())
    
    >>> # Scarica 15 minuti di ETH/USD
    >>> df = get_coinbase_candles("ETH-USD", granularity=900, num_candles=500)
    
    Notes
    -----
    L'API di Coinbase ha limiti di rate (circa 10 req/sec pubbliche).
    Per num_candles > 300, vengono fatte richieste multiple con pausa.
    
    I dati sono ordinati cronologicamente dal più vecchio al più recente.
    """
    # Validazione parametri
    valid_granularities = [60, 300, 900, 3600, 21600, 86400]
    if granularity not in valid_granularities:
        raise ValueError(
            f"Granularity {granularity} non valida. "
            f"Valori supportati: {valid_granularities}"
        )
    
    if num_candles <= 0:
        raise ValueError(f"num_candles deve essere > 0, ricevuto: {num_candles}")
    
    if num_candles > 1000:
        raise ValueError(
            f"num_candles troppo alto ({num_candles}). "
            f"Massimo raccomandato: 1000 per evitare timeout."
        )
    
    base_url = "https://api.exchange.coinbase.com"
    endpoint = f"/products/{product_id}/candles"
    
    all_data = []
    candles_per_request = 300  # Limite API Coinbase
    num_requests = (num_candles + candles_per_request - 1) // candles_per_request
    
    print(f"Scaricamento dati da Coinbase API...")
    print(f"  Prodotto: {product_id}")
    print(f"  Granularità: {granularity}s ({_granularity_to_string(granularity)})")
    print(f"  Numero candele: {num_candles}")
    
    for i in range(num_requests):
        candles_to_fetch = min(candles_per_request, num_candles - len(all_data))
        
        params = {
            "granularity": granularity,
        }
        
        # Se non è la prima richiesta, usa l'ultima timestamp come riferimento
        if all_data:
            # Calcola start dalla fine dell'ultima batch
            last_timestamp = all_data[-1][0]
            params["end"] = last_timestamp
        
        try:
            response = requests.get(
                base_url + endpoint,
                params=params,
                timeout=10
            )
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                print(f"  Richiesta {i+1}/{num_requests}: Nessun dato ricevuto")
                break
            
            # Limita al numero richiesto
            data = data[:candles_to_fetch]
            all_data.extend(data)
            
            print(f"  Richiesta {i+1}/{num_requests}: {len(data)} candele scaricate")
            
            # Pausa per rispettare rate limit (se servono più richieste)
            if i < num_requests - 1:
                time.sleep(0.2)
                
        except requests.exceptions.RequestException as e:
            raise requests.RequestException(
                f"Errore nel download da Coinbase per {product_id}: {e}"
            ) from e
    
    if not all_data:
        raise ValueError(
            f"Nessun dato ricevuto da Coinbase per {product_id}. "
            f"Verifica che il product_id sia valido."
        )
    
    # Converti in DataFrame
    # Formato Coinbase: [timestamp, low, high, open, close, volume]
    df = pd.DataFrame(
        all_data,
        columns=["timestamp", "Low", "High", "Open", "Close", "Volume"]
    )
    
    # Converti timestamp in datetime
    df["Date"] = pd.to_datetime(df["timestamp"], unit="s")
    df = df.drop("timestamp", axis=1)
    
    # Riordina colonne
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    
    # Ordina cronologicamente (dal più vecchio al più recente)
    df = df.sort_values("Date").reset_index(drop=True)
    
    print(f"  Totale candele scaricate: {len(df)}")
    print(f"  Range date: {df['Date'].min()} -> {df['Date'].max()}")
    print(f"  Range prezzi: {df['Low'].min():.2f} -> {df['High'].max():.2f}")
    print(f"  Volume totale: {df['Volume'].sum():.2f}")
    
    return df


def get_available_coinbase_products() -> list[dict]:
    """
    Ottiene la lista di tutti i prodotti disponibili su Coinbase.
    
    Returns
    -------
    list[dict]
        Lista di dizionari con informazioni sui prodotti disponibili.
        Ogni dict contiene: id, base_currency, quote_currency, status
        
    Examples
    --------
    >>> products = get_available_coinbase_products()
    >>> btc_products = [p for p in products if p['base_currency'] == 'BTC']
    >>> print(f"Trovati {len(btc_products)} prodotti BTC")
    """
    base_url = "https://api.exchange.coinbase.com"
    endpoint = "/products"
    
    try:
        response = requests.get(base_url + endpoint, timeout=10)
        response.raise_for_status()
        products = response.json()
        
        # Filtra solo prodotti attivi
        active_products = [
            {
                "id": p.get("id"),
                "base_currency": p.get("base_currency"),
                "quote_currency": p.get("quote_currency"),
                "status": p.get("status", "unknown")
            }
            for p in products
            if p.get("status") == "online"
        ]
        
        return active_products
        
    except requests.exceptions.RequestException as e:
        raise requests.RequestException(
            f"Errore nel download prodotti Coinbase: {e}"
        ) from e


def _granularity_to_string(granularity: int) -> str:
    """Converte granularità in secondi a stringa leggibile."""
    mapping = {
        60: "1 minuto",
        300: "5 minuti",
        900: "15 minuti",
        3600: "1 ora",
        21600: "6 ore",
        86400: "1 giorno"
    }
    return mapping.get(granularity, f"{granularity}s")


def validate_dataframe(df: pd.DataFrame) -> Tuple[bool, str]:
    """
    Valida che un DataFrame sia adatto per l'analisi Gann Fan.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame da validare
        
    Returns
    -------
    tuple[bool, str]
        (is_valid, message) - True se valido, altrimenti False con messaggio errore
        
    Examples
    --------
    >>> df = get_coinbase_candles()
    >>> is_valid, msg = validate_dataframe(df)
    >>> if not is_valid:
    ...     print(f"Errore: {msg}")
    """
    required_cols = ["High", "Low", "Close"]
    
    # Controlla colonne richieste
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        return False, f"Colonne mancanti: {missing}"
    
    # Controlla che non ci siano NaN nelle colonne critiche
    for col in required_cols:
        if df[col].isna().any():
            return False, f"Colonna '{col}' contiene valori NaN"
    
    # Controlla lunghezza minima
    if len(df) < 30:
        return False, f"DataFrame troppo corto ({len(df)} righe). Minimo: 30"
    
    # Controlla che i prezzi siano positivi
    for col in required_cols:
        if (df[col] <= 0).any():
            return False, f"Colonna '{col}' contiene valori <= 0"
    
    # Controlla che High >= Low
    if (df["High"] < df["Low"]).any():
        return False, "Trovate righe dove High < Low"
    
    return True, "DataFrame valido"
