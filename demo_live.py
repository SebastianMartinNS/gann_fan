"""
Script dimostrativo interattivo per Gann Fan con dati reali da Coinbase.

Questo script mostra come usare il modulo gann_fan con dati live.
"""

import matplotlib.pyplot as plt
from gann_fan import (
    get_coinbase_candles,
    validate_dataframe,
    gann_fan,
)
from gann_fan.plot import plot_fan_with_date


def main():
    """Esegue analisi Gann Fan su dati reali."""
    
    print("\n" + "=" * 70)
    print("GANN FAN - Analisi con Dati Reali da Coinbase")
    print("=" * 70 + "\n")
    
    # Scarica dati BTC/EUR 15 minuti - ultime 24 ore
    try:
        df = get_coinbase_candles(
            product_id="BTC-EUR",
            granularity=900,  # 15 minuti
            num_candles=96    # 24 ore × 4 candele/ora
        )
    except Exception as e:
        print(f"\n❌ Errore: {e}")
        return
    
    # Valida DataFrame
    is_valid, msg = validate_dataframe(df)
    if not is_valid:
        print(f"\n❌ Dati non validi: {msg}")
        return
    
    print(f"\n✅ Dati validi: {msg}\n")
    
    # Test 1: Ventaglio da ultimo pivot low (CRYPTO-ADAPTED)
    print("=" * 70)
    print("TEST 1: Ventaglio da Pivot Low - PPB Dinamico Crypto")
    print("=" * 70)
    
    try:
        fan = gann_fan(
            df,
            pivot_source="last_low",
            pivot_mode="atr",
            atr_len=14,
            atr_mult=1.5,
            atr_method="ema",       # EMA per crypto (più reattivo)
            use_dynamic_ppb=True,   # PPB adattivo (NUOVO)
            base_divisor=2.0,
            volatility_window=50,   # Finestra volatilità dinamica
            ratios=[1/8, 1/4, 1/2, 1, 2, 4, 8],  # Ratios classici
            bars_forward=100
        )
        
        print(f"\n✓ Ventaglio calcolato!")
        print(f"  Pivot: indice {fan.pivot_idx}")
        print(f"  Prezzo pivot: {fan.pivot_price:.2f} EUR")
        print(f"  PPB: {fan.ppb:.4f}")
        print(f"  Linee generate: {len(fan.lines)}")
        print(f"  Direzione: {fan.lines[0].direction.upper()}")
        
        # Visualizza
        fig, ax = plt.subplots(figsize=(16, 9))
        plot_fan_with_date(df, fan, date_col="Date", ax=ax, show_labels=True)
        ax.set_title(
            f"Gann Fan BTC/EUR 15min - Pivot Low (Crypto-Adapted)\n"
            f"Pivot @ {fan.pivot_price:.2f} EUR | PPB Dinamico: {fan.ppb:.2f}",
            fontsize=14,
            fontweight="bold"
        )
        plt.tight_layout()
        plt.savefig("gann_fan_live_low.png", dpi=150, bbox_inches="tight")
        print(f"\n✓ Grafico salvato: gann_fan_live_low.png")
        plt.show()
        
    except Exception as e:
        print(f"\n❌ Errore nel calcolo: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test 2: Ventaglio da ultimo pivot high (CRYPTO-ADAPTED)
    print("\n" + "=" * 70)
    print("TEST 2: Ventaglio da Pivot High - PPB Statico vs Dinamico")
    print("=" * 70)
    
    try:
        fan = gann_fan(
            df,
            pivot_source="last_high",
            pivot_mode="atr",
            atr_len=14,
            atr_mult=1.0,
            atr_method="ema",
            use_dynamic_ppb=False,  # PPB statico per confronto
            base_divisor=1.5,
            ratios=[1/4, 1/2, 1, 2, 4],
            bars_forward=100
        )
        
        print(f"\n✓ Ventaglio calcolato!")
        print(f"  Pivot: indice {fan.pivot_idx}")
        print(f"  Prezzo pivot: {fan.pivot_price:.2f} EUR")
        print(f"  PPB: {fan.ppb:.4f}")
        print(f"  Linee generate: {len(fan.lines)}")
        print(f"  Direzione: {fan.lines[0].direction.upper()}")
        
        # Visualizza
        fig, ax = plt.subplots(figsize=(16, 9))
        plot_fan_with_date(df, fan, date_col="Date", ax=ax, show_labels=True)
        ax.set_title(
            f"Gann Fan BTC/EUR 15min - Pivot High (Crypto-Adapted)\n"
            f"Pivot @ {fan.pivot_price:.2f} EUR | PPB Statico: {fan.ppb:.2f}",
            fontsize=14,
            fontweight="bold"
        )
        plt.tight_layout()
        plt.savefig("gann_fan_live_high.png", dpi=150, bbox_inches="tight")
        print(f"\n✓ Grafico salvato: gann_fan_live_high.png")
        plt.show()
        
    except Exception as e:
        print(f"\n❌ Errore nel calcolo: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n" + "=" * 70)
    print("✅ Analisi completata con successo!")
    print("=" * 70)


if __name__ == "__main__":
    main()
