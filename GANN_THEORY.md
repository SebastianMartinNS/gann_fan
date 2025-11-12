# Teoria del Ventaglio di Gann - Documentazione Matematica Completa

## Indice
1. [Introduzione](#introduzione)
2. [Fondamenti Teorici](#fondamenti-teorici)
3. [Parametri e Formule](#parametri-e-formule)
4. [Calcoli Matematici](#calcoli-matematici)
5. [Interpretazione](#interpretazione)
6. [Esempi Pratici](#esempi-pratici)

---

## Introduzione

Il **Ventaglio di Gann** (Gann Fan) è uno strumento di analisi tecnica sviluppato da W.D. Gann basato sulla relazione tra tempo e prezzo. Il concetto fondamentale è che i mercati si muovono in angoli geometrici prevedibili, con l'angolo 1x1 (45°) che rappresenta l'equilibrio perfetto tra tempo e prezzo.

### Principi Fondamentali
- **Tempo = Prezzo**: Una unità di tempo corrisponde a una unità di prezzo
- **Angoli Geometrici**: Il mercato rispetta angoli specifici (1x8, 1x4, 1x2, 1x1, 2x1, 4x1, 8x1)
- **Supporti/Resistenze Dinamici**: Le linee del ventaglio fungono da zone di supporto (direzione up) o resistenza (direzione down)

---

## Fondamenti Teorici

### Pivot Points (Punti di Inversione)

Un **pivot** è un punto sul grafico dove il prezzo inverte la direzione. Esistono:
- **Pivot Low**: Minimo locale (il prezzo scende, poi risale)
- **Pivot High**: Massimo locale (il prezzo sale, poi scende)

#### Rilevamento Pivot - Metodo Percentuale
Un pivot viene riconosciuto quando il prezzo si muove di una percentuale `θ` rispetto al candidato pivot.

**Formula Pivot Low:**
```
Se P_t - P_candidate >= θ × P_candidate
  → P_candidate è un Pivot Low
```

**Formula Pivot High:**
```
Se P_candidate - P_t >= θ × P_candidate
  → P_candidate è un Pivot High
```

**Parametri:**
- `θ` (threshold): Soglia percentuale (es. 0.05 = 5%)
- `P_t`: Prezzo corrente
- `P_candidate`: Prezzo candidato pivot

**Esempio:**
```
Candidato pivot low = 89,000 EUR
Threshold = 5% (0.05)
Prezzo successivo = 93,500 EUR

Variazione = (93,500 - 89,000) / 89,000 = 0.0506 = 5.06%
5.06% >= 5% → PIVOT CONFERMATO
```

#### Rilevamento Pivot - Metodo ATR

Usa l'**Average True Range** come soglia dinamica invece di una percentuale fissa.

**Formula:**
```
Pivot Low: Se P_t - P_candidate >= ATR_t × k
Pivot High: Se P_candidate - P_t >= ATR_t × k
```

**Parametri:**
- `k` (atr_mult): Moltiplicatore ATR (es. 1.5)
- `ATR_t`: Average True Range al tempo t

**Vantaggi:** Si adatta alla volatilità del mercato.

---

### Average True Range (ATR)

L'**ATR** misura la volatilità del mercato considerando i gap tra sessioni.

#### True Range (TR)

**Formula:**
```
TR_t = max(
    High_t - Low_t,           # Range barra corrente
    |High_t - Close_{t-1}|,   # Gap up
    |Low_t - Close_{t-1}|     # Gap down
)
```

**Spiegazione:**
- Considera il massimo tra 3 valori
- Include gap tra chiusura precedente e prezzi correnti
- Cattura la vera escursione di prezzo

**Esempio:**
```
Barra corrente:  High=90,500, Low=89,800, Close=90,200
Barra precedente: Close=89,500

Calcolo:
1. High - Low = 90,500 - 89,800 = 700
2. |High - Close_prev| = |90,500 - 89,500| = 1,000  ← Massimo
3. |Low - Close_prev| = |89,800 - 89,500| = 300

TR = 1,000 EUR
```

#### ATR - Metodo SMA

**Formula:**
```
ATR_t = (1/n) × Σ(TR_i) per i da (t-n+1) a t
```

**Parametri:**
- `n` (atr_len): Periodo di calcolo (tipicamente 14)
- `TR_i`: True Range alla barra i

**Esempio (n=3):**
```
TR_1 = 800
TR_2 = 950
TR_3 = 1,000

ATR_3 = (800 + 950 + 1,000) / 3 = 916.67 EUR
```

#### ATR - Metodo Wilder

**Formula ricorsiva:**
```
ATR_t = ATR_{t-1} + (1/n) × (TR_t - ATR_{t-1})
```

Equivalente a:
```
ATR_t = ((n-1) × ATR_{t-1} + TR_t) / n
```

**Parametri:**
- `n`: Periodo (tipicamente 14)
- `ATR_{t-1}`: ATR precedente

**Caratteristiche:**
- Smoothing esponenziale (simile a EMA con α = 1/n)
- Meno reattivo ai cambiamenti recenti
- Calcolo più smooth del SMA

**Esempio (n=14, ATR precedente = 900):**
```
TR_corrente = 1,000

ATR_nuovo = 900 + (1/14) × (1,000 - 900)
         = 900 + 0.0714 × 100
         = 900 + 7.14
         = 907.14 EUR
```

---

### Price Per Bar (PPB)

Il **PPB** definisce quanto prezzo corrisponde a una unità di tempo (una barra/candela).

#### PPB - Modalità ATR

**Formula:**
```
PPB = ATR_{pivot} / divisor
```

**Parametri:**
- `ATR_{pivot}`: ATR calcolato all'indice del pivot
- `divisor` (atr_divisor): Divisore per scala (tipicamente 1.0 - 3.0)

**Significato:**
- PPB alto = linee ripide = mercato volatile
- PPB basso = linee piatte = mercato calmo

**Esempio:**
```
ATR al pivot = 162.63 EUR
Divisor = 2.0

PPB = 162.63 / 2.0 = 81.31 EUR/barra
```

Significa: ogni barra (15 min) corrisponde a 81.31 EUR di movimento.

#### PPB - Modalità Fixed

**Formula:**
```
PPB = valore_fisso
```

**Uso:** Quando si vuole un PPB costante indipendente dalla volatilità.

---

### Ratios di Gann

I **ratios** definiscono gli angoli del ventaglio rispetto all'angolo base 1x1 (45°).

#### Ratios Classici di Gann

| Ratio | Nome | Angolo | Significato |
|-------|------|--------|-------------|
| 1/8   | 1x8  | 7.13°  | Supporto/resistenza molto debole |
| 1/4   | 1x4  | 14.04° | Supporto/resistenza debole |
| 1/3   | 1x3  | 18.43° | Supporto/resistenza moderato-debole |
| 1/2   | 1x2  | 26.57° | Supporto/resistenza moderato |
| 1     | 1x1  | 45.00° | **Equilibrio perfetto** (più importante) |
| 2     | 2x1  | 63.43° | Supporto/resistenza forte |
| 3     | 3x1  | 71.57° | Supporto/resistenza molto forte |
| 4     | 4x1  | 75.96° | Supporto/resistenza estremamente forte |
| 8     | 8x1  | 82.87° | Supporto/resistenza quasi verticale |

#### Calcolo Angolo

**Formula:**
```
θ = arctan(ratio × PPB / time_unit)
```

Per timeframe costante (1 barra = 1 unità):
```
θ = arctan(ratio)
```

**Esempio:**
```
Ratio = 1 (angolo 1x1)
θ = arctan(1) = 45°

Ratio = 2 (angolo 2x1)
θ = arctan(2) = 63.43°
```

---

## Calcoli Matematici

### Costruzione Linee del Ventaglio

Ogni linea del ventaglio segue l'equazione:

**Formula Generale:**
```
P(t) = P_0 ± r × ppb × (t - t_0)
```

**Parametri:**
- `P(t)`: Prezzo al tempo t
- `P_0`: Prezzo del pivot
- `r`: Ratio della linea (es. 1, 2, 4, 8)
- `ppb`: Price Per Bar
- `t`: Indice temporale (barra)
- `t_0`: Indice del pivot
- `±`: Segno dipende dalla direzione (+ per up, - per down)

#### Direzione UP (Pivot Low)

**Formula:**
```
P(t) = P_0 + r × ppb × (t - t_0)
```

**Esempio:**
```
Pivot: P_0 = 89,036.49 EUR, t_0 = 68
PPB = 81.31 EUR/barra
Ratio r = 2

Per t = 78 (10 barre dopo il pivot):
P(78) = 89,036.49 + 2 × 81.31 × (78 - 68)
      = 89,036.49 + 2 × 81.31 × 10
      = 89,036.49 + 1,626.20
      = 90,662.69 EUR
```

#### Direzione DOWN (Pivot High)

**Formula:**
```
P(t) = P_0 - r × ppb × (t - t_0)
```

**Esempio:**
```
Pivot: P_0 = 92,427.40 EUR, t_0 = 85
PPB = 260.17 EUR/barra
Ratio r = 1

Per t = 95 (10 barre dopo il pivot):
P(95) = 92,427.40 - 1 × 260.17 × (95 - 85)
      = 92,427.40 - 260.17 × 10
      = 92,427.40 - 2,601.70
      = 89,825.70 EUR
```

### Proiezione Forward

**Formula:**
```
end_idx = min(pivot_idx + bars_forward, len(df) - 1)
```

**Parametri:**
- `bars_forward`: Numero di barre da proiettare in avanti
- `len(df)`: Lunghezza totale del dataset

**Vincolo:** La proiezione non può superare la fine dei dati disponibili.

---

## Parametri del Modulo

### Parametri di Input

#### `pivot_source`
**Tipo:** `str`  
**Valori:** `"last_low"`, `"last_high"`, `"custom"`  
**Default:** `"last_low"`  
**Descrizione:** Fonte del pivot da cui costruire il ventaglio.

#### `pivot_mode`
**Tipo:** `str`  
**Valori:** `"atr"`, `"percent"`  
**Default:** `"atr"`  
**Descrizione:** Metodo di rilevamento pivot automatico.
- `"atr"`: Usa ATR come soglia dinamica
- `"percent"`: Usa soglia percentuale fissa

#### `threshold`
**Tipo:** `float`  
**Range:** `(0, 1]` tipicamente `0.01 - 0.10`  
**Default:** `0.05` (5%)  
**Descrizione:** Soglia percentuale per `pivot_mode="percent"`.  
**Uso:** Solo quando `pivot_mode="percent"`.

#### `atr_len`
**Tipo:** `int`  
**Range:** `≥ 2`, tipicamente `14`  
**Default:** `14`  
**Descrizione:** Periodo per calcolo ATR.  
**Nota:** Valori comuni: 7 (corto), 14 (standard), 21 (lungo).

#### `atr_mult`
**Tipo:** `float`  
**Range:** `> 0`, tipicamente `0.5 - 3.0`  
**Default:** `1.0`  
**Descrizione:** Moltiplicatore ATR per rilevamento pivot.  
**Uso:** Solo quando `pivot_mode="atr"`.
- Valori bassi (0.5-1.0): Più pivot rilevati
- Valori alti (2.0-3.0): Meno pivot, più significativi

#### `atr_method`
**Tipo:** `str`  
**Valori:** `"sma"`, `"wilder"`  
**Default:** `"sma"`  
**Descrizione:** Metodo di calcolo ATR.
- `"sma"`: Media mobile semplice
- `"wilder"`: Smoothing di Wilder (più smooth)

#### `ppb_mode`
**Tipo:** `str`  
**Valori:** `"ATR"`, `"Fixed"`  
**Default:** `"ATR"`  
**Descrizione:** Modalità calcolo Price Per Bar.
- `"ATR"`: PPB basato su ATR (dinamico)
- `"Fixed"`: PPB fisso (costante)

#### `atr_divisor`
**Tipo:** `float`  
**Range:** `> 0`, tipicamente `1.0 - 3.0`  
**Default:** `1.0`  
**Descrizione:** Divisore per calcolo PPB da ATR.  
**Uso:** Solo quando `ppb_mode="ATR"`.
- Valori bassi (1.0): Linee ripide
- Valori alti (3.0): Linee piatte

#### `fixed_ppb`
**Tipo:** `float`  
**Range:** `> 0`  
**Default:** `1.0`  
**Descrizione:** Valore PPB fisso.  
**Uso:** Solo quando `ppb_mode="Fixed"`.

#### `ratios`
**Tipo:** `List[float]`  
**Default:** `[1/8, 1/4, 1/3, 1/2, 1, 2, 3, 4, 8]`  
**Descrizione:** Lista dei ratios per le linee del ventaglio.  
**Nota:** Ratios duplicati vengono rimossi automaticamente.

#### `bars_forward`
**Tipo:** `int`  
**Range:** `> 0`, tipicamente `50 - 500`  
**Default:** `100`  
**Descrizione:** Numero di barre da proiettare in avanti dal pivot.

#### `custom_pivot`
**Tipo:** `Optional[Tuple[int, float]]`  
**Default:** `None`  
**Descrizione:** Pivot personalizzato `(indice, prezzo)`.  
**Uso:** Solo quando `pivot_source="custom"`.

---

## Interpretazione

### Direzione UP (da Pivot Low)

**Significato:** Il ventaglio parte da un minimo e proietta linee verso l'alto.

**Interpretazione linee:**
- **Linee = Supporti Dinamici**: Il prezzo dovrebbe rimbalzare su queste linee
- **Rottura al ribasso**: Se il prezzo rompe sotto una linea, cerca supporto sulla linea inferiore
- **Ratio più alti (4x1, 8x1)**: Supporti più forti e ripidi
- **Ratio più bassi (1x4, 1x8)**: Supporti più deboli e piatti

**Trading:**
```
Se prezzo > linea 1x1 (45°) → Trend rialzista forte
Se prezzo tra 1x2 e 1x1 → Trend rialzista moderato
Se prezzo < linea 1x2 → Trend rialzista debole o inversione
```

### Direzione DOWN (da Pivot High)

**Significato:** Il ventaglio parte da un massimo e proietta linee verso il basso.

**Interpretazione linee:**
- **Linee = Resistenze Dinamiche**: Il prezzo dovrebbe essere respinto da queste linee
- **Rottura al rialzo**: Se il prezzo supera una linea, cerca resistenza sulla linea superiore
- **Ratio più alti (4x1, 8x1)**: Resistenze più forti
- **Ratio più bassi (1x4, 1x8)**: Resistenze più deboli

**Trading:**
```
Se prezzo < linea 1x1 (45°) → Trend ribassista forte
Se prezzo tra 1x1 e 1x2 → Trend ribassista moderato
Se prezzo > linea 1x2 → Trend ribassista debole o inversione
```

### Confluenze

Quando più linee da ventagli diversi si incrociano nello stesso punto:
- **Zona di confluenza**: Area di forte supporto/resistenza
- **Probabilità alta di reazione**: Il prezzo tende a reagire in queste zone
- **Uso:** Identificare target price o stop loss

---

## Esempi Pratici

### Esempio 1: Ventaglio da Last Low (24h BTC/EUR)

**Dati:**
```python
from gann_fan import get_coinbase_candles, gann_fan

df = get_coinbase_candles("BTC-EUR", granularity=900, num_candles=96)
fan = gann_fan(
    df,
    pivot_source="last_low",
    pivot_mode="atr",
    atr_len=14,
    atr_mult=1.5,
    atr_method="sma",
    ppb_mode="ATR",
    atr_divisor=2.0,
    ratios=[1/8, 1/4, 1/2, 1, 2, 4, 8],
    bars_forward=50
)
```

**Output:**
```
Pivot: indice 68, prezzo 89,036.49 EUR
PPB: 81.31 EUR/barra
Linee: 7 (ratios 1/8, 1/4, 1/2, 1, 2, 4, 8)
Direzione: UP
```

**Calcolo Linea 1x1 (45°) a t=78:**
```
P(78) = 89,036.49 + 1 × 81.31 × (78 - 68)
      = 89,036.49 + 813.10
      = 89,849.59 EUR
```

**Interpretazione:**
- Il prezzo rimbalza dal minimo a 89,036.49 EUR
- Linea 1x1 a 89,849.59 EUR rappresenta equilibrio trend rialzista
- Se prezzo > 89,849.59 → trend forte
- Linea 2x1 a 90,662.69 EUR è resistenza forte successiva

### Esempio 2: Confronto PPB Multipli

**Scenario:** Stesso pivot, tre ventagli con PPB diversi.

**Setup:**
```python
pivot_idx, pivot_price = 68, 89036.49

# Narrow (linee ripide)
fan_narrow = gann_fan(df, pivot_source="custom", 
                      custom_pivot=(pivot_idx, pivot_price),
                      ppb_mode="ATR", atr_divisor=3.0, ratios=[1, 2])

# Medium (standard)
fan_medium = gann_fan(df, pivot_source="custom",
                      custom_pivot=(pivot_idx, pivot_price),
                      ppb_mode="ATR", atr_divisor=2.0, ratios=[1, 2])

# Wide (linee piatte)
fan_wide = gann_fan(df, pivot_source="custom",
                    custom_pivot=(pivot_idx, pivot_price),
                    ppb_mode="ATR", atr_divisor=1.0, ratios=[1, 2])
```

**Output:**
```
PPB narrow: 54.21 EUR/barra  (ATR/3)
PPB medium: 81.31 EUR/barra  (ATR/2)
PPB wide: 162.63 EUR/barra   (ATR/1)
```

**Interpretazione:**
- **Narrow**: Proiezione conservativa (mercato lento)
- **Medium**: Proiezione standard (velocità normale)
- **Wide**: Proiezione aggressiva (mercato veloce)

**Uso:** Identificare zone dove le linee convergono = target price critici.

### Esempio 3: Calcolo Manuale Completo

**Dati iniziali:**
```
Serie prezzi: [88,500, 89,200, 88,800, 89,800, 90,100]
High:        [88,700, 89,500, 89,000, 90,000, 90,300]
Low:         [88,400, 89,000, 88,600, 89,600, 89,900]
Close:       [88,500, 89,200, 88,800, 89,800, 90,100]
```

**Step 1: Calcolo ATR (n=3, metodo SMA)**

TR_1 = max(88,700-88,400, |88,700-0|, |88,400-0|) = 300
TR_2 = max(89,500-89,000, |89,500-88,500|, |89,000-88,500|) = 1,000
TR_3 = max(89,000-88,600, |89,000-89,200|, |88,600-89,200|) = 600

ATR_3 = (300 + 1,000 + 600) / 3 = 633.33 EUR

**Step 2: Rilevamento Pivot (metodo ATR, k=1.5)**

Candidato pivot low: indice 2, prezzo 88,800
Prezzo successivo: 89,800
Variazione: 89,800 - 88,800 = 1,000 EUR
Soglia ATR: 633.33 × 1.5 = 950 EUR

1,000 >= 950 → PIVOT LOW CONFERMATO

**Step 3: Calcolo PPB (divisor=2.0)**

PPB = ATR_pivot / divisor = 633.33 / 2.0 = 316.67 EUR/barra

**Step 4: Costruzione Linee (ratios=[1, 2])**

Pivot: t_0=2, P_0=88,800
Target: t=4 (2 barre dopo pivot)

Linea ratio=1 (1x1):
P(4) = 88,800 + 1 × 316.67 × (4-2) = 88,800 + 633.34 = 89,433.34 EUR

Linea ratio=2 (2x1):
P(4) = 88,800 + 2 × 316.67 × (4-2) = 88,800 + 1,266.68 = 90,066.68 EUR

**Interpretazione:**
- Prezzo reale a t=4: 90,100 EUR
- Sopra linea 2x1 (90,066.68) → Trend molto forte
- Prossimo target: linea 4x1

---

## Formula Reference Quick

### True Range
```
TR = max(H - L, |H - C_prev|, |L - C_prev|)
```

### ATR (SMA)
```
ATR = (1/n) × Σ(TR_i)
```

### ATR (Wilder)
```
ATR_t = ATR_{t-1} + (1/n) × (TR_t - ATR_{t-1})
```

### Pivot Detection (Percent)
```
Low:  (P_t - P_cand) / P_cand >= θ
High: (P_cand - P_t) / P_cand >= θ
```

### Pivot Detection (ATR)
```
Low:  P_t - P_cand >= ATR × k
High: P_cand - P_t >= ATR × k
```

### PPB
```
ATR mode:   PPB = ATR_pivot / divisor
Fixed mode: PPB = fixed_value
```

### Fan Lines
```
UP:   P(t) = P_0 + r × ppb × (t - t_0)
DOWN: P(t) = P_0 - r × ppb × (t - t_0)
```

### Angle
```
θ = arctan(ratio)
```

---

## Note Implementative

### Validazioni nel Codice

Il modulo `gann_fan` esegue le seguenti validazioni:

1. **DataFrame:** Deve contenere colonne `High`, `Low`, `Close`
2. **ATR length:** Deve essere ≥ 2
3. **Threshold:** Deve essere > 0
4. **ATR multiplier:** Deve essere > 0
5. **PPB divisor:** Deve essere > 0
6. **Bars forward:** Deve essere > 0
7. **Ratios:** Lista non vuota, valori > 0
8. **Pivot trovati:** Almeno un pivot deve essere rilevato

### Edge Cases Gestiti

- **DataFrame troppo corto:** Errore se len(df) < atr_len + 1
- **Nessun pivot trovato:** Suggerimento di ridurre threshold/atr_mult
- **ATR NaN al pivot:** Errore con suggerimento di aumentare dati o ridurre atr_len
- **Pivot al limite:** bars_forward limitato ai dati disponibili
- **Ratios duplicati:** Rimossi automaticamente

---

## Codice Esempio Minimo

```python
# Import
from gann_fan import get_coinbase_candles, gann_fan
from gann_fan.plot import plot_fan_with_date
import matplotlib.pyplot as plt

# Dati (24h BTC/EUR 15min)
df = get_coinbase_candles("BTC-EUR", 900, 96)

# Calcolo ventaglio
fan = gann_fan(df, pivot_source="last_low")

# Info
print(f"Pivot: {fan.pivot_idx} @ {fan.pivot_price:.2f}")
print(f"PPB: {fan.ppb:.2f}")
print(f"Linee: {len(fan.lines)}")

# Visualizza
plot_fan_with_date(df, fan, "Date")
plt.show()
```

---

## Bibliografia

- Gann, W.D. (1949). "45 Years in Wall Street"
- Gann, W.D. (1927). "The Tunnel Thru the Air"
- Wilder, J.W. (1978). "New Concepts in Technical Trading Systems"

---

**Documento creato per: Gann Fan Python Module v1.0.0**  
**Data: Novembre 2025**  
**Licenza: MIT**
