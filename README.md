# Semiconductor Fab Predictive Maintenance Simulator

A discrete-event simulation of a six-tool semiconductor fab, paired with a
machine learning pipeline that predicts each tool's Remaining Useful Life
(RUL) from live process drift and feeds predictions back into the running
simulation — so predictive maintenance can be tested against a reactive
baseline on actual profit, not just prediction accuracy.

## Why this exists

This project started on placement, where I found myself asking why maintenance scheduling wasn't more data-driven. 
Around the same time I was reading into digital twins and realised that was exactly the kind of system that could answer my question.
So, I set out to simulate a fab, predict failure before it happens, and actually test whether that prediction changes the outcome. 
This is the first serious piece of software I've built. I taught myself the statistics, ML, and software engineering behind it, coming from a mechanical engineering 
background rather than a computer science one. I've enjoyed it more than I expected, and I plan to keep extending it.

## Architecture

```
┌──────────────┐   18 sensor streams   ┌───────────────┐   raw + rolling   ┌────────────────┐
│  SimPy Fab   │ ────────────────────▶ │  EDA / Feature│ ────────────────▶│  GB Regressor  │
│  Simulation  │  (6 tool types,       │  Engineering  │   mean features   │  (RUL model)   │
│  18 instances│   nonlinear drift)    └───────────────┘                   └────────┬───────┘
└──────┬───────┘                                                                    │
       │                                                                            │ bootstrap
       │      RUL prediction + uncertainty, injected live via joblib                │ resample
       └────────────────────────────────────────────────────────────────────────────┤ (N=30)
                                                                                      ▼
                                                                          mean RUL ± std (UQ)
                                                                                      │
                                                                                      ▼
                                                                    A/B: models-on vs models-off
                                                                    paired comparison on profit
```

## Tech stack

| Tool | Why |
|---|---|
| **SimPy** | Discrete-event simulation of the fab — resource contention, repair, and lot flow needed an event-scheduling model, not a fixed timestep loop. |
| **NumPy / pandas** | Drift/noise generation and per-tool feature engineering. |
| **scikit-learn (Gradient Boosting)** | Selected over Random Forest after a bucketed comparison — GB had a lower RMSE near the failure threshold, the region that actually matters for triggering maintenance. |
| **joblib** | Serialises trained ensembles once per tool type and injects them live into the running simulation. |
| **Streamlit** *(planned)* | Dashboard layer — not yet built. |

## Results (50-seed A/B, stationary drift)

Paired comparison of predictive maintenance (model-triggered) against
reactive maintenance, same seed used for both arms of each pair to
isolate the effect of the intervention.

| | Reactive (off) | Predictive (on) |
|---|---|---|
| Breakdowns per run | 150–192 | **0, every run** |
| Breakdowns prevented per run | — | 235–281 |
| Profit improvement | — | **+156% average** (95% CI, run-to-run: 138–186%) |

Paired t-test: p < 0.001. The effect size is large mainly because
detection was perfect in every seed under this drift regime — closer to
"always catches it" vs "never catches it" than two comparably-noisy
strategies. That's a property of stationary, low-noise drift, not
necessarily a general claim about the model — see What's next below.

## How to run

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Currently always runs the full 50-seed A/B comparison (reactive vs.
# predictive maintenance) and saves results to ab_results.xlsx / .csv —
# see What's next for a planned single-run toggle
python <main_script>.py
```

*(Update this block with your actual entry-point paths/filenames.)*

## What's next

**Code quality pass, in progress:**
- Adding docstrings and type hints throughout — deferred during the
  build to move fast on the working pipeline first
- Splitting up functions that grew too large, e.g. `BaseMachine.running()`
  currently handles sensor drift, output calculation, model inference,
  and failure/reset logic in one method — being broken into separate,
  single-purpose methods
- Adding a toggle so running the script directly can do a single simulation or the full 50-seed A/B sweep. 
  Right now it always runs the full sweep, which takes a while even for a quick check

**Extending the simulation:**
- Adding non-stationary (accelerating) drift, to test whether the model's
  advantage holds once degradation — and detection — is genuinely hard,
  rather than the near-perfect case above
- Adding a scheduled/fixed-interval maintenance arm to the A/B comparison
  alongside reactive and predictive, to separate "any foresight beats
  none" from "the model specifically adds value"


**Not started:**
- SHAP explainability
- Drift detection (KS test on rolling sensor windows)
- Streamlit dashboard