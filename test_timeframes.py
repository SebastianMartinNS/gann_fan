"""Test veloce con timeframe multipli."""

from test_coinbase import get_coinbase_candles
from gann_fan.core import gann_fan

print("\n" + "=" * 60)
print("TEST TIMEFRAME MULTIPLI - BTC/EUR")
print("=" * 60 + "\n")

timeframes = {
    '1 ora': 3600,
    '15 min': 900,
    '5 min': 300,
}

results = []

for name, seconds in timeframes.items():
    print(f"Scaricamento {name}...", end=" ")
    try:
        df = get_coinbase_candles('BTC-EUR', seconds, 300)
        
        fan = gann_fan(
            df,
            pivot_source='last_low',
            pivot_mode='atr',
            atr_len=14,
            atr_mult=1.5,
            ppb_mode='ATR',
            atr_divisor=2.0,
            bars_forward=50
        )
        
        results.append({
            'timeframe': name,
            'candles': len(df),
            'pivot_price': fan.pivot_price,
            'ppb': fan.ppb,
            'lines': len(fan.lines)
        })
        
        print(f"✓ OK")
        
    except Exception as e:
        print(f"✗ Errore: {e}")

print("\n" + "=" * 60)
print("RISULTATI")
print("=" * 60)
print(f"{'Timeframe':<10} {'Candele':<10} {'Pivot (EUR)':<15} {'PPB':<12} {'Linee'}")
print("-" * 60)

for r in results:
    print(f"{r['timeframe']:<10} {r['candles']:<10} {r['pivot_price']:>13.2f} {r['ppb']:>11.4f} {r['lines']:>6}")

print("\n✅ Test completato!")
