import numpy as np
import pandas as pd

# ---------------------------------------------------------
# XIRR FUNCTION (Stable, Safe, Handles Edge Cases)
# ---------------------------------------------------------
def xirr(cashflows, dates, guess=0.1):
    """Compute XIRR using Newton's method."""
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

        if df == 0:
            return None

        new_rate = rate - f / df
        if abs(new_rate - rate) < 1e-7:
            return new_rate

        rate = new_rate

    return None


# ---------------------------------------------------------
# MERGE NAV + PORTFOLIO
# ---------------------------------------------------------
def merge_nav_with_portfolio(portfolio_df, nav_df, mutual_funds):
    # Normalize fund names
    portfolio_df["FundName"] = (
        portfolio_df["FundName"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Normalize mutual fund dict
    mf_map = {k.lower().strip(): v for k, v in mutual_funds.items()}

    # Map SchemeCode
    portfolio_df["SchemeCode"] = portfolio_df["FundName"].map(mf_map)

    # Merge
    merged = portfolio_df.merge(
        nav_df[["SchemeCode", "NAV", "Date"]],
        on="SchemeCode",
        how="left",
        suffixes=("_Purchase", "_Latest")
    )

    # Rename
    merged.rename(
        columns={
            "NAV_Latest": "LatestNAV",
            "Date_Latest": "LatestNAVDate"
        },
        inplace=True
    )

    return merged


# ---------------------------------------------------------
# SUMMARY CALCULATIONS (Portfolio + XIRR)
# ---------------------------------------------------------
def calculate_summary(df):
    # Basic calculations
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

    # XIRR calculation per fund
    xirr_values = []

    for fund in summary["FundName"]:
        fdf = df[df["FundName"] == fund]

        # Cashflows: investments must be negative
        cashflows = list(-fdf["Amount"].abs())

        # Dates
        dates = list(fdf["Date_Purchase"])

        # Add final value as positive cashflow
        final_value = fdf["Units"].sum() * fdf["LatestNAV"].iloc[-1]
        final_date = fdf["LatestNAVDate"].iloc[-1]

        cashflows.append(final_value)
        dates.append(final_date)

        # Compute XIRR
        try:
            rate = xirr(cashflows, dates)
            xirr_values.append(rate * 100 if rate is not None else None)
        except:
            xirr_values.append(None)

    summary["XIRR"] = xirr_values

    return summary
