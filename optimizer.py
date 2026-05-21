"""Mini Optimizer — implementation.

Vectorised with NumPy: for each (SL, TP) combination we compute the adjusted
PnL series across all trades in O(N) using boolean masks, then derive Sharpe,
total_pnl, stopped_out and took_profit counts.

Sharpe uses population standard deviation (ddof=0).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def optimize(
    trades_df: pd.DataFrame,
    stop_losses: list[float],
    take_profits: list[float],
    top_n: int = 5,
) -> list[dict]:
    if trades_df is None or len(trades_df) == 0:
        return []
    if not stop_losses or not take_profits:
        return []

    pnl = trades_df["pnl"].to_numpy(dtype=np.float64)
    mae = trades_df["mae"].to_numpy(dtype=np.float64)
    mfe = trades_df["mfe"].to_numpy(dtype=np.float64)
    n = pnl.shape[0]

    results: list[dict] = []
    for sl in stop_losses:
        sl_f = float(sl)
        sl_mask = mae >= sl_f  # SL has priority
        for tp in take_profits:
            tp_f = float(tp)
            tp_mask = (~sl_mask) & (mfe >= tp_f)
            neither = ~(sl_mask | tp_mask)

            adjusted = np.empty(n, dtype=np.float64)
            adjusted[sl_mask] = -sl_f
            adjusted[tp_mask] = tp_f
            adjusted[neither] = pnl[neither]

            mean = float(adjusted.mean())
            std = float(adjusted.std(ddof=0))
            sharpe = 0.0 if std == 0.0 else mean / std
            total_pnl = float(adjusted.sum())

            results.append(
                {
                    "stop_loss": sl_f,
                    "take_profit": tp_f,
                    "sharpe": float(sharpe),
                    "total_pnl": total_pnl,
                    "stopped_out": int(sl_mask.sum()),
                    "took_profit": int(tp_mask.sum()),
                }
            )

    results.sort(
        key=lambda r: (-r["sharpe"], -r["total_pnl"], r["stop_loss"], r["take_profit"])
    )
    return results[:top_n]
