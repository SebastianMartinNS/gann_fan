"""
Interfaccia a riga di comando per il ventaglio di Gann.

Fornisce un comando CLI per calcolare e visualizzare ventagli di Gann da file CSV.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional

import pandas as pd
import matplotlib.pyplot as plt

from gann_fan.core import gann_fan
from gann_fan.plot import plot_fan_with_date


def parse_ratios(ratios_str: str) -> List[float]:
    """
    Converte una stringa di ratios separati da virgola in lista di float.
    
    Parameters
    ----------
    ratios_str : str
        Stringa con ratios separati da virgola (es. "0.125,0.25,1,2,4")
    
    Returns
    -------
    List[float]
        Lista di ratios
    
    Raises
    ------
    ValueError
        Se la conversione fallisce
    """
    try:
        ratios = [float(r.strip()) for r in ratios_str.split(",")]
        return ratios
    except ValueError as e:
        raise ValueError(f"Errore nel parsing dei ratios: {e}")


def main():
    """Entry point principale per la CLI."""
    parser = argparse.ArgumentParser(
        description="Calcola e visualizza il ventaglio di Gann da dati CSV",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    # File input
    parser.add_argument(
        "--csv",
        type=str,
        required=True,
        help="Path al file CSV con colonne: Date, Open, High, Low, Close, Volume(opzionale)"
    )
    
    # Parametri pivot source
    parser.add_argument(
        "--pivot_source",
        type=str,
        choices=["last_low", "last_high", "custom"],
        default="last_low",
        help="Sorgente del pivot da utilizzare"
    )
    
    parser.add_argument(
        "--pivot_mode",
        type=str,
        choices=["atr", "percent"],
        default="atr",
        help="Modalità di rilevamento pivot (ignorato se pivot_source=custom)"
    )
    
    # Parametri pivot detection
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.05,
        help="Soglia percentuale per pivot_mode=percent (es. 0.05 = 5%%)"
    )
    
    parser.add_argument(
        "--atr_len",
        type=int,
        default=14,
        help="Periodo per il calcolo dell'ATR"
    )
    
    parser.add_argument(
        "--atr_mult",
        type=float,
        default=1.0,
        help="Moltiplicatore ATR per pivot_mode=atr"
    )
    
    parser.add_argument(
        "--atr_method",
        type=str,
        choices=["sma", "wilder"],
        default="sma",
        help="Metodo di calcolo ATR"
    )
    
    # Parametri ppb
    parser.add_argument(
        "--ppb_mode",
        type=str,
        choices=["ATR", "Fixed"],
        default="ATR",
        help="Modalità di calcolo Price Per Bar"
    )
    
    parser.add_argument(
        "--atr_divisor",
        type=float,
        default=1.0,
        help="Divisore ATR per ppb_mode=ATR"
    )
    
    parser.add_argument(
        "--fixed_ppb",
        type=float,
        default=1.0,
        help="Valore fisso ppb per ppb_mode=Fixed"
    )
    
    # Parametri ventaglio
    parser.add_argument(
        "--ratios",
        type=str,
        default="0.125,0.25,0.333,0.5,1,2,3,4,8",
        help="Ratios del ventaglio separati da virgola (es. '0.125,0.25,1,2,4,8')"
    )
    
    parser.add_argument(
        "--bars_forward",
        type=int,
        default=100,
        help="Numero di barre di proiezione del ventaglio"
    )
    
    # Parametri custom pivot
    parser.add_argument(
        "--pivot_idx",
        type=int,
        default=None,
        help="Indice del pivot custom (richiesto se pivot_source=custom)"
    )
    
    parser.add_argument(
        "--pivot_price",
        type=float,
        default=None,
        help="Prezzo del pivot custom (richiesto se pivot_source=custom)"
    )
    
    # Output
    parser.add_argument(
        "--out",
        type=str,
        default="gann_fan.png",
        help="Path del file PNG di output"
    )
    
    parser.add_argument(
        "--date_col",
        type=str,
        default="Date",
        help="Nome della colonna contenente le date"
    )
    
    parser.add_argument(
        "--no_labels",
        action="store_true",
        help="Non mostrare le etichette dei ratios sul grafico"
    )
    
    # Parse arguments
    args = parser.parse_args()
    
    # Validazione input
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"Errore: File CSV non trovato: {args.csv}", file=sys.stderr)
        return 1
    
    # Validazione custom pivot
    if args.pivot_source == "custom":
        if args.pivot_idx is None or args.pivot_price is None:
            print(
                "Errore: pivot_source='custom' richiede --pivot_idx e --pivot_price",
                file=sys.stderr
            )
            return 1
        custom_pivot = (args.pivot_idx, args.pivot_price)
    else:
        custom_pivot = None
    
    # Parse ratios
    try:
        ratios = parse_ratios(args.ratios)
    except ValueError as e:
        print(f"Errore: {e}", file=sys.stderr)
        return 1
    
    # Carica dati
    print(f"Caricamento dati da {args.csv}...")
    try:
        df = pd.read_csv(args.csv)
        
        # Verifica colonne richieste
        required_cols = ["High", "Low", "Close"]
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(
                f"Errore: Colonne mancanti nel CSV: {missing}",
                file=sys.stderr
            )
            return 1
        
        # Parse date se presente
        if args.date_col in df.columns:
            df[args.date_col] = pd.to_datetime(df[args.date_col])
            df = df.sort_values(args.date_col).reset_index(drop=True)
        else:
            print(
                f"Warning: Colonna '{args.date_col}' non trovata. "
                f"Verrà usato l'indice numerico.",
                file=sys.stderr
            )
        
        print(f"Caricati {len(df)} record.")
        
    except Exception as e:
        print(f"Errore nel caricamento del CSV: {e}", file=sys.stderr)
        return 1
    
    # Calcola ventaglio
    print("Calcolo del ventaglio di Gann...")
    try:
        fan = gann_fan(
            df=df,
            pivot_source=args.pivot_source,
            pivot_mode=args.pivot_mode,
            threshold=args.threshold,
            atr_len=args.atr_len,
            atr_mult=args.atr_mult,
            atr_method=args.atr_method,
            ppb_mode=args.ppb_mode,
            atr_divisor=args.atr_divisor,
            fixed_ppb=args.fixed_ppb,
            ratios=ratios,
            bars_forward=args.bars_forward,
            custom_pivot=custom_pivot
        )
        
        print(f"Pivot: indice={fan.pivot_idx}, prezzo={fan.pivot_price:.4f}")
        print(f"PPB: {fan.ppb:.6f}")
        print(f"Linee generate: {len(fan.lines)}")
        
    except Exception as e:
        print(f"Errore nel calcolo del ventaglio: {e}", file=sys.stderr)
        return 1
    
    # Crea grafico
    print(f"Generazione grafico...")
    try:
        fig, ax = plt.subplots(figsize=(14, 8))
        
        # Usa plot con date se disponibile
        if args.date_col in df.columns:
            plot_fan_with_date(
                df=df,
                fan=fan,
                date_col=args.date_col,
                ax=ax,
                show_labels=not args.no_labels
            )
        else:
            from gann_fan.plot import plot_fan
            plot_fan(
                df=df,
                fan=fan,
                ax=ax,
                show_labels=not args.no_labels
            )
        
        # Salva il grafico
        plt.tight_layout()
        plt.savefig(args.out, dpi=150, bbox_inches="tight")
        print(f"Grafico salvato in: {args.out}")
        
    except Exception as e:
        print(f"Errore nella generazione del grafico: {e}", file=sys.stderr)
        return 1
    
    print("Completato con successo!")
    return 0


if __name__ == "__main__":
    sys.exit(main())
