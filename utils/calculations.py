#utils/calculations.py — MERGE NAV + PORTFOLIO
def merge_nav_with_portfolio(portfolio_df, nav_df, mutual_funds):
    # -------------------------------
    # 1. Normalize fund names
    # -------------------------------
    portfolio_df["FundName"] = (
        portfolio_df["FundName"]
        .astype(str)
        .str.strip()
        .str.lower()
    )

    # Normalize mutual_funds dict keys
    mf_map = {k.lower().strip(): v for k, v in mutual_funds.items()}

    # -------------------------------
    # 2. Map SchemeCode
    # -------------------------------
    portfolio_df["SchemeCode"] = portfolio_df["FundName"].map(mf_map)

    # -------------------------------
    # 3. Merge with NAV data
    # -------------------------------
    merged = portfolio_df.merge(
        nav_df[["SchemeCode", "NAV", "Date"]],
        on="SchemeCode",
        how="left",
        suffixes=("_Purchase", "_Latest")
    )

    # -------------------------------
    # 4. Rename columns
    # -------------------------------
    merged.rename(
    columns={
        "NAV_Latest": "LatestNAV",
        "Date_Latest": "LatestNAVDate"
    },
    inplace=True
    )


    return merged



#utils/calculations.py — SUMMARY CALCULATIONS
def calculate_summary(df):
    # Calculate values
    df["CurrentValue"] = df["Units"] * df["NAV_Latest"]
    df["Invested"] = df["Amount"]

    # Build summary table with latest NAV + date included
    summary = df.groupby("FundName").agg({
        "Invested": "sum",
        "CurrentValue": "sum",
        "NAV_Latest": "last",
        "Date_Latest": "last"
    }).reset_index()

    summary["ProfitLoss"] = summary["CurrentValue"] - summary["Invested"]
    summary["ReturnPct"] = (summary["ProfitLoss"] / summary["Invested"]) * 100

    # Rename columns to clean names
    summary.rename(columns={
        "NAV_Latest": "LatestNAV",
        "Date_Latest": "LatestNAVDate"
    }, inplace=True)

    return summary

