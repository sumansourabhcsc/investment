#utils/calculations.py — MERGE NAV + PORTFOLIO
def merge_nav_with_portfolio(portfolio_df, nav_df, mutual_funds):
    portfolio_df["SchemeCode"] = portfolio_df["FundName"].map(mutual_funds)

    merged = portfolio_df.merge(
        nav_df[["SchemeCode", "NAV", "Date"]],
        on="SchemeCode",
        how="left",
        suffixes=("_Purchase", "_Latest")
    )

    merged.rename(columns={"NAV": "LatestNAV", "Date": "LatestNAVDate"}, inplace=True)
    return merged
