"""
Script di esempio per testare il modulo Gann Fan con dati sintetici.

Genera dati di prezzo simulati e calcola/visualizza un ventaglio di Gann.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

from gann_fan.core import gann_fan
from gann_fan.plot import plot_fan_with_date


def generate_sample_data(n_bars: int = 500) -> pd.DataFrame:
    """
    Genera dati di prezzo sintetici con trend e swing.
    
    Parameters
    ----------
    n_bars : int
        Numero di barre da generare
    
    Returns
    -------
    pd.DataFrame
        DataFrame con colonne Date, Open, High, Low, Close, Volume
    """
    np.random.seed(42)
    
    # Genera serie temporale
    start_date = datetime(2024, 1, 1)
    dates = [start_date + timedelta(hours=i) for i in range(n_bars)]
    
    # Genera prezzi con trend e volatilità
    base_price = 40000
    trend = np.linspace(0, 5000, n_bars)  # Trend rialzista
    
    # Oscillazione sinusoidale
    swing = 2000 * np.sin(np.linspace(0, 4 * np.pi, n_bars))
    
    # Rumore random
    noise = np.random.normal(0, 500, n_bars)
    
    # Prezzo close
    close = base_price + trend + swing + noise
    
    # Genera OHLC
    high = close + np.abs(np.random.normal(200, 100, n_bars))
    low = close - np.abs(np.random.normal(200, 100, n_bars))
    open_price = close + np.random.normal(0, 100, n_bars)
    
    # Volume casuale
    volume = np.random.uniform(1000000, 5000000, n_bars)
    
    df = pd.DataFrame({
        "Date": dates,
        "Open": open_price,
        "High": high,
        "Low": low,
        "Close": close,
        "Volume": volume
    })
    
    return df


def main():
    """Funzione principale dell'esempio."""
    print("=" * 60)
    print("Gann Fan - Esempio con dati sintetici")
    print("=" * 60)
    
    # Genera dati
    print("\n1. Generazione dati sintetici...")
    df = generate_sample_data(n_bars=500)
    print(f"   Generati {len(df)} record da {df['Date'].min()} a {df['Date'].max()}")
    print(f"   Range prezzi: {df['Close'].min():.2f} - {df['Close'].max():.2f}")
    
    # Calcola ventaglio con pivot automatico (last_low)
    print("\n2. Calcolo ventaglio di Gann (last_low, ATR)...")
    fan1 = gann_fan(
        df,
        pivot_source="last_low",
        pivot_mode="atr",
        atr_len=14,
        atr_mult=1.5,
        atr_method="sma",
        ppb_mode="ATR",
        atr_divisor=1.5,
        ratios=[1/8, 1/4, 1/2, 1, 2, 4, 8],
        bars_forward=200
    )
    
    print(f"   Pivot: indice={fan1.pivot_idx}, data={df.iloc[fan1.pivot_idx]['Date']}, prezzo={fan1.pivot_price:.2f}")
    print(f"   PPB: {fan1.ppb:.6f}")
    print(f"   Linee generate: {len(fan1.lines)}")
    
    # Calcola ventaglio con pivot custom
    print("\n3. Calcolo ventaglio con pivot custom...")
    custom_idx = 150
    custom_price = df.iloc[custom_idx]["Close"]
    
    fan2 = gann_fan(
        df,
        pivot_source="custom",
        custom_pivot=(custom_idx, custom_price),
        ppb_mode="Fixed",
        fixed_ppb=50.0,
        ratios=[1/4, 1/2, 1, 2, 4],
        bars_forward=250
    )
    
    print(f"   Pivot: indice={fan2.pivot_idx}, data={df.iloc[fan2.pivot_idx]['Date']}, prezzo={fan2.pivot_price:.2f}")
    print(f"   PPB: {fan2.ppb:.6f}")
    print(f"   Linee generate: {len(fan2.lines)}")
    
    # Visualizza entrambi i ventagli
    print("\n4. Creazione visualizzazioni...")
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(16, 12))
    
    # Plot 1: Ventaglio automatico
    plot_fan_with_date(df, fan1, date_col="Date", ax=ax1, show_labels=True)
    ax1.set_title("Gann Fan - Pivot automatico (last_low, ATR)", fontsize=14, fontweight="bold")
    
    # Plot 2: Ventaglio custom
    plot_fan_with_date(df, fan2, date_col="Date", ax=ax2, show_labels=True)
    ax2.set_title("Gann Fan - Pivot custom con PPB fisso", fontsize=14, fontweight="bold")
    
    plt.tight_layout()
    
    # Salva immagine
    output_file = "gann_fan_example.png"
    plt.savefig(output_file, dpi=150, bbox_inches="tight")
    print(f"   Grafico salvato in: {output_file}")
    
    # Mostra
    plt.show()
    
    print("\n" + "=" * 60)
    print("Esempio completato!")
    print("=" * 60)


if __name__ == "__main__":
    main()
