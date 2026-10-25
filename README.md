# D2C Returns & Refund Process Improvement (Business Analyst project)

**Role focus:** Business Analyst | **Deliverables:** BRD, as-is / to-be process maps, requirements and user stories, KPI framework, cost-benefit model, supporting Python analysis

## The case
A fictional D2C footwear and apparel brand sees one in four orders returned. Returns cost about 11% of GMV and customers wait almost 13 days for refunds. As the BA, the goal is to quantify the problem, document the current process, specify requirements for a better one, and test whether the investment pays back.

## What is inside
| File | What it is |
|---|---|
| `docs/BRD_returns_process_improvement.md` (and `.docx`) | Full business requirements document: objectives, scope, RACI, findings, FR/NFR, user stories, KPIs, cost-benefit, roadmap, risks |
| `outputs/process_as_is.png`, `process_to_be.png` | Swimlane process maps |
| `outputs/01-06_*.png` | Analysis charts (return rate, reasons, refund stages, CSAT vs TAT, cost, savings scenarios) |
| `outputs/key_numbers.json` | Every number quoted in the BRD |
| `src/generate_data.py`, `src/analysis.py`, `src/process_maps.py` | Reproducible pipeline |

## Headline findings (synthetic data)
- Return rate **24.9%**; **43.7% of returns are size/fit** issues. Size-guide users return at 18.3% vs 29.0% (association, to be tested).
- Refund takes **12.8 days** on average; CSAT drops from about 4.0 (6-9 days) to 2.9 (12+ days).
- Return cost about **INR 46.5 lakh** over six months (INR 777 per return); 60% is unrecovered product value.
- Defect returns are 10.5% of returns but 22% of cost, a signal for the supplier-quality loop.
- **The business case is marginal on hard savings alone** (base case: INR 13.4 lakh a year vs INR 19.5 lakh year-1 investment, payback about 17.5 months), so the BRD recommends a gated pilot rather than a full build.

## Run it
```bash
pip install pandas numpy matplotlib
python src/generate_data.py && python src/analysis.py && python src/process_maps.py
```

*All data is synthetic. Cost inputs are stated assumptions; replace them with company actuals before using the numbers.*
