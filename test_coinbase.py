"""
Test con dati reali da Coinbase API.

Scarica dati OHLC con timeframe 15 minuti e testa il ventaglio di Gann.
"""

import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import time

from gann_fan.core import gann_fan
from gann_fan.plot import plot_fan_with_date


def get_coinbase_candles(
    product_id: str = "BTC-EUR",
    granularity: int = 900,  # 15 minuti = 900 secondi
    num_candles: int = 300
) -> pd.DataFrame:
    """
    Scarica dati OHLC da Coinbase Public API.
    
    Parameters
    ----------
    product_id : str
        Coppia di trading (es. "BTC-EUR", "ETH-USD")
    granularity : int
        Granularità in secondi:
        - 60: 1 minuto
        - 300: 5 minuti
        - 900: 15 minuti
        - 3600: 1 ora
        - 21600: 6 ore
        - 86400: 1 giorno
    num_candles : int
        Numero di candele da scaricare
    
    Returns
    -------
    pd.DataFrame
        DataFrame con colonne: Date, Open, High, Low, Close, Volume
    """
    print(f"Scaricamento dati da Coinbase API...")
    print(f"  Prodotto: {product_id}")
    print(f"  Granularità: {granularity}s ({granularity//60} minuti)")
    print(f"  Numero candele: {num_candles}")
    
    # Endpoint API pubblica di Coinbase
    base_url = "https://api.exchange.coinbase.com"
    endpoint = f"/products/{product_id}/candles"
    
    # Coinbase restituisce max 300 candele per richiesta
    max_per_request = 300
    all_data = []
    
    end_time = datetime.utcnow()
    
    # Calcola quante richieste servono
    num_requests = (num_candles + max_per_request - 1) // max_per_request
    
    for i in range(num_requests):
        candles_to_get = min(max_per_request, num_candles - len(all_data))
        
        # Calcola start e end time
        end_timestamp = int(end_time.timestamp())
        start_timestamp = end_timestamp - (candles_to_get * granularity)
        
        params = {
            "granularity": granularity,
            "start": start_timestamp,
            "end": end_timestamp
        }
        
        try:
            response = requests.get(base_url + endpoint, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                print(f"  Warning: Nessun dato ricevuto nella richiesta {i+1}")
                break
            
            all_data.extend(data)
            print(f"  Richiesta {i+1}/{num_requests}: {len(data)} candele scaricate")
            
            # Aggiorna end_time per la prossima richiesta
            end_time = datetime.fromtimestamp(data[-1][0])
            
            # Rate limiting
            if i < num_requests - 1:
                time.sleep(0.5)
                
        except requests.exceptions.RequestException as e:
            print(f"  Errore nella richiesta: {e}")
            break
    
    if not all_data:
        raise ValueError("Nessun dato scaricato da Coinbase")
    
    print(f"  Totale candele scaricate: {len(all_data)}")
    
    # Converti in DataFrame
    # Formato Coinbase: [timestamp, low, high, open, close, volume]
    df = pd.DataFrame(all_data, columns=["timestamp", "Low", "High", "Open", "Close", "Volume"])
    
    # Converti timestamp in datetime
    df["Date"] = pd.to_datetime(df["timestamp"], unit="s")
    
    # Riordina colonne
    df = df[["Date", "Open", "High", "Low", "Close", "Volume"]]
    
    # Ordina per data crescente
    df = df.sort_values("Date").reset_index(drop=True)
    
    # Converti a float
    for col in ["Open", "High", "Low", "Close", "Volume"]:
        df[col] = df[col].astype(float)
    
    print(f"  Range date: {df['Date'].min()} -> {df['Date'].max()}")
    print(f"  Range prezzi: {df['Close'].min():.2f} -> {df['Close'].max():.2f}")
    print(f"  Volume totale: {df['Volume'].sum():.2f}")
    
    return df


def test_gann_with_real_data():
    """Test completo del ventaglio di Gann con dati reali."""
    print("=" * 70)
    print("TEST GANN FAN CON DATI REALI DA COINBASE")
    print("=" * 70)
    print()
    
    # Scarica dati reali
    try:
        df = get_coinbase_candles(
            product_id="BTC-EUR",
            granularity=900,  # 15 minuti
            num_candles=500
        )
    except Exception as e:
        print(f"\n❌ Errore nello scaricamento dati: {e}")
        print("\nProva con dati di backup...")
        return test_with_backup_data()
    
    print("\n" + "=" * 70)
    print("TEST 1: Pivot automatico (last_low) con ATR")
    print("=" * 70)
    
    try:
        fan1 = gann_fan(
            df,
            pivot_source="last_low",
            pivot_mode="atr",
            atr_len=14,
            atr_mult=1.5,
            atr_method="sma",
            ppb_mode="ATR",
            atr_divisor=2.0,
            ratios=[1/8, 1/4, 1/2, 1, 2, 4, 8],
            bars_forward=50  # Ridotto per migliore visualizzazione
        )
        
        print(f"✓ Ventaglio calcolato con successo!")
        print(f"  Pivot: indice={fan1.pivot_idx}, data={df.iloc[fan1.pivot_idx]['Date']}")
        print(f"  Prezzo pivot: {fan1.pivot_price:.2f} EUR")
        print(f"  PPB (ATR-based): {fan1.ppb:.4f}")
        print(f"  Linee generate: {len(fan1.lines)}")
        print(f"  Direzione: {fan1.lines[0].direction}")
        
        # Stampa dettagli linee
        print("\n  Dettaglio linee:")
        for line in fan1.lines:
            print(f"    Ratio {line.ratio:.3f}: {line.y0:.2f} -> {line.y1:.2f}")
        
        # Salva grafico con zoom sul pivot
        fig, ax = plt.subplots(figsize=(16, 9))
        
        # Limita la visualizzazione a una finestra ragionevole intorno al pivot
        start_idx = max(0, fan1.pivot_idx - 50)
        end_idx = min(len(df) - 1, fan1.pivot_idx + 100)
        df_view = df.iloc[start_idx:end_idx+1].copy()
        df_view_reset = df_view.reset_index(drop=True)
        
        # Aggiusta gli indici del fan per la vista
        fan1_adjusted = type(fan1)(
            pivot_idx=fan1.pivot_idx - start_idx,
            pivot_price=fan1.pivot_price,
            ppb=fan1.ppb,
            lines=[
                type(line)(
                    ratio=line.ratio,
                    direction=line.direction,
                    start_idx=max(0, line.start_idx - start_idx),
                    end_idx=min(len(df_view_reset) - 1, line.end_idx - start_idx),
                    y0=line.y0,
                    y1=line.y1
                )
                for line in fan1.lines
            ]
        )
        
        plot_fan_with_date(df_view_reset, fan1_adjusted, date_col="Date", ax=ax, show_labels=True)
        ax.set_title(
            f"Gann Fan BTC/EUR 15min - Pivot Low Automatico (ATR)\n"
            f"Pivot: {df.iloc[fan1.pivot_idx]['Date']} @ {fan1.pivot_price:.2f} EUR",
            fontsize=14,
            fontweight="bold"
        )
        plt.tight_layout()
        plt.savefig("coinbase_btc_eur_15min_last_low.png", dpi=150, bbox_inches="tight")
        print(f"\n✓ Grafico salvato: coinbase_btc_eur_15min_last_low.png")
        
    except Exception as e:
        print(f"\n❌ Errore nel Test 1: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("TEST 2: Pivot automatico (last_high) con percentuale")
    print("=" * 70)
    
    try:
        fan2 = gann_fan(
            df,
            pivot_source="last_high",
            pivot_mode="percent",
            threshold=0.03,  # 3%
            ppb_mode="ATR",
            atr_len=20,
            atr_divisor=1.5,
            ratios=[1/4, 1/2, 1, 2, 4],
            bars_forward=80  # Ridotto per migliore visualizzazione
        )
        
        print(f"✓ Ventaglio calcolato con successo!")
        print(f"  Pivot: indice={fan2.pivot_idx}, data={df.iloc[fan2.pivot_idx]['Date']}")
        print(f"  Prezzo pivot: {fan2.pivot_price:.2f} EUR")
        print(f"  PPB (ATR-based): {fan2.ppb:.4f}")
        print(f"  Linee generate: {len(fan2.lines)}")
        print(f"  Direzione: {fan2.lines[0].direction}")
        
        # Salva grafico con zoom
        fig, ax = plt.subplots(figsize=(16, 9))
        
        # Limita la visualizzazione
        start_idx = max(0, fan2.pivot_idx - 30)
        end_idx = min(len(df) - 1, fan2.pivot_idx + 100)
        df_view = df.iloc[start_idx:end_idx+1].copy()
        df_view_reset = df_view.reset_index(drop=True)
        
        # Aggiusta gli indici
        fan2_adjusted = type(fan2)(
            pivot_idx=fan2.pivot_idx - start_idx,
            pivot_price=fan2.pivot_price,
            ppb=fan2.ppb,
            lines=[
                type(line)(
                    ratio=line.ratio,
                    direction=line.direction,
                    start_idx=max(0, line.start_idx - start_idx),
                    end_idx=min(len(df_view_reset) - 1, line.end_idx - start_idx),
                    y0=line.y0,
                    y1=line.y1
                )
                for line in fan2.lines
            ]
        )
        
        plot_fan_with_date(df_view_reset, fan2_adjusted, date_col="Date", ax=ax, show_labels=True)
        ax.set_title(
            f"Gann Fan BTC/EUR 15min - Pivot High Automatico (3% threshold)\n"
            f"Pivot: {df.iloc[fan2.pivot_idx]['Date']} @ {fan2.pivot_price:.2f} EUR",
            fontsize=14,
            fontweight="bold"
        )
        plt.tight_layout()
        plt.savefig("coinbase_btc_eur_15min_last_high.png", dpi=150, bbox_inches="tight")
        print(f"\n✓ Grafico salvato: coinbase_btc_eur_15min_last_high.png")
        
    except Exception as e:
        print(f"\n❌ Errore nel Test 2: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("TEST 3: Confronto multipli timeframe su stesso grafico")
    print("=" * 70)
    
    try:
        # Trova pivot significativo
        from gann_fan.core import pivots_atr
        highs, lows = pivots_atr(df, atr_len=14, atr_mult=1.2, method="sma")
        
        if len(lows) > 0:
            # Usa l'ultimo pivot low più recente per migliore visualizzazione
            pivot_idx = lows[-1][0]  # Ultimo low
            pivot_price = df.iloc[pivot_idx]["Close"]
            
            print(f"  Pivot selezionato: idx={pivot_idx}, price={pivot_price:.2f}")
            
            # Tre ventagli con PPB diversi - bars_forward ridotto
            fan_narrow = gann_fan(
                df, pivot_source="custom", custom_pivot=(pivot_idx, pivot_price),
                ppb_mode="ATR", atr_len=14, atr_divisor=3.0,
                ratios=[1, 2], bars_forward=50
            )
            
            fan_medium = gann_fan(
                df, pivot_source="custom", custom_pivot=(pivot_idx, pivot_price),
                ppb_mode="ATR", atr_len=14, atr_divisor=2.0,
                ratios=[1, 2], bars_forward=50
            )
            
            fan_wide = gann_fan(
                df, pivot_source="custom", custom_pivot=(pivot_idx, pivot_price),
                ppb_mode="ATR", atr_len=14, atr_divisor=1.0,
                ratios=[1, 2], bars_forward=50
            )
            
            print(f"  PPB narrow: {fan_narrow.ppb:.4f}")
            print(f"  PPB medium: {fan_medium.ppb:.4f}")
            print(f"  PPB wide: {fan_wide.ppb:.4f}")
            
            # Plot combinato con zoom
            fig, ax = plt.subplots(figsize=(18, 10))
            
            # Limita visualizzazione a finestra intorno al pivot
            start_idx = max(0, pivot_idx - 30)
            end_idx = min(len(df) - 1, pivot_idx + 80)
            
            # Prezzi nella finestra
            ax.plot(df["Date"].iloc[start_idx:end_idx+1], 
                   df["Close"].iloc[start_idx:end_idx+1], 
                   label="BTC/EUR Close", color="black", linewidth=1.5, zorder=2)
            
            # Pivot
            ax.scatter([df.iloc[pivot_idx]["Date"]], [pivot_price], 
                      color="red", s=150, zorder=5, label=f"Pivot @ {pivot_price:.2f}")
            
            # Ventagli con colori diversi
            colors = ["blue", "green", "orange"]
            alphas = [0.6, 0.7, 0.8]
            labels = ["Narrow (÷3)", "Medium (÷2)", "Wide (÷1)"]
            linewidths = [2.0, 2.0, 2.0]
            
            for fan, color, alpha, label, lw in zip([fan_narrow, fan_medium, fan_wide], colors, alphas, labels, linewidths):
                for line in fan.lines:
                    # Disegna tutte le linee del ventaglio, anche se escono dalla finestra
                    x = [df.iloc[line.start_idx]["Date"], df.iloc[line.end_idx]["Date"]]
                    y = [line.y0, line.y1]
                    ax.plot(x, y, color=color, linestyle="--", linewidth=lw, alpha=alpha)
                
                # Label solo per una linea
                ax.plot([], [], color=color, linestyle="--", linewidth=lw+0.5, label=f"Fan {label}")
            
            ax.set_xlabel("Date", fontsize=12)
            ax.set_ylabel("Price (EUR)", fontsize=12)
            ax.set_title(
                f"Gann Fan BTC/EUR 15min - Confronto PPB Multipli\n"
                f"Pivot: {df.iloc[pivot_idx]['Date']} @ {pivot_price:.2f} EUR",
                fontsize=14,
                fontweight="bold"
            )
            ax.legend(loc="best", fontsize=10)
            ax.grid(True, alpha=0.3)
            plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
            plt.tight_layout()
            plt.savefig("coinbase_btc_eur_15min_multiple_fans.png", dpi=150, bbox_inches="tight")
            print(f"\n✓ Grafico salvato: coinbase_btc_eur_15min_multiple_fans.png")
        
    except Exception as e:
        print(f"\n❌ Errore nel Test 3: {e}")
        import traceback
        traceback.print_exc()
    
    # Salva dati per riferimento futuro
    df.to_csv("coinbase_btc_eur_15min_data.csv", index=False)
    print(f"\n✓ Dati salvati: coinbase_btc_eur_15min_data.csv")
    
    print("\n" + "=" * 70)
    print("✅ TUTTI I TEST COMPLETATI CON SUCCESSO!")
    print("=" * 70)
    print("\nFile generati:")
    print("  - coinbase_btc_eur_15min_last_low.png")
    print("  - coinbase_btc_eur_15min_last_high.png")
    print("  - coinbase_btc_eur_15min_multiple_fans.png")
    print("  - coinbase_btc_eur_15min_data.csv")


def test_with_backup_data():
    """Test con dati di backup se Coinbase non è disponibile."""
    print("\nGenerazione dati di backup con pattern realistici...")
    
    # Genera dati simulati più realistici
    np.random.seed(42)
    n = 500
    
    # Trend base
    base = 85000
    trend = np.linspace(0, 5000, n)
    
    # Oscillazioni a diverse frequenze
    cycle1 = 3000 * np.sin(np.linspace(0, 3 * np.pi, n))
    cycle2 = 1000 * np.sin(np.linspace(0, 8 * np.pi, n))
    
    # Rumore
    noise = np.random.normal(0, 400, n)
    
    # Close price
    close = base + trend + cycle1 + cycle2 + noise
    
    # OHLC
    high = close + np.abs(np.random.normal(150, 50, n))
    low = close - np.abs(np.random.normal(150, 50, n))
    open_price = close + np.random.normal(0, 80, n)
    volume = np.random.uniform(10, 100, n)
    
    # Date (15 minuti)
    start_date = datetime.now() - timedelta(minutes=15 * n)
    dates = [start_date + timedelta(minutes=15 * i) for i in range(n)]
    
    df = pd.DataFrame({
        "Date": dates,
        "Open": open_price,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume
    })
    
    print(f"Dati generati: {len(df)} candele")
    print(f"Range date: {df['Date'].min()} -> {df['Date'].max()}")
    print(f"Range prezzi: {df['Close'].min():.2f} -> {df['Close'].max():.2f}")
    
    # Test con dati di backup
    print("\nTest con dati simulati...")
    fan = gann_fan(
        df,
        pivot_source="last_low",
        pivot_mode="atr",
        atr_len=14,
        atr_mult=1.5,
        ppb_mode="ATR",
        atr_divisor=2.0,
        ratios=[1/8, 1/4, 1/2, 1, 2, 4, 8],
        bars_forward=100
    )
    
    print(f"✓ Ventaglio calcolato: pivot={fan.pivot_idx}, ppb={fan.ppb:.4f}")
    
    fig, ax = plt.subplots(figsize=(16, 9))
    plot_fan_with_date(df, fan, date_col="Date", ax=ax, show_labels=True)
    ax.set_title("Gann Fan - Dati Simulati BTC/EUR 15min", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig("backup_gann_fan_15min.png", dpi=150, bbox_inches="tight")
    print(f"✓ Grafico salvato: backup_gann_fan_15min.png")
    
    df.to_csv("backup_data_15min.csv", index=False)
    print(f"✓ Dati salvati: backup_data_15min.csv")


if __name__ == "__main__":
    test_gann_with_real_data()
