"""Draw as-is and to-be returns process maps (swimlanes) with matplotlib."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle
from pathlib import Path
import textwrap
O = Path(__file__).resolve().parents[1]/"outputs"
BLUE, ORANGE, INK, MUTED, GRID, AQUA = "#2a78d6", "#eb6834", "#0b0b0b", "#52514e", "#e6e5e1", "#1baf7a"

def draw(title, lanes, steps, arrows, fname, pain=None):
    fig, ax = plt.subplots(figsize=(13, 6.2)); ax.set_xlim(0, 13); ax.set_ylim(0, len(lanes)); ax.axis("off")
    for i, l in enumerate(lanes):
        y = len(lanes) - 1 - i
        ax.add_patch(Rectangle((0, y), 13, 1, fill=False, edgecolor=GRID, lw=1))
        ax.add_patch(Rectangle((0, y), 1.25, 1, facecolor="#f3f2ee", edgecolor=GRID, lw=1))
        ax.text(.62, y + .5, l, ha="center", va="center", fontsize=8, color=INK, wrap=True, fontweight="bold")
    pos = {}
    for sid, (lane, x, text, kind) in steps.items():
        y = len(lanes) - 1 - lane + .5; pos[sid] = (x, y)
        col = {"std": "white", "pain": "#fde6dc", "good": "#dff3ea", "decision": "#e7effb"}[kind]
        ec = {"std": MUTED, "pain": ORANGE, "good": AQUA, "decision": BLUE}[kind]
        ax.add_patch(FancyBboxPatch((x - .8, y - .33), 1.6, .66, boxstyle="round,pad=0.02,rounding_size=.08", facecolor=col, edgecolor=ec, lw=1.3))
        ax.text(x, y, textwrap.fill(text, 21), ha="center", va="center", fontsize=6.4, color=INK, linespacing=1.15)
    for a, b, lab in arrows:
        (x1, y1), (x2, y2) = pos[a], pos[b]
        sx, ex = (x1 + .8, x2 - .8) if x2 > x1 else ((x1, x2) if abs(x2 - x1) < .1 else (x1 - .8, x2 + .8))
        if abs(x2 - x1) < .1: sy, ey = (y1 - .33, y2 + .33) if y2 < y1 else (y1 + .33, y2 - .33)
        else: sy, ey = y1, y2
        ax.annotate("", xy=(ex, ey), xytext=(sx, sy), arrowprops=dict(arrowstyle="-|>", color=MUTED, lw=1.1, shrinkA=0, shrinkB=0))
        if lab: ax.text((sx + ex)/2, (sy + ey)/2 + .1, lab, fontsize=6.3, color=BLUE, ha="center")
    ax.set_title(title, loc="left", fontsize=11, color=INK, pad=8)
    if pain: ax.text(0, -.12, pain, fontsize=7.5, color=MUTED, transform=ax.transData)
    fig.tight_layout(); fig.savefig(O/fname); plt.close()

lanes = ["Customer", "Support team", "Logistics partner", "Warehouse / QC", "Finance"]
as_is = {
 "a": (0, 2.3, "Raises return on app / calls support", "std"),
 "b": (1, 2.3, "Agent checks order, reason and policy manually", "pain"),
 "c": (1, 4.2, "Agent emails pickup request to 3PL", "pain"),
 "d": (2, 4.2, "Reverse pickup (avg 3.2 days)", "pain"),
 "e": (3, 6.1, "Parcel received; wait in unsorted pile (3.5 days)", "pain"),
 "f": (3, 8.0, "Manual QC grading on paper / sheet (3.6 days)", "pain"),
 "g": (3, 10.0, "Grade shared by email to Finance", "pain"),
 "h": (4, 10.0, "Finance verifies and triggers refund (2.5 days)", "pain"),
 "i": (0, 11.8, "Refund received; 'where is my refund?' tickets", "pain"),
}
as_arrows = [("a","b",""),("b","c",""),("c","d",""),("d","e",""),("e","f",""),("f","g",""),("g","h",""),("h","i","")]
draw("AS-IS: Returns & refund process (avg 12.8 days, 5 manual touchpoints)", lanes, as_is, as_arrows, "process_as_is.png",
     "Pain points (orange): manual policy checks, email hand-offs, no visibility for customer, QC queue, refund waits for batch verification.")
to_be = {
 "a": (0, 2.3, "Self-serve return in app with reason + size prompt", "good"),
 "b": (1, 2.3, "Auto-rules engine approves in-policy returns", "good"),
 "c": (2, 4.2, "Pickup auto-booked via API; tracking shared", "good"),
 "d": (3, 6.1, "Scan at receipt triggers QC task", "good"),
 "e": (3, 8.0, "Guided QC checklist; fast-track for low-risk items", "good"),
 "f": (1, 8.0, "Exceptions (fraud flags, disputes) reviewed here", "decision"),
 "g": (4, 10.0, "Auto-refund on QC pass; instant for trusted prepaid", "good"),
 "h": (0, 11.8, "Status notifications at every stage; refund confirmed", "good"),
}
to_arrows = [("a","b",""),("b","c","approved"),("c","d",""),("d","e",""),("e","g","pass"),("e","f","flag"),("g","h","")]
draw("TO-BE: Automated returns workflow (target 6 days, 2 manual touchpoints)", lanes, to_be, to_arrows, "process_to_be.png",
     "Changes: rules-based approval, API pickup booking, scan-triggered QC with fast-track, auto-refund, proactive notifications.")
print("done")
