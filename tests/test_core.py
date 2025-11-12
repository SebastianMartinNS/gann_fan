"""
Test suite per il modulo core del ventaglio di Gann.

Verifica la correttezza matematica di tutte le funzioni principali:
- ATR con metodi SMA e Wilder
- Rilevamento pivot percentuale e ATR-based
- Calcolo Price Per Bar
- Costruzione completa del ventaglio
- Gestione errori ed edge cases
"""

import pytest
import numpy as np
import pandas as pd

from gann_fan.core import (
    atr,
    pivots_percent,
    pivots_atr,
    compute_ppb,
    gann_fan,
    FanLine,
    FanResult,
)


class TestATR:
    """Test per la funzione atr()."""
    
    def test_atr_sma_basic(self):
        """Verifica calcolo ATR con metodo SMA su dati semplici."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 118, 125],
            "Low": [100, 105, 110, 112, 115],
            "Close": [105, 110, 115, 115, 120],
        })
        
        result = atr(df, length=3, method="sma")
        
        # Primi 2 valori devono essere NaN
        assert np.isnan(result.iloc[0])
        assert np.isnan(result.iloc[1])
        
        # Dal terzo valore in poi deve essere calcolato
        assert not np.isnan(result.iloc[2])
        assert result.iloc[2] > 0
    
    def test_atr_wilder_basic(self):
        """Verifica calcolo ATR con metodo Wilder."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 118, 125],
            "Low": [100, 105, 110, 112, 115],
            "Close": [105, 110, 115, 115, 120],
        })
        
        result = atr(df, length=3, method="wilder")
        
        # Primi 2 valori devono essere NaN
        assert np.isnan(result.iloc[0])
        assert np.isnan(result.iloc[1])
        
        # Dal terzo valore in poi deve essere calcolato
        assert not np.isnan(result.iloc[2])
        assert result.iloc[2] > 0
    
    def test_atr_deterministic(self):
        """Verifica che ATR sia deterministico."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 118, 125, 130],
            "Low": [100, 105, 110, 112, 115, 120],
            "Close": [105, 110, 115, 115, 120, 125],
        })
        
        result1 = atr(df, length=3, method="sma")
        result2 = atr(df, length=3, method="sma")
        
        pd.testing.assert_series_equal(result1, result2)
    
    def test_atr_missing_columns(self):
        """Verifica errore con colonne mancanti."""
        df = pd.DataFrame({
            "High": [110, 115],
            "Low": [100, 105],
            # Manca Close
        })
        
        with pytest.raises(ValueError, match="Colonne mancanti"):
            atr(df)
    
    def test_atr_invalid_length(self):
        """Verifica errore con length non valido."""
        df = pd.DataFrame({
            "High": [110, 115],
            "Low": [100, 105],
            "Close": [105, 110],
        })
        
        with pytest.raises(ValueError, match="length deve essere >= 1"):
            atr(df, length=0)
    
    def test_atr_too_short(self):
        """Verifica errore con DataFrame troppo corto."""
        df = pd.DataFrame({
            "High": [110],
            "Low": [100],
            "Close": [105],
        })
        
        with pytest.raises(ValueError, match="troppo corto"):
            atr(df)


class TestPivotsPercent:
    """Test per la funzione pivots_percent()."""
    
    def test_simple_swing(self):
        """Verifica rilevamento pivot su swing semplice."""
        # Crea un pattern: down -> up -> down
        prices = [100, 90, 80, 90, 100, 90, 80]
        df = pd.DataFrame({
            "High": prices,
            "Low": prices,
            "Close": prices,
        })
        
        highs, lows = pivots_percent(df, threshold=0.1)
        
        # Deve rilevare almeno un low
        assert len(lows) > 0
        # Il low deve essere al punto più basso
        assert lows[0][1] == 80
    
    def test_no_pivots(self):
        """Verifica che con threshold alto non vengano rilevati pivot."""
        df = pd.DataFrame({
            "Close": [100, 101, 102, 103, 104],
            "High": [100, 101, 102, 103, 104],
            "Low": [100, 101, 102, 103, 104],
        })
        
        highs, lows = pivots_percent(df, threshold=0.5)
        
        assert len(highs) == 0
        assert len(lows) == 0
    
    def test_invalid_threshold(self):
        """Verifica errore con threshold non valido."""
        df = pd.DataFrame({
            "Close": [100, 101],
            "High": [100, 101],
            "Low": [100, 101],
        })
        
        with pytest.raises(ValueError, match="threshold deve essere > 0"):
            pivots_percent(df, threshold=0)


class TestPivotsATR:
    """Test per la funzione pivots_atr()."""
    
    def test_basic_detection(self):
        """Verifica rilevamento pivot con ATR."""
        # Crea swing con volatilità crescente
        df = pd.DataFrame({
            "High": [110, 115, 120, 125, 120, 115, 110],
            "Low": [100, 105, 110, 115, 110, 105, 100],
            "Close": [105, 110, 115, 120, 115, 110, 105],
        })
        
        highs, lows = pivots_atr(df, atr_len=3, atr_mult=0.5, method="sma")
        
        # Con parametri permissivi dovrebbe rilevare almeno un pivot
        assert len(highs) + len(lows) > 0
    
    def test_invalid_atr_mult(self):
        """Verifica errore con atr_mult non valido."""
        df = pd.DataFrame({
            "High": [110, 115],
            "Low": [100, 105],
            "Close": [105, 110],
        })
        
        with pytest.raises(ValueError, match="atr_mult deve essere > 0"):
            pivots_atr(df, atr_mult=0)


class TestComputePPB:
    """Test per la funzione compute_ppb()."""
    
    def test_fixed_mode(self):
        """Verifica calcolo ppb in modalità Fixed."""
        df = pd.DataFrame({
            "High": [110, 115],
            "Low": [100, 105],
            "Close": [105, 110],
        })
        
        ppb = compute_ppb(df, mode="Fixed", fixed_ppb=2.5)
        assert ppb == 2.5
    
    def test_atr_mode(self):
        """Verifica calcolo ppb in modalità ATR."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 125, 130],
            "Low": [100, 105, 110, 115, 120],
            "Close": [105, 110, 115, 120, 125],
        })
        
        ppb = compute_ppb(
            df,
            mode="ATR",
            atr_len=3,
            atr_method="sma",
            atr_divisor=2.0,
            pivot_idx=3
        )
        
        # ppb deve essere positivo e finito
        assert ppb > 0
        assert np.isfinite(ppb)
    
    def test_invalid_fixed_ppb(self):
        """Verifica errore con fixed_ppb non valido."""
        df = pd.DataFrame({
            "High": [110, 115],
            "Low": [100, 105],
            "Close": [105, 110],
        })
        
        with pytest.raises(ValueError, match="fixed_ppb deve essere > 0"):
            compute_ppb(df, mode="Fixed", fixed_ppb=0)
    
    def test_invalid_atr_divisor(self):
        """Verifica errore con atr_divisor non valido."""
        df = pd.DataFrame({
            "High": [110, 115],
            "Low": [100, 105],
            "Close": [105, 110],
        })
        
        with pytest.raises(ValueError, match="atr_divisor deve essere > 0"):
            compute_ppb(df, mode="ATR", atr_divisor=0, pivot_idx=0)


