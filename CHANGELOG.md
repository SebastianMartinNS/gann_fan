# Changelog

Tutte le modifiche notevoli a questo progetto saranno documentate in questo file.

Il formato è basato su [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
e questo progetto aderisce al [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-12

### Aggiunto
- Implementazione completa del modulo `gann_fan.core` con:
  - Funzione `atr()` per calcolo Average True Range (metodi SMA e Wilder)
  - Funzione `pivots_percent()` per rilevamento pivot percentuale
  - Funzione `pivots_atr()` per rilevamento pivot basato su ATR
  - Funzione `compute_ppb()` per calcolo Price Per Bar
  - Funzione `gann_fan()` per costruzione completa del ventaglio di Gann
- Modulo `gann_fan.plot` con:
  - Funzione `plot_fan()` per visualizzazione con indici numerici
  - Funzione `plot_fan_with_date()` per visualizzazione con date
- Interfaccia CLI completa in `gann_fan.cli` con tutti i parametri configurabili
- Test suite completa in `tests/test_core.py` con:
  - Test per ATR (SMA e Wilder)
  - Test per pivot detection (percent e ATR)
  - Test per calcolo ppb
  - Test per costruzione ventaglio
  - Test per edge cases e error handling
- Strutture dati `FanLine` e `FanResult` con dataclass
- Type hints completi su tutte le API pubbliche
- Docstring NumPy-style per tutte le funzioni
- Validazione rigorosa degli input con messaggi di errore informativi
- File di configurazione:
  - `pyproject.toml` per configurazione del progetto
  - `pytest.ini` per configurazione test
  - `.gitignore` per gestione repository
- Documentazione completa:
  - `README.md` con API, formule matematiche ed esempi
  - `QUICKSTART.md` per iniziare rapidamente
  - `INSTALL.md` con istruzioni dettagliate di installazione
  - `CHANGELOG.md` per tracciare le versioni
- Script di supporto:
  - `example.py` con dimostrazione pratica
  - `verify_install.py` per verificare l'installazione
- File di dipendenze:
  - `requirements.txt` per dipendenze runtime
  - `requirements-dev.txt` per dipendenze di sviluppo
- Licenza MIT

### Caratteristiche tecniche
- Python >= 3.9
- Dipendenze: pandas, numpy, matplotlib
- Ripetibilità garantita (calcoli deterministici)
- Formule matematicamente rigorose
- Gestione completa degli errori
- Test coverage elevato

### Note di rilascio
Prima versione stabile del modulo Gann Fan. Tutti i requisiti dell'Objective sono soddisfatti:
- ✅ Calcolo matematicamente corretto
- ✅ API pulita e ben documentata
- ✅ Test automatizzati completi
- ✅ CLI funzionante
- ✅ Ripetibilità e rigore matematico
- ✅ Qualità del codice (PEP8, type hints, docstrings)

## [Unreleased]

### Pianificato per versioni future
- Support multi-pivot per analisi di più ventagli simultanei
- Filtro regime ADX per disabilitare pivot in bassa volatilità
- Export in formato GeoJSON/JSON serializzabile
- Backtesting framework integrato
- Modalità streaming per aggiornamenti real-time
- Support per timeframe multipli
- Indicatori complementari (RSI, MACD, etc.)
- Interfaccia web/dashboard interattiva
- Performance optimization per dataset molto grandi
- Parallelizzazione calcoli con multiprocessing
