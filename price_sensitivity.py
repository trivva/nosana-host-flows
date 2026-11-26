"""
Do Nosana hosts sell more when the NOS price moves? (v2)

Daily panel, 13 Aug - 25 Nov 2026:
  - host payouts (NOS received from job vaults)
  - host sales: NOS sent directly to sale venues (Kraken, DEX pools/routers, Jupiter)
  - NOS price and volume (CoinGecko daily snapshots)

Dependent variable: sell ratio = NOS sold on day t / average daily payouts over the previous 7 days.
Dividing by recent payouts removes the mechanical effect of network activity (more jobs -> more NOS to sell).

Sales are lumpy (median ratio ~0.13, max ~15: a few large batch sales), so the main specification uses
log(1 + sell_ratio); the raw ratio is kept as a robustness check.

Models (OLS, Newey-West standard errors with 5 lags because daily flows are autocorrelated):
  (1) log(1 + sell_ratio_t) = a + b1 r_t + b2 r_(t-1) + b3 r7_(t-1)
  (2) same, for the top 10% hosts and the other 90% separately
  (3) sell_ratio_t = a + c log(price_t / 30-day average price)   (do hosts sell more when NOS is "expensive"?)
where r_t = daily log return, r7_(t-1) = log return over the 7 days up to t-1.

Implemented with numpy only (OLS + Newey-West by hand, Spearman via ranks).
Outputs: output/price_sensitivity.csv, output/price_vs_sales.png, printed summary
"""
from math import erf, sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).parent
D, OUT = ROOT / "data", ROOT / "output"
SPLIT, END = pd.Timestamp("2026-08-28"), pd.Timestamp("2026-11-24")   # last day with a full close price
SALE = {"cex", "dex"}
EXTRA_DEX = {"66y7ViQ6mUyYa1sPDRrroPuAAuTeN1Cb4jKb6FEE5sR1", "8ZPyVHWS2gom2AAkiy8WGpQHLvo2mSnkxJ7UYznDz6EV"}

# ---------- data ----------
r1 = pd.read_csv(D / "archive_2026-11-11/q6a_received_per_host_day.csv", parse_dates=["day"])
s1 = pd.read_csv(D / "archive_2026-11-11/q6b_sent_per_host_day.csv", parse_dates=["day"]).assign(dest="")
r2 = pd.read_csv(D / "q8a_received_per_host_day_v2.csv", parse_dates=["day"])
s2 = pd.read_csv(D / "q8b_sent_per_host_day_v2.csv", parse_dates=["day"]).fillna({"dest": ""})
rec = pd.concat([r1[r1.day < SPLIT], r2[r2.day >= SPLIT]])
snt = pd.concat([s1[s1.day < SPLIT], s2[s2.day >= SPLIT]])
snt.loc[snt.dest.isin(EXTRA_DEX), "category"] = "dex"
snt = snt[snt.category.isin(SALE)]

per_host = rec.groupby("host").received.sum().sort_values(ascending=False)
big = set(per_host.index[:round(len(per_host) * 0.10)])

# CoinGecko snapshot at 00:00 UTC on day D = close of day D-1
px = pd.read_csv(D / "nos_usd_coingecko.csv")
px["day"] = pd.to_datetime(px.event_date.str[:10]) - pd.Timedelta(days=1)
px = px.set_index("day")[["close_price_usd", "volume_usd"]].rename(columns={"close_price_usd": "price", "volume_usd": "vol_usd"})

days = pd.date_range(rec.day.min(), END)
df = pd.DataFrame(index=days)
df["payouts"] = rec.groupby("day").received.sum().reindex(days).fillna(0)
df["sold"] = snt.groupby("day").sent.sum().reindex(days).fillna(0)
df["sold_kraken"] = snt[snt.category == "cex"].groupby("day").sent.sum().reindex(days).fillna(0)
df["sold_big"] = snt[snt.host.isin(big)].groupby("day").sent.sum().reindex(days).fillna(0)
df["sold_small"] = snt[~snt.host.isin(big)].groupby("day").sent.sum().reindex(days).fillna(0)
df["pay_big"] = rec[rec.host.isin(big)].groupby("day").received.sum().reindex(days).fillna(0)
df["pay_small"] = rec[~rec.host.isin(big)].groupby("day").received.sum().reindex(days).fillna(0)
df = df.join(px)

df["r"] = np.log(df.price).diff()
df["r_lag"] = df.r.shift(1)
df["r7_lag"] = np.log(df.price).diff(7).shift(1)
df["rich"] = np.log(df.price / df.price.rolling(30, min_periods=10).mean())
for seg, pay in (("", "payouts"), ("_big", "pay_big"), ("_small", "pay_small")):
    base = df[pay].rolling(7).mean().shift(1)
    df[f"ratio{seg}"] = df[f"sold{seg}"] / base.where(base > 0)
df["sold_usd"] = df.sold * df.price
df["share_of_volume"] = df.sold_usd / df.vol_usd


# ---------- stats helpers ----------
def pval(t):
    return 2 * (1 - 0.5 * (1 + erf(abs(t) / sqrt(2))))


def ols_nw(y, X, lags=5):
    """OLS coefficients with Newey-West (HAC) standard errors."""
    X = np.column_stack([np.ones(len(X)), X])
    XtX_inv = np.linalg.inv(X.T @ X)
    b = XtX_inv @ X.T @ y
    u = y - X @ b
    Xu = X * u[:, None]
    S = Xu.T @ Xu
    for l in range(1, lags + 1):
        w = 1 - l / (lags + 1)                        # Bartlett kernel
        G = Xu[l:].T @ Xu[:-l]
        S += w * (G + G.T)
    se = np.sqrt(np.diag(XtX_inv @ S @ XtX_inv))
    r2 = 1 - (u @ u) / ((y - y.mean()) @ (y - y.mean()))
    return b, se, r2