class TestGannFan:
    """Test per la funzione gann_fan()."""
    
    def test_basic_fan_creation(self):
        """Verifica creazione base del ventaglio."""
        # Crea dati con un chiaro low seguito da risalita
        prices = [100, 90, 80, 70, 80, 90, 100, 110]
        df = pd.DataFrame({
            "High": [p + 5 for p in prices],
            "Low": [p - 5 for p in prices],
            "Close": prices,
        })
        
        fan = gann_fan(
            df,
            pivot_source="last_low",
            pivot_mode="percent",
            threshold=0.1,
            ppb_mode="Fixed",
            fixed_ppb=1.0,
            ratios=[1, 2],
            bars_forward=3
        )
        
        # Verifica struttura risultato
        assert isinstance(fan, FanResult)
        assert fan.pivot_idx >= 0
        assert fan.pivot_price > 0
        assert fan.ppb > 0
        assert len(fan.lines) > 0
        
        # Verifica struttura linee
        for line in fan.lines:
            assert isinstance(line, FanLine)
            assert line.ratio > 0
            assert line.direction in ["up", "down"]
            assert line.start_idx == fan.pivot_idx
            assert line.y0 == fan.pivot_price
    
    def test_custom_pivot(self):
        """Verifica utilizzo di pivot custom."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 125],
            "Low": [100, 105, 110, 115],
            "Close": [105, 110, 115, 120],
        })
        
        fan = gann_fan(
            df,
            pivot_source="custom",
            custom_pivot=(1, 110.0),
            ppb_mode="Fixed",
            fixed_ppb=1.0,
            ratios=[1],
            bars_forward=2
        )
        
        assert fan.pivot_idx == 1
        assert fan.pivot_price == 110.0
    
    def test_missing_columns(self):
        """Verifica errore con colonne mancanti."""
        df = pd.DataFrame({
            "High": [110, 115],
            # Mancano Low e Close
        })
        
        with pytest.raises(ValueError, match="Colonne mancanti"):
            gann_fan(df)
    
    def test_invalid_bars_forward(self):
        """Verifica errore con bars_forward non valido."""
        df = pd.DataFrame({
            "High": [110, 115],
            "Low": [100, 105],
            "Close": [105, 110],
        })
        
        with pytest.raises(ValueError, match="bars_forward deve essere >= 1"):
            gann_fan(df, bars_forward=0)
    
    def test_no_pivots_found(self):
        """Verifica errore quando nessun pivot viene trovato."""
        # Dati monotoni senza swing
        df = pd.DataFrame({
            "High": [110, 111, 112, 113],
            "Low": [100, 101, 102, 103],
            "Close": [105, 106, 107, 108],
        })
        
        with pytest.raises(ValueError, match="Nessun pivot.*trovato"):
            gann_fan(
                df,
                pivot_source="last_low",
                pivot_mode="percent",
                threshold=0.5  # Threshold alto per non trovare pivot
            )
    
    def test_line_equations(self):
        """Verifica correttezza delle equazioni delle linee."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 125, 130],
            "Low": [100, 105, 110, 115, 120],
            "Close": [105, 110, 115, 120, 125],
        })
        
        fan = gann_fan(
            df,
            pivot_source="custom",
            custom_pivot=(1, 100.0),
            ppb_mode="Fixed",
            fixed_ppb=2.0,
            ratios=[1],
            bars_forward=3
        )
        
        # Trova la linea con ratio 1
        line = [l for l in fan.lines if l.ratio == 1][0]
        
        # Verifica equazione: y1 = y0 + ratio * ppb * (end_idx - start_idx)
        bars = line.end_idx - line.start_idx
        expected_y1 = line.y0 + line.ratio * fan.ppb * bars
        
        # Considera direzione
        if line.direction == "down":
            expected_y1 = line.y0 - line.ratio * fan.ppb * bars
        
        assert abs(line.y1 - expected_y1) < 1e-6
    
    def test_ratios_deduplication(self):
        """Verifica che i ratios duplicati vengano rimossi."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 125],
            "Low": [100, 105, 110, 115],
            "Close": [105, 110, 115, 120],
        })
        
        fan = gann_fan(
            df,
            pivot_source="custom",
            custom_pivot=(1, 110.0),
            ppb_mode="Fixed",
            fixed_ppb=1.0,
            ratios=[1, 1, 2, 2, 1],  # Duplicati
            bars_forward=2
        )
        
        # Deve avere solo 2 linee (1 e 2)
        assert len(fan.lines) == 2


class TestEdgeCases:
    """Test per edge cases e situazioni limite."""
    
    def test_very_short_dataframe(self):
        """Verifica gestione DataFrame molto corti."""
        df = pd.DataFrame({
            "High": [110],
            "Low": [100],
            "Close": [105],
        })
        
        with pytest.raises(ValueError, match="troppo corto"):
            gann_fan(df)
    
    def test_empty_ratios_list(self):
        """Verifica errore con lista ratios vuota."""
        df = pd.DataFrame({
            "High": [110, 115, 120],
            "Low": [100, 105, 110],
            "Close": [105, 110, 115],
        })
        
        with pytest.raises(ValueError, match="Lista ratios vuota"):
            gann_fan(
                df,
                pivot_source="custom",
                custom_pivot=(0, 105.0),
                ratios=[]
            )
    
    def test_pivot_at_end(self):
        """Verifica che pivot all'ultimo indice funzioni correttamente."""
        df = pd.DataFrame({
            "High": [110, 115, 120, 125],
            "Low": [100, 105, 110, 115],
            "Close": [105, 110, 115, 120],
        })
        
        fan = gann_fan(
            df,
            pivot_source="custom",
            custom_pivot=(3, 120.0),  # Ultimo indice
            ppb_mode="Fixed",
            fixed_ppb=1.0,
            ratios=[1],
            bars_forward=10
        )
        
        # end_idx dovrebbe essere limitato alla lunghezza del df
        for line in fan.lines:
            assert line.end_idx == 3  # Non può andare oltre


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
