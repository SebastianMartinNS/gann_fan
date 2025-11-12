# Guida all'installazione completa

## Prerequisiti

- Python >= 3.9
- pip (package manager Python)
- Git (opzionale, per clonare il repository)

## Metodo 1: Installazione completa (consigliato)

### Passo 1: Clona o scarica il progetto

```bash
# Con Git
git clone <repository-url>
cd gann_fan

# Oppure scarica e estrai il file ZIP
```

### Passo 2: Crea un ambiente virtuale (opzionale ma consigliato)

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Passo 3: Installa le dipendenze

```bash
# Dipendenze principali
pip install -r requirements.txt

# Oppure con dipendenze di sviluppo
pip install -r requirements-dev.txt
```

### Passo 4: Installa il pacchetto in modalità development

```bash
pip install -e .
```

Questo permette di modificare il codice e vedere immediatamente le modifiche senza reinstallare.

### Passo 5: Verifica l'installazione

```bash
python verify_install.py
```

Se tutto è OK, dovresti vedere:
```
✓ INSTALLAZIONE VERIFICATA CON SUCCESSO!
```

## Metodo 2: Installazione solo dipendenze

Se vuoi solo usare il modulo senza installarlo come pacchetto:

```bash
pip install pandas numpy matplotlib
```

Poi puoi importare direttamente dalle cartelle:
```python
import sys
sys.path.insert(0, '/path/to/gann_fan')
from gann_fan.core import gann_fan
```

## Metodo 3: Installazione da pyproject.toml

```bash
# Solo dipendenze runtime
pip install .

# Con dipendenze di sviluppo
pip install ".[dev]"
```

## Test dell'installazione

### 1. Test con dati sintetici

```bash
python example.py
```

Questo genererà un file `gann_fan_example.png` e aprirà una finestra con i grafici.

### 2. Test unitari

```bash
pytest
```

Output atteso:
```
============================= test session starts ==============================
...
collected XX items

tests/test_core.py::TestATR::test_atr_sma_basic PASSED
tests/test_core.py::TestATR::test_atr_wilder_basic PASSED
...
============================== XX passed in X.XXs ===============================
```

### 3. Test con coverage

```bash
pytest --cov=gann_fan --cov-report=html
```

Poi apri `htmlcov/index.html` nel browser per vedere il report di copertura.

### 4. Test CLI

```bash
# Crea un CSV di test
python -c "
import pandas as pd
import numpy as np
df = pd.DataFrame({
    'Date': pd.date_range('2024-01-01', periods=100, freq='H'),
    'High': np.random.uniform(41000, 42000, 100),
    'Low': np.random.uniform(39000, 40000, 100),
    'Close': np.random.uniform(39500, 41500, 100),
})
df.to_csv('test_data.csv', index=False)
"

# Esegui CLI
python -m gann_fan.cli --csv test_data.csv --out test_output.png
```

## Risoluzione problemi

### Errore: "pandas could not be resolved"

**Causa:** Dipendenze non installate

**Soluzione:**
```bash
pip install pandas numpy matplotlib
```

### Errore: "No module named 'gann_fan'"

**Causa:** Pacchetto non installato

**Soluzione:**
```bash
pip install -e .
```

### Errore: "pytest: command not found"

**Causa:** pytest non installato

**Soluzione:**
```bash
pip install pytest pytest-cov
```

### Errore Python non trovato

**Windows:**
- Assicurati che Python sia nel PATH
- Prova a usare `py` invece di `python`

**Linux/macOS:**
- Usa `python3` invece di `python`

### Errore permessi (Windows)

**Causa:** PowerShell ExecutionPolicy

**Soluzione:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Errore permessi (Linux/macOS)

**Causa:** Permessi insufficienti

**Soluzione:**
```bash
# NON usare sudo con pip
# Usa invece un ambiente virtuale
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Disinstallazione

```bash
# Disinstalla il pacchetto
pip uninstall gann-fan

# Rimuovi l'ambiente virtuale
deactivate  # Esci dall'ambiente
rm -rf venv  # Linux/macOS
rmdir /s venv  # Windows
```

## Aggiornamento

```bash
# Aggiorna le dipendenze
pip install --upgrade -r requirements.txt

# Reinstalla il pacchetto
pip install -e . --force-reinstall
```

## Supporto

Per problemi o domande:

1. Verifica che tutti i prerequisiti siano installati
2. Esegui `python verify_install.py` per diagnosticare problemi
3. Controlla i log di errore completi
4. Consulta il README.md per esempi e documentazione

## Prossimi passi

Dopo l'installazione:

1. Leggi il [README.md](README.md) per la documentazione completa
2. Consulta il [QUICKSTART.md](QUICKSTART.md) per iniziare rapidamente
3. Esplora `example.py` per vedere casi d'uso pratici
4. Esegui i test con `pytest` per verificare il comportamento
