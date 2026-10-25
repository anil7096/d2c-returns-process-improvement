"""Synthetic returns data for a D2C footwear + apparel brand (seeded)."""
import numpy as np, pandas as pd
from pathlib import Path
rng = np.random.default_rng(21); OUT = Path(__file__).resolve().parents[1] / "data"
N = 24000
cats = {"Sneakers":(2499,.27),"Formal shoes":(2999,.22),"T-shirts":(799,.17),"Jeans":(1599,.31),"Kurtas":(1299,.24),"Jackets":(2799,.20)}
cat = rng.choice(list(cats), N, p=[.22,.10,.24,.18,.16,.10])
price = np.array([cats[c][0] for c in cat]) * rng.uniform(.85, 1.1, N)
base = np.array([cats[c][1] for c in cat])
df = pd.DataFrame({"order_id":[f"D{i+1:06d}" for i in range(N)],
    "order_date":rng.choice(pd.date_range("2026-04-01","2026-09-30"), N), "category":cat, "order_value_inr":price.round(),
    "channel":rng.choice(["Website","App","Marketplace"], N, p=[.35,.45,.20]), "payment":rng.choice(["Prepaid","COD"], N, p=[.55,.45]),
    "customer_id":[f"C{rng.integers(1, 15000):05d}" for _ in range(N)]})
# size-guide effect: apparel/footwear without size chart interaction return more
df["used_size_guide"] = rng.random(N) < .38
p_ret = base * np.where(df.used_size_guide, .70, 1.10) * np.where(df.payment == "COD", 1.25, .9) * np.where(df.channel == "Marketplace", 1.2, 1.0)
df["returned"] = rng.random(N) < p_ret.clip(0, .8)
reasons = ["Size/fit issue","Not as pictured","Quality defect","Changed mind","Wrong item sent","Late delivery","Wardrobing/misuse"]
def reason(row):
    if row.category in ("Sneakers","Formal shoes","Jeans"): p = [.50,.14,.10,.12,.04,.05,.05]
    elif row.category in ("Jackets","Kurtas"): p = [.35,.22,.12,.14,.04,.05,.08]
    else: p = [.36,.20,.12,.16,.04,.06,.06]
    return rng.choice(reasons, p=p)
ret = df[df.returned].copy(); ret["reason"] = ret.apply(reason, axis=1)
ret["return_requested_days"] = rng.integers(1, 10, len(ret))
# process timestamps (days): pickup -> warehouse receipt -> QC -> refund. Manual QC is the bottleneck, esp. in peak
ret["pickup_tat_days"] = np.round(rng.gamma(2, 1.1, len(ret)) + 1, 1)
ret["warehouse_receipt_days"] = np.round(rng.gamma(2, 1.0, len(ret)) + 1.5, 1)
ret["qc_wait_days"] = np.round(rng.gamma(2.4, 1.5, len(ret)) + (ret.order_date.dt.month.isin([6,9]) if False else 0), 1)
ret["refund_days"] = np.round(rng.gamma(1.6, 1.0, len(ret)) + np.where(ret.payment == "COD", 1.5, 0.3), 1)
ret["total_refund_tat_days"] = (ret.pickup_tat_days + ret.warehouse_receipt_days + ret.qc_wait_days + ret.refund_days).round(1)
ret["qc_grade"] = np.where(ret.reason.isin(["Quality defect"]), rng.choice(["A","B","C","Reject"], len(ret), p=[.05,.15,.30,.50]),
                  np.where(ret.reason == "Wardrobing/misuse", rng.choice(["A","B","C","Reject"], len(ret), p=[.05,.15,.40,.40]),
                           rng.choice(["A","B","C","Reject"], len(ret), p=[.62,.23,.10,.05])))
ret["manual_touchpoints"] = rng.integers(3, 8, len(ret))
ret["support_tickets"] = rng.poisson(0.4 + 0.18*(ret.total_refund_tat_days - 6).clip(lower=0))
ret["csat"] = np.clip(np.round(4.6 - 0.13*(ret.total_refund_tat_days - 5).clip(lower=0) - 0.2*ret.support_tickets + rng.normal(0, .7, len(ret))), 1, 5).astype(int)
df = df.merge(ret[["order_id","reason","return_requested_days","pickup_tat_days","warehouse_receipt_days","qc_wait_days","refund_days",
     "total_refund_tat_days","qc_grade","manual_touchpoints","support_tickets","csat"]], on="order_id", how="left")
df.to_csv(OUT/"orders_returns.csv", index=False); print(len(df), df.returned.sum(), round(100*df.returned.mean(),1))