def spearman(a, b):
    ra, rb = pd.Series(a).rank().values, pd.Series(b).rank().values
    return np.corrcoef(ra, rb)[0, 1]


# ---------- models ----------
rows = []
print(f"Days: {df.index.min():%d %b} -> {df.index.max():%d %b %Y}")
print(f"Host direct sales: {df.sold.sum():,.0f} NOS, ~${df.sold_usd.sum() / len(df):,.0f}/day, "
      f"median {df.share_of_volume.median():.2%} of NOS daily volume (max {df.share_of_volume.max():.1%})")

print("\nSpearman correlation, sell ratio vs:")
d = df.dropna(subset=["ratio", "r", "r_lag", "r7_lag"])
for v in ("r", "r_lag", "r7_lag", "rich"):
    dd = df.dropna(subset=["ratio", v])
    rho = spearman(dd.ratio, dd[v])
    print(f"  {v:7}: rho = {rho:+.2f}  (n={len(dd)})")
    rows.append({"model": "spearman", "segment": "all", "var": v, "coef": rho, "se": None, "p": None, "n": len(dd)})

names = ["const", "r_t", "r_(t-1)", "r7_(t-1)"]
for spec, f in (("log1p", np.log1p), ("raw", lambda x: x)):
    for seg in ("", "_big", "_small"):
        dd = df.dropna(subset=[f"ratio{seg}", "r", "r_lag", "r7_lag"])
        b, se, r2 = ols_nw(f(dd[f"ratio{seg}"].values), dd[["r", "r_lag", "r7_lag"]].values)
        label = {"": "all hosts", "_big": "top 10%", "_small": "other 90%"}[seg]
        print(f"\nOLS {spec}(sell ratio), {label}, n={len(dd)}, R2={r2:.2f}, Newey-West SE (5 lags)")
        for n_, bi, si in zip(names, b, se):
            print(f"  {n_:9} {bi:+7.3f}  (se {si:.3f}, p={pval(bi / si):.3f})")
            rows.append({"model": f"ols_returns_{spec}", "segment": label, "var": n_, "coef": bi, "se": si,
                         "p": pval(bi / si), "n": len(dd), "r2": r2})

print()
for seg in ("", "_big", "_small"):
    dd = df.dropna(subset=[f"ratio{seg}", "rich"])
    b, se, r2 = ols_nw(np.log1p(dd[f"ratio{seg}"].values), dd[["rich"]].values)
    label = {"": "all hosts", "_big": "top 10%", "_small": "other 90%"}[seg]
    print(f"OLS log1p(sell ratio) on log(price / 30d avg) ({label}): {b[1]:+.3f} (se {se[1]:.3f}, p={pval(b[1] / se[1]):.3f}), n={len(dd)}")
    rows.append({"model": "ols_rich_log1p", "segment": label, "var": "log(price/30d avg)", "coef": b[1], "se": se[1],
                 "p": pval(b[1] / se[1]), "n": len(dd), "r2": r2})

# terciles of the trailing 7-day return
t = df.dropna(subset=["ratio", "r7_lag"]).copy()
t["trailing_week"] = pd.qcut(t.r7_lag, 3, labels=["down", "flat", "up"])
terc = t.groupby("trailing_week", observed=True).agg(
    avg_7d_return=("r7_lag", "mean"), median_ratio_all=("ratio", "median"),
    median_ratio_top10=("ratio_big", "median"), median_ratio_other90=("ratio_small", "median"), days=("ratio", "size"))
print("\nMedian sell ratio by trailing 7-day return tercile:")
print(terc.round(2).to_string())
terc.to_csv(OUT / "sell_ratio_by_trailing_return.csv")

# simple contrast: sell ratio on up days vs down days
up, down = d[d.r > 0].ratio, d[d.r <= 0].ratio
print(f"\nMean sell ratio: up days {up.mean():.2f} (n={len(up)}) vs down days {down.mean():.2f} (n={len(down)})")

pd.DataFrame(rows).to_csv(OUT / "price_sensitivity.csv", index=False)
df.to_csv(OUT / "daily_panel.csv", index_label="day")

# ---------- chart ----------
# Daily bars, not a rolling mean: sales come in one-day blocks, smoothing would spread them over a week
DARK, LIGHT, GRID = "#1f4e9c", "#9cc3ee", "#e6e5e0"
other = df.sold - df.sold_kraken
fig, ax = plt.subplots(figsize=(7.5, 3.8), dpi=200)
ax.bar(df.index, df.sold_kraken / 1e3, color=DARK, width=0.9, label="Kraken deposits (one operator)")
ax.bar(df.index, other / 1e3, bottom=df.sold_kraken / 1e3, color=LIGHT, width=0.9, label="DEX sales (incl. Jupiter), all hosts")
ax.set_ylabel("NOS sold per day (thousands)")
ax2 = ax.twinx()
ax2.plot(df.index, df.price, color="#0b0b0b", linewidth=1.5, label="NOS price (USD, daily close)")
ax2.set_ylabel("NOS price (USD)")
ax2.set_ylim(0, df.price.max() * 1.1)
ax.set_title("Host sales come in one-day blocks (13 Aug - 24 Nov 2026)", loc="left", fontsize=11, fontweight="bold")
for a_ in (ax, ax2):
    a_.spines["top"].set_visible(False)
ax.grid(axis="y", color=GRID)
ax.set_axisbelow(True)
h1, l1 = ax.get_legend_handles_labels()
h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc="upper right", fontsize=7.5, frameon=False)
fig.autofmt_xdate()
fig.tight_layout()
fig.savefig(OUT / "price_vs_sales.png")
