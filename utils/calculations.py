import pandas as pd

def calculate_current_value(fund_df, latest_nav):
    total_units = fund_df["Units"].sum()
    return total_units * latest_nav


def calculate_invested_amount(fund_df):
    return fund_df["Amount"].sum()


def calculate_profit(invested, current):
    return current - invested
