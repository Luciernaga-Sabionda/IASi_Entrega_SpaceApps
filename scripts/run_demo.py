#!/usr/bin/env python3
# Demo rápida del score IASi
from math import exp

weights = {"alpha":0.25,"beta":0.20,"gamma":0.25,"delta":0.15,"epsilon":0.15}
def sigmoid(x): return 1/(1+exp(-x))
def clip(x, lo=0, hi=1): return max(lo, min(hi, x))

ejemplo = {
  "A": {"a_score": 0.8},
  "R": {"r_zscore": 2.1},
  "D": {"p95_defo_mm": 18.7, "coh_mean": 0.46},
  "M": {"m_verified_ratio": 0.67},
  "S": {"s_activity_z": 1.9}
}

def iasi_score(x,w):
    A_ = clip(x["A"].get("a_score",0))
    R_ = sigmoid(x["R"].get("r_zscore",0))
    D_ = clip(x["D"].get("p95_defo_mm",0)/20.0) if x["D"].get("coh_mean",0)>=0.3 else 0.0
    M_ = clip(x["M"].get("m_verified_ratio",0))
    S_ = sigmoid(x["S"].get("s_activity_z",0))
    return w["alpha"]*A_ + w["beta"]*R_ + w["gamma"]*D_ + w["delta"]*M_ + w["epsilon"]*S_

if __name__=="__main__":
    s = iasi_score(ejemplo, weights)
    print(f"IASi = {s:.2f}")
