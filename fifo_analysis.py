"""
How long do Nosana hosts keep the NOS they earn, and where does it go?

FIFO method (first in, first out), per host:
- every payout day creates a "lot" of received NOS;
- every NOS outflow consumes the oldest lots first;
- for each NOS consumed we record the holding time (days) and the destination category.

Inputs : data/q6a_received_per_host_day.csv, data/q6b_sent_per_host_day.csv (CDP SQL exports)
Outputs: output/*.csv, output/*.png, printed summary
"""
from collections import deque
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).parent
OUT = ROOT / "output"
OUT.mkdir(exist_ok=True)

SALE = {"cex", "dex"}                                  # direct sale venues
PROBABLE_SALE = SALE | {"consolidated_emptied"}        # + consolidation wallets that were emptied
ALL_EXITS = PROBABLE_SALE | {"consolidated_kept", "other"}
END = pd.Timestamp("2026-11-11")                       # last day of data

received = pd.read_csv(ROOT / "data/q6a_received_per_host_day.csv", parse_dates=["day"])
sent = pd.read_csv(ROOT / "data/q6b_sent_per_host_day.csv", parse_dates=["day"])

# ---------- 1. FIFO per host ----------
consumed = []      # host, day_received, day_sent, holding_days, category, nos
remaining = []     # lots never sent out: host, day_received, nos
unmatched = {}     # outflows with no lot available (NOS held before the period or from other sources)

for host, r in received.groupby("host"):
    lots = deque([[d, a] for d, a in r.sort_values("day")[["day", "received"]].itertuples(index=False)])
    events = sent[sent.host == host].sort_values("day")
    queue = deque()
    for d, cat, amt in events[["day", "category", "sent"]].itertuples(index=False):
        # add lots received up to this day (assumption: received before sent on the same day)
        while lots and lots[0][0] <= d:
            queue.append(lots.popleft())
        left = amt
        while left > 1e-9 and queue:
            lot = queue[0]
            take = min(left, lot[1])
            consumed.append((host, lot[0], d, (d - lot[0]).days, cat, take))
            lot[1] -= take
            left -= take
            if lot[1] <= 1e-9:
                queue.popleft()
        if left > 1e-9:
            unmatched[cat] = unmatched.get(cat, 0) + left
    for lot in list(queue) + list(lots):
        if lot[1] > 1e-9:
            remaining.append((host, lot[0], lot[1]))

c = pd.DataFrame(consumed, columns=["host", "day_received", "day_sent", "holding_days", "category", "nos"])
rem = pd.DataFrame(remaining, columns=["host", "day_received", "nos"])
c.to_csv(OUT / "fifo_outflows.csv", index=False)
rem.to_csv(OUT / "fifo_still_held.csv", index=False)

total = received.received.sum()
print(f"NOS received by hosts: {total:,.0f}  ({received.host.nunique()} hosts, "
      f"{received.day.min():%d %b} -> {received.day.max():%d %b %Y})")
print(f"  sent out (FIFO)   : {c.nos.sum():,.0f}  ({c.nos.sum()/total:.0%})")
print(f"  still held        : {rem.nos.sum():,.0f}  ({rem.nos.sum()/total:.0%})")
print(f"  outflows not matched to a payout in the period: {sum(unmatched.values()):,.0f}")

order = ["cex", "dex", "consolidated_emptied", "consolidated_kept", "other"]
dest = c.groupby("category").nos.sum().reindex(order).fillna(0)
print("\nDestination of NOS received (FIFO):")
for k, v in dest.items():
    print(f"  {k:22} {v:>10,.0f}  {v/total:6.1%}")
print(f"  {'still held':22} {rem.nos.sum():>10,.0f}  {rem.nos.sum()/total:6.1%}")


# ---------- 2. Share sent out within N days (right-censoring corrected) ----------
def share_within(days: int, cats: set) -> tuple[float, float]:
    """Share of NOS received at least `days` days before the end of the data that left to `cats` within `days`."""
    cutoff = END - pd.Timedelta(days=days)
    base = received[received.day <= cutoff].received.sum()
    hit = c[(c.day_received <= cutoff) & (c.holding_days <= days) & (c.category.isin(cats))].nos.sum()
    return hit / base, base


print("\nShare of received NOS leaving within N days:")
rows = []
for n in (1, 7, 30):
    s_sale, base = share_within(n, SALE)
    s_prob, _ = share_within(n, PROBABLE_SALE)
    s_any, _ = share_within(n, ALL_EXITS)
    rows.append({"days": n, "direct_sale": s_sale, "probable_sale": s_prob, "any_outflow": s_any, "base_nos": base})
    print(f"  {n:>2} d: direct sale {s_sale:5.1%} | probable sale {s_prob:5.1%} | "
          f"any outflow {s_any:5.1%}   (base {base:,.0f} NOS)")
