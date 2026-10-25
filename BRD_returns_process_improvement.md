# Business Requirements Document: Returns & Refund Process Improvement

| | |
|---|---|
| **Company (fictional)** | Stride & Co., a D2C footwear and apparel brand |
| **Prepared by** | Business Analyst |
| **Version / status** | 1.0, for sponsor review |
| **Data basis** | 24,000 orders, Apr-Sep 2026 (synthetic dataset in `data/`) |

## 1. Executive summary
One in four orders (24.9%) is returned. Returns cost an estimated **INR 46.5 lakh in six months, 11% of GMV (INR 424 lakh)**, about INR 777 per return. Customers wait **12.8 days on average for a refund**, and satisfaction falls steeply with wait time (CSAT 4.0 at 6-9 days vs 2.9 beyond 12 days). 55% of returns take longer than 12 days. This document sets out the requirements for a three-part programme: a **fit guide**, **QC and refund automation**, and **proactive status communication**.

## 2. Business problem and objectives
**Problem:** returns are expensive, slow, and manual. Fit-related returns (44% of all returns) are largely preventable; slow refunds drive tickets and low CSAT.

| # | Objective (SMART) | Baseline | Target (6 months after go-live) |
|---|---|---|---|
| O1 | Reduce return rate | 24.9% | 21% or lower |
| O2 | Cut average refund turnaround | 12.8 days | 7 days or lower |
| O3 | Reduce manual touchpoints per return | 5.0 | 2 or fewer |
| O4 | Raise CSAT on returns | 3.3 (average across returns) | 4.0 or higher |
| O5 | Reduce support tickets per return | 1.6 | 0.6 or lower |

## 3. Scope
**In scope:** return initiation, approval, reverse pickup booking, warehouse receipt and QC, refund, customer notifications, reporting.
**Out of scope:** forward logistics, pricing and return-policy changes (policy is an input, not changed here), marketplace-owned return flows, supplier chargeback contracts (flagged as a follow-up).

## 4. Stakeholders and RACI
| Stakeholder | Interest | Role |
|---|---|---|
| COO (sponsor) | Cost and customer experience | Accountable |
| Head of Customer Support | Ticket volume, CSAT | Responsible (requirements, UAT) |
| Warehouse manager | QC throughput | Responsible (QC workflow) |
| Finance controller | Refund accuracy, fraud | Consulted (refund rules, controls) |
| Product / Tech lead | App and API changes | Responsible (delivery) |
| Logistics partners (3PL) | Pickup API | Consulted |
| Customers | Fast, clear refunds | Informed (pilot feedback) |

## 5. Current state (as-is)
See `outputs/process_as_is.png`. Average days by stage: pickup **3.2**, warehouse receipt **3.5**, QC wait **3.6**, refund **2.5**. A return passes through about 5 manual touchpoints (policy check, email to 3PL, paper/sheet QC, email to Finance, manual refund verification). The customer has no visibility between request and refund.

### Key findings
1. **Fit drives returns.** Size/fit is 43.7% of returns; Jeans (33%) and Sneakers (28%) return most. Orders where the customer used the size guide return at **18.3% vs 29.0%** for those who did not (association, not proven cause).
2. **Channel and payment matter.** COD 29.3% vs prepaid 21.4%; marketplace 29.5% vs app/website about 24%.
3. **Slow refunds hurt.** CSAT by refund time: 6-9 days 3.99, 9-12 days 3.61, 12+ days 2.88; tickets per return rise from 0.8 to 2.0.
4. **Quality returns are costly.** Defects are 10.5% of returns but 22% of return cost (INR 10.2 lakh), because most are graded C or Reject and cannot be resold. This points to a supplier-quality loop.
5. **Value loss dominates cost:** unrecovered product value INR 28.0 lakh (60%), reverse + lost forward shipping 9.3, support 4.3, handling and QC 3.9, payment gateway 1.0.
6. **Wardrobing/misuse is 5.8% of returns;** 78 of 3,212 repeat customers (3+ orders) return two-thirds or more of what they buy.

## 6. Future state (to-be)
See `outputs/process_to_be.png`. Self-serve return with a size prompt, rules-based approval, API pickup booking, scan-triggered QC with fast-track for low-risk items, auto-refund on QC pass (instant for trusted prepaid customers), and status notifications at each stage. Exceptions (fraud flags, disputes) go to a human queue.

## 7. Requirements
### 7.1 Functional
| ID | Requirement | Priority |
|---|---|---|
| FR-01 | Customer can raise a return in the app/website with reason selection and photo upload for defect/wrong-item reasons | Must |
| FR-02 | Rules engine auto-approves returns that meet policy (window, condition, category) and routes others to an agent | Must |
| FR-03 | System books reverse pickup with the 3PL by API and shares tracking with the customer | Must |
| FR-04 | Receiving scan creates a QC task and timestamps warehouse receipt | Must |
| FR-05 | Guided QC checklist assigns grade A/B/C/Reject; fast-track path for low-risk categories and customers | Must |
| FR-06 | Refund triggers automatically on QC pass; refund method follows original payment (COD: to bank/UPI after verification) | Must |
| FR-07 | Instant refund option for trusted prepaid customers at pickup scan (risk rules defined by Finance) | Should |
| FR-08 | Notifications (SMS/WhatsApp/app) at request, pickup, receipt, QC result, refund | Must |
| FR-09 | Fit-guide prompt shown on product pages and at checkout for footwear, jeans and jackets, with size recommendation | Should |
| FR-10 | Fraud flags: repeat-return ratio, wardrobing indicators; flagged returns go to exception queue | Should |
| FR-11 | Dashboard with the KPIs in section 8, refreshed daily | Must |
| FR-12 | Defect returns feed a supplier-quality report by supplier and part | Could |

