"""
Modulo per la visualizzazione del ventaglio di Gann.

Fornisce funzioni per creare grafici dei prezzi con le linee del ventaglio sovrapposte.
"""

from typing import Optional
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.axes import Axes

from gann_fan.core import FanResult


def plot_fan(
    df: pd.DataFrame,
    fan: FanResult,
    ax: Optional[Axes] = None,
    show_labels: bool = True,
    figsize: tuple = (14, 8)
) -> Axes:
    """
    Visualizza il ventaglio di Gann insieme ai prezzi.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con dati di prezzo (deve contenere almeno "Close")
    fan : FanResult
        Risultato del calcolo del ventaglio di Gann
    ax : Optional[Axes], default=None
        Axes matplotlib su cui disegnare. Se None, viene creato un nuovo plot
    show_labels : bool, default=True
        Se True, mostra le etichette con i ratios sulle linee
    figsize : tuple, default=(14, 8)
        Dimensioni della figura (usato solo se ax è None)
    
    Returns
    -------
    Axes
        L'oggetto Axes matplotlib utilizzato
    
    Examples
    --------
    >>> import pandas as pd
    >>> from gann_fan.core import gann_fan
    >>> from gann_fan.plot import plot_fan
    >>> import matplotlib.pyplot as plt
    >>> 
    >>> df = pd.read_csv("prices.csv")
    >>> fan = gann_fan(df, pivot_source="last_low")
    >>> plot_fan(df, fan)
    >>> plt.show()
    """
    # Crea nuovo plot se necessario
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Disegna i prezzi
    ax.plot(df.index, df["Close"], label="Close", color="black", linewidth=1.5, zorder=2)
    
    # Disegna il punto pivot
    ax.scatter(
        [fan.pivot_idx],
        [fan.pivot_price],
        color="red",
        s=100,
        zorder=5,
        label=f"Pivot ({fan.pivot_idx}, {fan.pivot_price:.2f})"
    )
    
    # Definisci colori per le linee - più intensi per migliore visibilità
    colors_up = plt.cm.Greens(0.7)
    colors_down = plt.cm.Reds(0.7)
    
    # Disegna le linee del ventaglio
    for line in fan.lines:
        # Array di indici e prezzi per la linea
        x = [line.start_idx, line.end_idx]
        y = [line.y0, line.y1]
        
        # Colore basato sulla direzione
        color = colors_up if line.direction == "up" else colors_down
        
        # Disegna la linea - linewidth aumentato per migliore visibilità
        ax.plot(x, y, color=color, linestyle="--", linewidth=1.5, alpha=0.75, zorder=1)
        
        # Aggiungi etichetta se richiesto
        if show_labels:
            # Posiziona l'etichetta alla fine della linea
            label_text = f"{line.ratio:.3g}"
            ax.text(
                line.end_idx,
                line.y1,
                label_text,
                fontsize=9,
                color=color,
                ha="left",
                va="center",
                alpha=0.9,
                fontweight="bold"
            )
    
    # Configurazione del plot
    ax.set_xlabel("Bar Index", fontsize=12)
    ax.set_ylabel("Price", fontsize=12)
    ax.set_title(
        f"Gann Fan - Pivot: {fan.pivot_idx}, PPB: {fan.ppb:.4f}",
        fontsize=14,
        fontweight="bold"
    )
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    
    return ax


def plot_fan_with_date(
    df: pd.DataFrame,
    fan: FanResult,
    date_col: str = "Date",
    ax: Optional[Axes] = None,
    show_labels: bool = True,
    figsize: tuple = (14, 8)
) -> Axes:
    """
    Visualizza il ventaglio di Gann con asse x basato su date.
    
    Parameters
    ----------
    df : pd.DataFrame
        DataFrame con dati di prezzo e colonna date
    fan : FanResult
        Risultato del calcolo del ventaglio di Gann
    date_col : str, default="Date"
        Nome della colonna contenente le date
    ax : Optional[Axes], default=None
        Axes matplotlib su cui disegnare. Se None, viene creato un nuovo plot
    show_labels : bool, default=True
        Se True, mostra le etichette con i ratios sulle linee
    figsize : tuple, default=(14, 8)
        Dimensioni della figura (usato solo se ax è None)
    
    Returns
    -------
    Axes
        L'oggetto Axes matplotlib utilizzato
    
    Raises
    ------
    ValueError
        Se date_col non è presente nel DataFrame
    """
    if date_col not in df.columns:
        raise ValueError(f"Colonna '{date_col}' non trovata nel DataFrame")
    
    # Crea nuovo plot se necessario
    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)
    
    # Usa le date come asse x
    dates = df[date_col]
    
    # Disegna i prezzi
    ax.plot(dates, df["Close"], label="Close", color="black", linewidth=1.5, zorder=2)
    
    # Disegna il punto pivot
    ax.scatter(
        [dates.iloc[fan.pivot_idx]],
        [fan.pivot_price],
        color="red",
        s=100,
        zorder=5,
        label=f"Pivot ({dates.iloc[fan.pivot_idx]}, {fan.pivot_price:.2f})"
    )
    
    # Definisci colori per le linee - più intensi per migliore visibilità
    colors_up = plt.cm.Greens(0.7)
    colors_down = plt.cm.Reds(0.7)
    
    # Disegna le linee del ventaglio
    for line in fan.lines:
        # Array di date e prezzi per la linea
        x = [dates.iloc[line.start_idx], dates.iloc[line.end_idx]]
        y = [line.y0, line.y1]
        
        # Colore basato sulla direzione
        color = colors_up if line.direction == "up" else colors_down
        
        # Disegna la linea - linewidth aumentato per migliore visibilità
        ax.plot(x, y, color=color, linestyle="--", linewidth=1.5, alpha=0.75, zorder=1)
        
        # Aggiungi etichetta se richiesto
        if show_labels:
            label_text = f"{line.ratio:.3g}"
            ax.text(
                dates.iloc[line.end_idx],
                line.y1,
                label_text,
                fontsize=9,
                color=color,
                ha="left",
                va="center",
                alpha=0.9,
                fontweight="bold"
            )
    
    # Configurazione del plot
    ax.set_xlabel("Date", fontsize=12)
    ax.set_ylabel("Price", fontsize=12)
    ax.set_title(
        f"Gann Fan - Pivot: {dates.iloc[fan.pivot_idx]}, PPB: {fan.ppb:.4f}",
        fontsize=14,
        fontweight="bold"
    )
    ax.legend(loc="best")
    ax.grid(True, alpha=0.3)
    
    # Ruota le etichette delle date per leggibilità
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha="right")
    
    return ax
