import json, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg"); import matplotlib.pyplot as plt
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; O = ROOT/"outputs"
BLUE, ORANGE, INK, MUTED, GRID, AQUA = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e1", "#1baf7a"
plt.rcParams.update({"axes.edgecolor":GRID,"axes.labelcolor":MUTED,"xtick.color":MUTED,"ytick.color":MUTED,"axes.spines.top":False,
  "axes.spines.right":False,"axes.grid":True,"grid.color":GRID,"axes.axisbelow":True,"figure.dpi":150})
df = pd.read_csv(ROOT/"data/orders_returns.csv", parse_dates=["order_date"]); r = df[df.returned].copy()
out = {}

# ---------- 1. where do returns come from
rate = lambda g: df.groupby(g).returned.mean().mul(100).round(1)
out["return_rate_overall"] = round(df.returned.mean()*100, 1)
by_cat, by_pay, by_ch, by_sg = rate("category"), rate("payment"), rate("channel"), rate("used_size_guide")
reasons = r.reason.value_counts(); reasons_pct = (reasons/reasons.sum()*100).round(1)
out.update(by_cat=by_cat.to_dict(), by_pay=by_pay.to_dict(), by_ch=by_ch.to_dict(), by_sg={str(k): v for k, v in by_sg.items()}, reasons=reasons_pct.to_dict())

# ---------- 2. process time
stages = ["pickup_tat_days","warehouse_receipt_days","qc_wait_days","refund_days"]
st = r[stages].mean().round(1); out["stage_days"] = st.to_dict(); out["avg_tat"] = round(r.total_refund_tat_days.mean(), 1)
r["tat_band"] = pd.cut(r.total_refund_tat_days, [0, 6, 9, 12, 100], labels=["<=6 days","6-9","9-12","12+ days"])
band = r.groupby("tat_band", observed=True).agg(n=("csat","size"), csat=("csat","mean"), tickets=("support_tickets","mean")).round(2)
out["tat_band"] = band.reset_index().astype({"tat_band": str}).to_dict("records")
out["avg_touchpoints"] = round(r.manual_touchpoints.mean(), 1)

# ---------- 3. cost of returns (assumptions in README)
A = dict(reverse_pickup=85, warehouse_handling=35, manual_qc=30, forward_ship_lost=70, ticket=45, gateway_pct=0.02)
rec = {"A": 1.0, "B": .75, "C": .40, "Reject": 0.0}
r["recovery"] = r.qc_grade.map(rec)
r["value_loss"] = r.order_value_inr * (1 - r.recovery)
r["cost_reverse"] = A["reverse_pickup"] + A["forward_ship_lost"]; r["cost_handling"] = A["warehouse_handling"] + A["manual_qc"]
r["cost_support"] = r.support_tickets * A["ticket"]; r["cost_gateway"] = np.where(r.payment == "Prepaid", r.order_value_inr * A["gateway_pct"], 0)
r["total_cost"] = r[["value_loss","cost_reverse","cost_handling","cost_support","cost_gateway"]].sum(axis=1)
tot = r[["value_loss","cost_reverse","cost_handling","cost_support","cost_gateway"]].sum()
out["cost_lakh"] = (tot/1e5).round(1).to_dict(); out["cost_total_lakh"] = round(tot.sum()/1e5, 1)
out["cost_per_return"] = round(r.total_cost.mean()); out["returns"] = int(len(r)); out["orders"] = int(len(df))
out["gmv_lakh"] = round(df.order_value_inr.sum()/1e5, 1); out["cost_pct_gmv"] = round(tot.sum()/df.order_value_inr.sum()*100, 1)
out["grade_mix"] = (r.qc_grade.value_counts(normalize=True)*100).round(1).to_dict()
out["cost_by_reason_lakh"] = (r.groupby("reason").total_cost.sum()/1e5).round(1).sort_values(ascending=False).to_dict()

