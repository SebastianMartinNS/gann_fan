# Guida rapida all'installazione e utilizzo

## Installazione rapida

```bash
# Naviga nella directory del progetto
cd gann_fan

# Installa il pacchetto in modalità development
pip install -e .

# Oppure installa con dipendenze dev per i test
pip install -e ".[dev]"
```

## Test rapido

```bash
# Esegui l'esempio con dati sintetici
python example.py

# Esegui i test
pytest

# Esegui i test con coverage
pytest --cov=gann_fan --cov-report=html
```

## Utilizzo base

### Come libreria

```python
import pandas as pd
from gann_fan.core import gann_fan
from gann_fan.plot import plot_fan_with_date
import matplotlib.pyplot as plt

# Carica dati
df = pd.read_csv("data.csv", parse_dates=["Date"])
df = df.sort_values("Date").reset_index(drop=True)

# Calcola ventaglio
fan = gann_fan(df, pivot_source="last_low", bars_forward=200)

# Visualizza
plot_fan_with_date(df, fan, date_col="Date")
plt.show()
```

### Da CLI

```bash
python -m gann_fan.cli --csv data.csv --out gann.png
```

## Risoluzione problemi comuni

### Errore: "Import pandas could not be resolved"

Assicurati di aver installato le dipendenze:
```bash
pip install pandas numpy matplotlib
```

### Errore: "Nessun pivot trovato"

Prova a:
- Ridurre `threshold` (per pivot_mode="percent")
- Ridurre `atr_mult` (per pivot_mode="atr")
- Aumentare la lunghezza del DataFrame

### Errore: "ATR non disponibile"

Assicurati che:
- Il DataFrame abbia almeno `atr_len + 1` righe
- Il pivot non sia nelle prime `atr_len` righe

## Prossimi passi

Consulta il [README.md](README.md) per:
- Documentazione completa dell'API
- Spiegazione delle formule matematiche
- Esempi avanzati
- Lista completa parametri CLI