pd.DataFrame(rows).to_csv(OUT / "share_out_within_n_days.csv", index=False)

# ---------- 3. Large vs small hosts ----------
per_host = received.groupby("host").received.sum().sort_values(ascending=False)
top_n = max(1, round(len(per_host) * 0.10))
big = set(per_host.index[:top_n])
print(f"\nTop 10% of hosts ({top_n}) = {per_host.iloc[:top_n].sum()/total:.0%} of NOS received")

seg_rows = []
for name, hosts in (("top 10%", big), ("other 90%", set(per_host.index) - big)):
    rcv = received[received.host.isin(hosts)]
    cc = c[c.host.isin(hosts)]
    cutoff = END - pd.Timedelta(days=30)
    base = rcv[rcv.day <= cutoff].received.sum()
    sold30 = cc[(cc.day_received <= cutoff) & (cc.holding_days <= 30) & cc.category.isin(PROBABLE_SALE)].nos.sum()
    sales = cc[cc.category.isin(PROBABLE_SALE)].sort_values("holding_days")
    median_days = sales[sales.nos.cumsum() >= sales.nos.sum() / 2].holding_days.iloc[0] if len(sales) else None
    seg_rows.append({"segment": name, "hosts": len(hosts), "nos_received": rcv.received.sum(),
                     "probable_sale_30d": sold30 / base if base else None, "median_days_to_sale": median_days})
    print(f"  {name:9}: {len(hosts):>3} hosts, {rcv.received.sum():>9,.0f} NOS received, "
          f"sold within 30 d: {sold30/base:5.1%}, median days to sale: {median_days}")
pd.DataFrame(seg_rows).to_csv(OUT / "segments.csv", index=False)

# ---------- 4. Holding curve (amount-weighted Kaplan-Meier, any outflow) ----------
lots_all = pd.concat([
    c.assign(event=1, t=c.holding_days)[["t", "nos", "event"]],
    rem.assign(event=0, t=(END - rem.day_received).dt.days)[["t", "nos", "event"]],
])
surv, s = [], 1.0
for t in range(0, 61):
    at_risk = lots_all[lots_all.t >= t].nos.sum()
    ev = lots_all[(lots_all.t == t) & (lots_all.event == 1)].nos.sum()
    if at_risk > 0:
        s *= 1 - ev / at_risk
    surv.append((t, s))
sv = pd.DataFrame(surv, columns=["days", "share_still_held"])
sv.to_csv(OUT / "holding_curve.csv", index=False)
print("\nShare still held (Kaplan-Meier, any outflow): "
      + ", ".join(f"{d} d = {sv.share_still_held[d]:.0%}" for d in (1, 7, 30, 60)))

# ---------- 5. Charts ----------
BLUE, GRID = "#2a78d6", "#e6e5e0"

fig, ax = plt.subplots(figsize=(7, 3.6), dpi=200)
ax.step(sv.days, sv.share_still_held * 100, where="post", color=BLUE, linewidth=2)
ax.set_ylim(0, 100)
ax.set_xlabel("Days after receipt")
ax.set_ylabel("% of NOS still in host wallet")
ax.set_title("How long Nosana hosts hold the NOS they earn", loc="left", fontsize=11, fontweight="bold")
ax.grid(axis="y", color=GRID)
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "holding_curve.png")

labels = {"cex": "Exchange (Kraken)", "dex": "DEX", "consolidated_emptied": "Consolidated, then moved on",
          "consolidated_kept": "Consolidated and kept", "other": "Other / unlabelled"}
d2 = dest.rename(labels)
d2["Still with the host"] = rem.nos.sum()
d2 = d2.sort_values()
fig, ax = plt.subplots(figsize=(7, 3.2), dpi=200)
ax.barh(d2.index, d2.values / total * 100, color=BLUE, height=0.6)
for i, v in enumerate(d2.values / total * 100):
    ax.text(v + 0.5, i, f"{v:.0f}%", va="center", fontsize=9)
ax.set_xlabel("% of NOS paid to hosts")
ax.set_title("Where NOS paid to hosts goes (Aug - Nov 2026)", loc="left", fontsize=11, fontweight="bold")
for side in ("top", "right"):
    ax.spines[side].set_visible(False)
fig.tight_layout()
fig.savefig(OUT / "destinations.png")