# ---------- 4. repeat returners
cust = df.groupby("customer_id").agg(orders=("order_id","size"), returns=("returned","sum"))
rep = cust[(cust.orders >= 3)]; out["repeat_customers_3plus"] = int(len(rep)); out["repeat_high_return"] = int((rep.returns/rep.orders >= .67).sum())
out["wardrobing_pct"] = float(reasons_pct.get("Wardrobing/misuse", 0))

# ---------- 5. to-be scenarios (explicit assumptions)
ng = df[~df.used_size_guide]; rate_ng, rate_g = ng.returned.mean(), df[df.used_size_guide].returned.mean()
size_share = (r.reason == "Size/fit issue").mean()
months = 6
def scenario(sg_uplift, qc_cut, instant_refund_share):
    # (1) fit-guide adoption: convert part of non-users to users, avoided returns = conv * rate gap
    conv = len(ng) * sg_uplift; avoided = conv * (rate_ng - rate_g)
    avg_cost = r.total_cost.mean(); s1 = avoided * avg_cost
    # (2) QC automation: cut qc_wait days; saves manual QC cost on fast-track share + tickets from delay
    s2 = len(r) * (A["manual_qc"] * qc_cut) + r.cost_support.sum() * (qc_cut * .5)
    # (3) instant refund for prepaid: fewer 'where is my refund' tickets
    pre = r[r.payment == "Prepaid"]; s3 = pre.cost_support.sum() * instant_refund_share * .6
    return dict(fit_guide=round(s1/1e5, 1), qc_automation=round(s2/1e5, 1), instant_refund=round(s3/1e5, 1), avoided_returns=int(avoided))
sc = {"Low": scenario(.15, .40, .30), "Base": scenario(.30, .60, .50), "High": scenario(.45, .75, .70)}
for k, v in sc.items(): v["total_6m_lakh"] = round(v["fit_guide"] + v["qc_automation"] + v["instant_refund"], 1); v["annual_lakh"] = round(v["total_6m_lakh"]*2, 1)
out["scenarios"] = sc; out["rate_ng"] = round(rate_ng*100, 1); out["rate_g"] = round(rate_g*100, 1)
invest = dict(fit_tool_annual=9.0, qc_workflow_one_time=6.0, qc_workflow_annual=1.5, refund_integration_one_time=3.0)
inv_y1 = invest["fit_tool_annual"] + invest["qc_workflow_one_time"] + invest["qc_workflow_annual"] + invest["refund_integration_one_time"]
out["invest_y1_lakh"] = inv_y1
for k, v in sc.items(): v["net_y1_lakh"] = round(v["annual_lakh"] - inv_y1, 1); v["payback_months"] = round(inv_y1 / (v["annual_lakh"]/12), 1) if v["annual_lakh"] > 0 else None
json.dump(out, open(O/"key_numbers.json", "w"), indent=2, default=str)
print(json.dumps(out, indent=1, default=str))

# ---------- charts
fig, ax = plt.subplots(figsize=(7.5, 4)); s = by_cat.sort_values(); ax.barh(s.index, s.values, color=[ORANGE if v > out["return_rate_overall"] else BLUE for v in s.values], height=.55)
for y, v in enumerate(s.values): ax.text(v + .3, y, f"{v:.0f}%", va="center", fontsize=8, color=INK)
ax.axvline(out["return_rate_overall"], color=MUTED, ls="--", lw=1); ax.grid(axis="y", visible=False); ax.set_xlabel("Return rate %")
ax.set_title("Fit-sensitive categories return the most", loc="left", color=INK, fontsize=11); fig.tight_layout(); fig.savefig(O/"01_return_rate_by_category.png"); plt.close()