### 7.2 Non-functional
Refund and QC events logged for audit; PII handled under the company's data policy; notification delivery within 5 minutes of the event; system supports 3x current monthly return volume; 99.5% availability for the customer-facing return flow.

### 7.3 User stories (selection)
- **US-1** As a customer, I want to return an item in a few taps and see its status, so that I don't need to call support. *Acceptance:* return raised in under 2 minutes; status visible at each stage; no support call needed for in-policy returns.
- **US-2** As a QC associate, I want a guided checklist on a handheld, so that grading is consistent and fast. *Acceptance:* grade recorded within 24 hours of receipt for 90% of items; grade and photo stored against the return.
- **US-3** As a Finance controller, I want refunds to release automatically with fraud rules, so that I don't verify each refund. *Acceptance:* auto-release only for QC pass; flagged returns held; monthly audit sample shows under 0.5% erroneous refunds.
- **US-4** As a support agent, I want to see the full return timeline, so that I can answer "where is my refund?" in one touch.

## 8. KPI framework
| KPI | Definition | Baseline | Target | Owner |
|---|---|---|---|---|
| Return rate | Returned orders / delivered orders | 24.9% | 21% | Head of Product |
| Fit-return share | Size/fit returns / all returns | 43.7% | 35% | Head of Product |
| Refund TAT | Request to refund (days, average and P90) | 12.8 avg, 17.5 P90 | 7 avg | COO |
| QC wait | Receipt to grading (days) | 3.6 | 1.0 | Warehouse mgr |
| Touchpoints per return | Manual hand-offs | 5.0 | 2 | COO |
| Tickets per return | Support tickets / returns | 1.6 | 0.6 | Support head |
| Returns CSAT | Post-refund survey | 3.3 | 4.0 | Support head |
| Cost per return | Total return cost / returns | INR 777 | INR 650 | Finance |

## 9. Cost-benefit analysis
Savings are estimated from the dataset with stated assumptions (see `src/analysis.py`). Cost per avoided return uses the average cost per return (INR 777). QC automation saves 60% (base) of manual QC cost per return plus a share of delay-driven ticket cost. Instant refund removes a share of prepaid-customer tickets.

| Scenario | Fit-guide adoption among non-users | Fit guide | QC automation | Instant refund | Annual savings (INR lakh) |
|---|---|---|---|---|---|
| Low | +15% | 3.8 | 3.2 | 0.6 | 7.6 |
| **Base** | **+30%** | **7.4** | **4.8** | **1.2** | **13.4** |
| High | +45% | 11.2 | 6.0 | 1.6 | 18.8 |

**Investment (assumed):** fit tool INR 9.0 lakh a year; QC workflow INR 6.0 lakh one-time + 1.5 lakh a year; refund integration INR 3.0 lakh one-time. Year 1 total **INR 19.5 lakh**; recurring thereafter INR 10.5 lakh a year.

| Scenario | Net year 1 | Net year 2 | Payback |
|---|---|---|---|
| Low | -11.9 | -2.9 | beyond 24 months |
| Base | -6.1 | +2.9 | about 17.5 months |
| High | -0.7 | +8.3 | about 12.5 months |

**Honest reading:** on hard savings alone, the business case is **marginal in the base case** and negative if adoption is low. It becomes attractive only if adoption is high, or when benefits not counted here are included: repeat purchase from happier customers (CSAT 2.9 vs 4.0), supplier chargebacks on defect returns (INR 10.2 lakh of return cost), and lower fraud losses. These are not quantified because the dataset has no retention or chargeback data. **Recommendation:** run a staged pilot rather than a full build, with go/no-go gates below.

## 10. Implementation roadmap
| Phase | Weeks | Scope | Gate to proceed |
|---|---|---|---|
| 1. Quick wins | 1-6 | QC checklist and scan-triggered QC (no new tech), status notifications, daily KPI dashboard | QC wait under 2 days; tickets per return down 20% |
| 2. Pilot | 7-14 | Auto-approval and auto-refund; fit guide on Jeans and Sneakers only | Fit-return share down 3 points in pilot categories; refund errors under 0.5% |
| 3. Scale | 15-26 | Extend to all categories, instant refund for trusted prepaid, 3PL API | Base-case savings run-rate confirmed |

## 11. Risks and assumptions
| Risk / assumption | Impact | Mitigation |
|---|---|---|
| Size-guide effect is correlation, not cause (guide users may be more careful buyers) | Savings overstated | A/B test in pilot before scaling spend |
| Customers abuse instant refunds | Loss from fraud | Limit to trusted customers; cap value; audit |
| 3PL cannot support API booking | Delays phase 3 | Interim file-based booking; vendor SLA |
| Warehouse adoption of handhelds | QC gains not realised | Training, floor champions, weekly review |
| Cost figures are assumptions (reverse pickup INR 85, forward shipping lost 70, QC 30, handling 35, ticket 45, gateway 2%) | Cost estimates shift | Replace with finance actuals before approval |
| Dataset is synthetic | Findings illustrate method | Re-run `src/analysis.py` on real data |

## 12. Open questions
1. What is the current return window by category, and is it changing?
2. Can Finance approve auto-refund rules and a value cap for instant refunds?
3. Who owns supplier chargebacks for defect returns?
4. Is retention data available to size the CSAT-to-repeat-purchase benefit?
