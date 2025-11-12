"""
Script di verifica dell'installazione del modulo Gann Fan.

Esegui questo script dopo l'installazione per verificare che tutto funzioni correttamente.
"""

import sys


def check_imports():
    """Verifica che tutti i moduli siano importabili."""
    print("Verifica imports...")
    
    try:
        import pandas
        print("✓ pandas installato")
    except ImportError:
        print("✗ pandas NON installato - esegui: pip install pandas")
        return False
    
    try:
        import numpy
        print("✓ numpy installato")
    except ImportError:
        print("✗ numpy NON installato - esegui: pip install numpy")
        return False
    
    try:
        import matplotlib
        print("✓ matplotlib installato")
    except ImportError:
        print("✗ matplotlib NON installato - esegui: pip install matplotlib")
        return False
    
    try:
        import gann_fan
        print("✓ gann_fan installato")
    except ImportError:
        print("✗ gann_fan NON installato - esegui: pip install -e .")
        return False
    
    return True


def check_api():
    """Verifica che le API principali siano disponibili."""
    print("\nVerifica API...")
    
    try:
        from gann_fan import atr, pivots_percent, pivots_atr, compute_ppb, gann_fan
        print("✓ Funzioni core disponibili")
    except ImportError as e:
        print(f"✗ Errore import funzioni core: {e}")
        return False
    
    try:
        from gann_fan.plot import plot_fan, plot_fan_with_date
        print("✓ Funzioni plot disponibili")
    except ImportError as e:
        print(f"✗ Errore import funzioni plot: {e}")
        return False
    
    try:
        from gann_fan import FanLine, FanResult
        print("✓ Strutture dati disponibili")
    except ImportError as e:
        print(f"✗ Errore import strutture dati: {e}")
        return False
    
    return True


def check_basic_functionality():
    """Verifica funzionalità base con dati minimali."""
    print("\nVerifica funzionalità base...")
    
    try:
        import pandas as pd
        import numpy as np
        from gann_fan.core import atr, gann_fan
        
        # Crea dati minimali
        df = pd.DataFrame({
            "High": [110, 115, 120, 125, 130, 125, 120, 115, 110, 115, 120, 125, 130, 135, 140],
            "Low": [100, 105, 110, 115, 120, 115, 110, 105, 100, 105, 110, 115, 120, 125, 130],
            "Close": [105, 110, 115, 120, 125, 120, 115, 110, 105, 110, 115, 120, 125, 130, 135],
        })
        
        # Test ATR
        atr_result = atr(df, length=5)
        assert not atr_result.isna().all(), "ATR completamente NaN"
        print("✓ ATR calcola correttamente")
        
        # Test gann_fan
        fan = gann_fan(
            df,
            pivot_source="custom",
            custom_pivot=(5, 120.0),
            ppb_mode="Fixed",
            fixed_ppb=1.0,
            ratios=[1, 2],
            bars_forward=5
        )
        
        assert fan.pivot_idx == 5
        assert fan.pivot_price == 120.0
        assert fan.ppb == 1.0
        assert len(fan.lines) == 2
        print("✓ gann_fan calcola correttamente")
        
        return True
        
    except Exception as e:
        print(f"✗ Errore nel test funzionalità: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Funzione principale."""
    print("=" * 60)
    print("Verifica installazione Gann Fan")
    print("=" * 60)
    print()
    
    success = True
    
    # Verifica imports
    if not check_imports():
        success = False
        print("\n⚠ Installa le dipendenze mancanti e riprova.")
    
    # Verifica API (solo se imports ok)
    if success and not check_api():
        success = False
    
    # Verifica funzionalità (solo se tutto ok finora)
    if success and not check_basic_functionality():
        success = False
    
    print()
    print("=" * 60)
    if success:
        print("✓ INSTALLAZIONE VERIFICATA CON SUCCESSO!")
        print("=" * 60)
        print()
        print("Prossimi passi:")
        print("  1. Esegui l'esempio: python example.py")
        print("  2. Esegui i test: pytest")
        print("  3. Consulta il README.md per la documentazione completa")
        return 0
    else:
        print("✗ INSTALLAZIONE INCOMPLETA O ERRORI")
        print("=" * 60)
        print()
        print("Risolvi gli errori sopra e riprova.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
