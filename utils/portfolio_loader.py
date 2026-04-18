import os
import pandas as pd

def load_all_funds(base_path="mutualfund"):
    all_data = []

    for fund_name in os.listdir(base_path):
        fund_folder = os.path.join(base_path, fund_name)
        fund_file = os.path.join(fund_folder, "fund.csv")

        if os.path.isfile(fund_file):
            df = pd.read_csv(fund_file)

            df["FundName"] = fund_name
            df.columns = df.columns.str.strip()

            # FIX: detect correct date column
            date_col = None

            for col in df.columns:
                if col.lower() in ["date", "purchase_date", "purchasedate", "date_purchase"]:
                    date_col = col
                    break

            if date_col:
                df["Date_Purchase"] = pd.to_datetime(df[date_col], errors="coerce")
            else:
                df["Date_Purchase"] = pd.NaT

            # numeric safety
            df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            df["Units"] = pd.to_numeric(df["Units"], errors="coerce")

            # FIX: ensure correct types
            #df["Amount"] = pd.to_numeric(df["Amount"], errors="coerce")
            #df["Units"] = pd.to_numeric(df["Units"], errors="coerce")
            #df["Date_Purchase"] = pd.to_datetime(df["Date_Purchase"], errors="coerce")

            all_data.append(df)

    if not all_data:
        return pd.DataFrame()

    return pd.concat(all_data, ignore_index=True)
