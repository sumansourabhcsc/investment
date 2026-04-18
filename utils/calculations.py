import numpy as np
import pandas as pd


# -----------------------------
# XIRR
# -----------------------------
def xirr(cashflows, dates, guess=0.1):
    def npv(rate):
        return sum(
            cf / ((1 + rate) ** ((d - dates[0]).days / 365))
            for cf, d in zip(cashflows, dates)
        )

    rate = guess
    for _ in range(100):
        f = npv(rate)

        df = sum(
            -((d - dates[0]).days / 365) * cf /
            ((1 + rate) ** (((d - dates[0]).days / 365) + 1))
            for cf, d in zip(cashflows, dates)
        )

        if abs(df) < 1e-10:
            return None

        new_rate = rate - f / df

        if new_rate < -0.9999 or new_rate > 10:
            return None

        if abs(new_rate - rate) < 1e-6:
            return new_rate

        rate = new_rate

    return None


# -----------------------------
# MERGE
# -----------------------------
def merge_nav_with_portfolio(portfolio_df, nav_df, mutual_funds):

    portfolio_df["FundName"] = portfolio_df["FundName"].str.strip().str.lower()
    mf_map = {k.lower().strip(): v for k, v in mutual_funds.items()}

    portfolio_df["SchemeCode"] = portfolio_df["FundName"].map(mf_map)

    portfolio_df["SchemeCode"] = portfolio_df["SchemeCode"].astype(str)
    nav_df["SchemeCode"] = nav_df["SchemeCode"].astype(str)

    merged = portfolio_df.merge(
        nav_df[["SchemeCode", "NAV", "Date"]],
        on="SchemeCode",
        how="left"
    )

    merged.rename(columns={
        "NAV": "LatestNAV",
        "Date": "LatestNAVDate"
    }, inplace=True)

    return merged


# -----------------------------
# SUMMARY
# -----------------------------
def calculate_summary(df):

    df = df.dropna(subset=["LatestNAV", "LatestNAVDate", "Date_Purchase"])

    df["CurrentValue"] = df["Units"] * df["LatestNAV"]
    df["Invested"] = df["Amount"]

    summary = df.groupby("FundName").agg({
        "Invested": "sum",
        "CurrentValue": "sum",
        "LatestNAV": "last",
        "LatestNAVDate": "last"
    }).reset_index()

    summary["ProfitLoss"] = summary["CurrentValue"] - summary["Invested"]
    summary["ReturnPct"] = (summary["ProfitLoss"] / summary["Invested"]) * 100

    xirr_values = []

    for fund in summary["FundName"]:
        fdf = df[df["FundName"] == fund]

        cashflows = list(-fdf["Amount"].abs())
        dates = list(fdf["Date_Purchase"])

        latest_nav = fdf["LatestNAV"].iloc[-1]

        final_value = fdf["Units"].sum() * latest_nav
        final_date = fdf["LatestNAVDate"].iloc[-1]

        cashflows.append(final_value)
        dates.append(final_date)

        if not (any(c > 0 for c in cashflows) and any(c < 0 for c in cashflows)):
            xirr_values.append(None)
            continue

        rate = xirr(cashflows, dates)
        xirr_values.append(rate * 100 if rate else None)

    summary["XIRR"] = [
        f"{x:.2f}%" if x is not None else "N/A"
        for x in xirr_values
    ]

    return summary
