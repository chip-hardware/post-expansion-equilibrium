# Dynamics of Post-Expansion Market Equilibrium

## Overview
This research project evaluates the structural behavior of highly liquid financial instruments following significant price displacement vectors using automated data pipelines.

The primary hypothesis states that high-momentum expansion candles generate structural pricing anomalies. The distribution mechanics that follow often induce temporary counter-trend or short-term breakout participation before the market mechanics deliver the price back to the **50% geometric center (Equilibrium level)** of the initial impulse to achieve structural rebalancing.

## Core Framework
The market architecture is modeled through three distinct structural phases:
1. **The Displacement Vector:** A high-volume, dynamic expansion bar that deviates significantly from the local volatility baseline.
2. **The Inducement & Distribution Phase:** A prolonged consolidation period characterized by structural noise and fake breakouts designed to build liquidity pools above or below the minor local boundaries.
3. **The Rebalancing Phase:** A rapid price delivery sequence back to the exact 50% midpoint of the original displacement bar to clear the pricing asymmetry.

```text
       [ Peak Expansion ] ---> (Inducement Phase)
             / \
            /   \    <--- Local Range Matrix / Stop Mitigation
           /     \
   =======/=======\======= [ 50% Equilibrium Level ] <--- Target Pivot
         /
 [Origin Vector]
```

## Analytical Engine (`radar_yfinance.py`)
The repository contains an automated quantitative scanner that isolates expansion vectors without relying on lagging indicators. 

### Features
* **Automated Pipeline:** Automatically syncs and pulls fresh 1-hour price data directly via the Yahoo Finance API layer.
* **H4 Resampling:** Mathematically aggregates 1h bar matrices into standard 4-hour ECN structural frames.
* **Dynamic Volatility Profiling:** Implements a dynamic rolling average window to measure baseline candle sizes, isolating expansion vectors that exceed the local variance by a factor of 3.5x.

### Execution
Ensure you have the required dependencies installed:
```bash
pip install pandas yfinance
```
To run the scanning engine:
```bash
python radar_yfinance.py
```

## Empirical Validation (Case Studies)
The automated scanner's findings have been compiled into detailed structural charts mapping different market scenarios. Review the specific documentation in the `charts/` directory:

* [**Case 01: GBPUSD**](./charts/gbpusd/readme.md) — Isolated short-term equilibrium mitigation cycles.
* [**Case 02: EURUSD**](./charts/eurusd/6week.md) — Multi-week macro-scale induced distribution trap (6-week rebalancing lifecycle).
* [**Case 03: USDCHF**](./charts/usdchf/readme.md) — Sequential block mitigation within a cascading trend structure.
* [**Case 04: USDCAD**](./charts/usdcad/readme.md) — Failed trend continuation matrix and 50% equilibrium level inversion.
* [**Case 05: GBPJPY**](./charts/gbpjpy/readme.md) — High-velocity algorithmic price delivery during macroeconomic crisis conditions.

## Open Research & Collaboration
This project functions as an open-source technical notebook. The objective is to compile empirical data regarding the duration of the distribution phases across different asset classes (Majors, Crosses, Commodities) and time horizons.

Contributions, data-driven counter-arguments, or historical dataset submissions are welcome via opening an **Issue** or starting a thread in the **Discussions** tab.
