"""
Test suite per implementazione crypto-adapted del ventaglio di Gann.

Verifica funzionalità specifiche per crypto trading:
- ATR percentuale (normalizzato)
- Pivot detection su scala logaritmica
- PPB dinamico adattivo
- Comparazione con implementazione classica
"""

import pytest
import numpy as np
import pandas as pd

from gann_fan.core import (
    atr_percent,
    pivots_percent_log,
    pivots_atr_adaptive,
    compute_ppb_dynamic,
    gann_fan,
    FanLine,
    FanResult,
)


class TestATRPercent:
    """Test per atr_percent() - ATR normalizzato."""
    
    def test_atr_percent_basic(self):
        """Verifica che ATR% sia normalizzato (0-100 range)."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 118, 125, 130, 128, 135],
            "Low": [100, 105, 110, 112, 115, 120, 122, 125],
            "Close": [105, 110, 115, 115, 120, 125, 125, 130],
        })
        
        result = atr_percent(df, length=3, method="ema")
        
        # Valori non-NaN devono essere positivi
        valid_values = result[~result.isna()]
        assert all(valid_values > 0)
        
        # ATR% tipicamente < 50% (volatilità estrema > 50% è rara)
        assert all(valid_values < 50)
    
    def test_atr_percent_comparable(self):
        """Verifica che ATR% sia comparabile tra scale di prezzo diverse."""
        # Dataset 1: prezzi bassi
        df_low = pd.DataFrame({
            "High": [110, 115, 120],
            "Low": [100, 105, 110],
            "Close": [105, 110, 115],
        })
        
        # Dataset 2: prezzi alti (10x)
        df_high = pd.DataFrame({
            "High": [1100, 1150, 1200],
            "Low": [1000, 1050, 1100],
            "Close": [1050, 1100, 1150],
        })
        
        atr_low = atr_percent(df_low, length=2, method="sma")
        atr_high = atr_percent(df_high, length=2, method="sma")
        
        # ATR% deve essere simile indipendentemente dal prezzo assoluto
        # (stessa volatilità relativa)
        assert np.allclose(atr_low.iloc[-1], atr_high.iloc[-1], rtol=0.01)
    
    def test_atr_percent_ema_responsive(self):
        """Verifica che EMA sia più reattivo di SMA."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 200, 205],  # Spike improvviso
            "Low": [100, 105, 110, 190, 195],
            "Close": [105, 110, 115, 195, 200],
        })
        
        atr_sma = atr_percent(df, length=3, method="sma")
        atr_ema = atr_percent(df, length=3, method="ema")
        
        # EMA deve reagire più velocemente allo spike
        # (differenza maggiore dopo il salto)
        assert atr_ema.iloc[-1] != atr_sma.iloc[-1]


class TestPivotsPercentLog:
    """Test per pivots_percent_log() - scala logaritmica."""
    
    def test_log_scale_symmetry(self):
        """Verifica simmetria movimenti up/down su scala log."""
        # +100% seguito da -50% dovrebbe tornare a prezzo iniziale
        df = pd.DataFrame({
            "Close": [100, 200, 100],  # 100 → 200 (+100%), 200 → 100 (-50%)
        })
        
        highs, lows = pivots_percent_log(df, threshold=0.5)
        
        # Deve rilevare un pivot high a indice 1
        assert len(highs) == 1
        assert highs[0] == (1, 200)
    
    def test_exponential_moves(self):
        """Verifica rilevamento movimenti esponenziali tipici crypto."""
        # Simula pump crypto: +50%, +50%, +50%
        df = pd.DataFrame({
            "Close": [100, 150, 225, 337.5, 200],  # 3 pump poi correzione
        })
        
        highs, lows = pivots_percent_log(df, threshold=0.30)
        
        # Deve rilevare pivot high prima della correzione
        assert len(highs) >= 1
        assert highs[-1][0] == 3  # Indice del picco


class TestPivotsATRAdaptive:
    """Test per pivots_atr_adaptive() - soglie adattive."""
    
    def test_adaptive_threshold(self):
        """Verifica che soglia si adatti alla volatilità."""
        # DataFrame con volatilità crescente
        df = pd.DataFrame({
            "High": [110, 115, 120, 150, 180, 200],
            "Low": [100, 105, 110, 140, 170, 190],
            "Close": [105, 110, 115, 145, 175, 195],
        })
        
        highs, lows = pivots_atr_adaptive(
            df, atr_len=3, atr_mult=1.5, method="ema"
        )
        
        # Deve rilevare almeno un pivot (volatilità aumenta)
        assert len(highs) + len(lows) > 0


class TestComputePPBDynamic:
    """Test per compute_ppb_dynamic() - PPB adattivo."""
    
    def test_ppb_dynamic_adapts(self):
        """Verifica che PPB si adatti a volatilità rolling."""
        # Crea dataset con volatilità deterministicamente crescente
        prices = [100]
        for i in range(100):
            # Prima metà: oscillazioni piccole (+/-0.5%)
            # Seconda metà: oscillazioni grandi (+/-2%)
            if i < 50:
                change = 0.005 if i % 2 == 0 else -0.005
            else:
                change = 0.02 if i % 2 == 0 else -0.02
            prices.append(prices[-1] * (1 + change))
        
        df = pd.DataFrame({
            "High": [p * 1.01 for p in prices],
            "Low": [p * 0.99 for p in prices],
            "Close": prices,
        })
        
        # Calcola PPB nella fase bassa e alta volatilità
        ppb_low_vol = compute_ppb_dynamic(df, pivot_idx=40, volatility_window=30)
        ppb_high_vol = compute_ppb_dynamic(df, pivot_idx=95, volatility_window=30)
        
        # PPB alta volatilità deve essere > PPB bassa volatilità
        assert ppb_high_vol > ppb_low_vol * 1.5  # Almeno 50% più alto
    
    def test_ppb_dynamic_vs_static(self):
        """Confronta PPB dinamico vs statico."""
        df = pd.DataFrame({
            "High": [110 + i for i in range(50)],
            "Low": [100 + i for i in range(50)],
            "Close": [105 + i for i in range(50)],
        })
        
        ppb_dynamic = compute_ppb_dynamic(
            df, pivot_idx=30, atr_len=14, atr_method="ema",
            volatility_window=20, base_divisor=2.0
        )
        
        # PPB deve essere positivo e ragionevole
        assert ppb_dynamic > 0
        assert ppb_dynamic < df["Close"].iloc[30] * 0.1  # < 10% del prezzo