fig, ax = plt.subplots(figsize=(7.5, 4)); s = reasons_pct.sort_values(); ax.barh(s.index, s.values, color=[ORANGE if i == s.index[-1] else BLUE for i in s.index], height=.55)
for y, v in enumerate(s.values): ax.text(v + .3, y, f"{v:.0f}%", va="center", fontsize=8, color=INK)
ax.grid(axis="y", visible=False); ax.set_xlabel("% of returns"); ax.set_title("Why customers return", loc="left", color=INK, fontsize=11); fig.tight_layout(); fig.savefig(O/"02_return_reasons.png"); plt.close()

fig, ax = plt.subplots(figsize=(7.5, 2.8)); left = 0
for (k, v), col in zip(st.items(), [BLUE, AQUA, ORANGE, "#6250d6"]):
    ax.barh([0], [v], left=left, color=col, height=.45, edgecolor="white", linewidth=2); ax.text(left + v/2, 0, f"{v:.1f}d", ha="center", va="center", color="white", fontsize=8)
    ax.text(left + v/2, .38, k.replace("_days","").replace("_"," "), ha="center", fontsize=7.5, color=MUTED); left += v
ax.set_yticks([]); ax.grid(False); ax.set_xlabel("Days from return request to refund"); ax.set_title(f"Average refund takes {out['avg_tat']} days; QC wait is the biggest controllable stage", loc="left", color=INK, fontsize=10)
fig.tight_layout(); fig.savefig(O/"03_refund_tat_stages.png"); plt.close()

fig, ax = plt.subplots(figsize=(6.5, 3.8)); b = band.reset_index(); ax.bar(b.tat_band.astype(str), b.csat, color=BLUE, width=.5)
for i, v in enumerate(b.csat): ax.text(i, v + .05, f"{v:.2f}", ha="center", fontsize=8, color=INK)
ax.set_ylim(0, 5); ax.set_xlabel("Refund turnaround band"); ax.set_ylabel("Avg CSAT (1-5)"); ax.set_title("Slower refunds, lower satisfaction", loc="left", color=INK, fontsize=11)
fig.tight_layout(); fig.savefig(O/"04_csat_vs_tat.png"); plt.close()

fig, ax = plt.subplots(figsize=(6.5, 3.8)); cs = pd.Series(out["cost_lakh"]).sort_values(); ax.barh([c.replace("_"," ") for c in cs.index], cs.values, color=BLUE, height=.5)
for y, v in enumerate(cs.values): ax.text(v + .3, y, f"{v:.1f}", va="center", fontsize=8, color=INK)
ax.grid(axis="y", visible=False); ax.set_xlabel("INR lakh (6 months)"); ax.set_title(f"Returns cost about INR {out['cost_total_lakh']} lakh ({out['cost_pct_gmv']}% of GMV)", loc="left", color=INK, fontsize=11)
fig.tight_layout(); fig.savefig(O/"05_cost_of_returns.png"); plt.close()

fig, ax = plt.subplots(figsize=(7, 4)); x = np.arange(3); w = .6; bot = np.zeros(3)
for key, col, lab in [("fit_guide", BLUE, "Fit guide"), ("qc_automation", AQUA, "QC automation"), ("instant_refund", ORANGE, "Instant refund")]:
    vals = np.array([sc[s][key]*2 for s in ["Low","Base","High"]]); ax.bar(x, vals, w, bottom=bot, color=col, label=lab, edgecolor="white", linewidth=2); bot += vals
ax.axhline(inv_y1, color=MUTED, ls="--", lw=1); ax.text(2.4, inv_y1 + .4, f"Year-1 investment {inv_y1:.1f}", color=MUTED, fontsize=8, ha="right")
ax.set_xticks(x, ["Low","Base","High"]); ax.set_ylabel("Annual savings, INR lakh"); ax.set_ylim(0, 24); ax.grid(axis="x", visible=False); ax.legend(frameon=False, fontsize=8, ncol=3, loc="upper left")
ax.set_title("Annual savings by scenario vs year-1 investment", loc="left", color=INK, fontsize=11); fig.tight_layout(); fig.savefig(O/"06_savings_scenarios.png"); plt.close()