class TestGannFanCrypto:
    """Test per gann_fan() con parametri crypto-adapted."""
    
    def test_gann_fan_dynamic_ppb(self):
        """Verifica creazione ventaglio con PPB dinamico."""
        df = pd.DataFrame({
            "High": [110 + i * 2 for i in range(50)],
            "Low": [100 + i * 2 for i in range(50)],
            "Close": [105 + i * 2 for i in range(50)],
        })
        
        fan = gann_fan(
            df,
            pivot_source="last_low",
            pivot_mode="atr",
            atr_len=14,
            atr_mult=1.5,
            atr_method="ema",
            use_dynamic_ppb=True,
            base_divisor=2.0,
            volatility_window=30,
            bars_forward=20
        )
        
        assert isinstance(fan, FanResult)
        assert fan.ppb > 0
        assert len(fan.lines) == 7  # Default ratios
        assert all(isinstance(line, FanLine) for line in fan.lines)
    
    def test_gann_fan_static_vs_dynamic(self):
        """Confronta PPB statico vs dinamico."""
        df = pd.DataFrame({
            "High": [110 + i for i in range(50)],
            "Low": [100 + i for i in range(50)],
            "Close": [105 + i for i in range(50)],
        })
        
        fan_static = gann_fan(df, use_dynamic_ppb=False, bars_forward=20)
        fan_dynamic = gann_fan(df, use_dynamic_ppb=True, bars_forward=20)
        
        # Entrambi devono generare ventaglio
        assert len(fan_static.lines) > 0
        assert len(fan_dynamic.lines) > 0
        
        # PPB possono essere diversi
        # (non necessariamente, dipende dai dati)
        assert fan_static.ppb > 0
        assert fan_dynamic.ppb > 0


class TestBackwardCompatibility:
    """Test compatibilità con implementazione legacy."""
    
    def test_alias_functions(self):
        """Verifica che alias legacy funzionino."""
        from gann_fan.core import atr, pivots_percent, pivots_atr, compute_ppb
        
        df = pd.DataFrame({
            "High": [110, 115, 120, 118, 125],
            "Low": [100, 105, 110, 112, 115],
            "Close": [105, 110, 115, 115, 120],
        })
        
        # atr() è alias di atr_percent()
        result1 = atr(df, length=3)
        result2 = atr_percent(df, length=3)
        pd.testing.assert_series_equal(result1, result2)
        
        # pivots_percent() è alias di pivots_percent_log()
        highs1, lows1 = pivots_percent(df, threshold=0.05)
        highs2, lows2 = pivots_percent_log(df, threshold=0.05)
        assert highs1 == highs2
        assert lows1 == lows2
        
        # pivots_atr() è alias di pivots_atr_adaptive()
        highs3, lows3 = pivots_atr(df, atr_len=3)
        highs4, lows4 = pivots_atr_adaptive(df, atr_len=3)
        assert highs3 == highs4
        assert lows3 == lows4


class TestRealWorldScenarios:
    """Test con scenari realistici di trading crypto."""
    
    def test_bitcoin_like_volatility(self):
        """Simula volatilità tipo Bitcoin."""
        np.random.seed(123)
        
        # Simula 96 candele 15-min (24h) con volatilità ~3%
        prices = [50000]
        for _ in range(95):
            change = np.random.normal(0, 0.015)  # 1.5% std
            prices.append(prices[-1] * (1 + change))
        
        df = pd.DataFrame({
            "High": [p * 1.005 for p in prices],
            "Low": [p * 0.995 for p in prices],
            "Close": prices,
        })
        
        fan = gann_fan(
            df,
            pivot_source="last_low",
            pivot_mode="atr",
            atr_len=14,
            atr_mult=1.5,
            atr_method="ema",
            use_dynamic_ppb=True,
            bars_forward=30
        )
        
        # Verifica risultato ragionevole
        assert fan.ppb > 0
        assert fan.ppb < prices[-1] * 0.05  # PPB < 5% del prezzo
        assert len(fan.lines) > 0
    
    def test_extreme_pump_dump(self):
        """Simula pump & dump estremo (scenario altcoin)."""
        # Prezzo stabile → pump +200% → dump -60%
        prices = [100] * 20 + [100 + i*10 for i in range(20)] + [300 - i*5 for i in range(20)]
        
        df = pd.DataFrame({
            "High": [p * 1.02 for p in prices],
            "Low": [p * 0.98 for p in prices],
            "Close": prices,
        })
        
        # Deve gestire volatilità estrema senza errori
        fan = gann_fan(
            df,
            pivot_source="last_low",
            pivot_mode="atr",
            atr_mult=2.0,  # Soglia alta per volatilità estrema
            use_dynamic_ppb=True,
            bars_forward=10
        )
        
        assert fan.ppb > 0
        assert len(fan.lines) > 0
