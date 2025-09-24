# 1A_Charts/1a_charts_lookup.py

import pandas as pd
from typing import List, Union

class OneAChartsLookup:
    def __init__(self, csv_path: str):
        """
        Initialize lookup tool for 1A_Charts.

        Args:
            csv_path: Path to the 1A_Charts CSV file
                      (local file OR s3://bucket/key.csv)
        """
        storage_opts = {"anon": False} if csv_path.startswith("s3://") else None
        self.df = pd.read_csv(csv_path, parse_dates=["Date"], dayfirst=True,
                              storage_options=storage_opts)

        # Normalize Date column to date only
        self.df["Date"] = self.df["Date"].dt.date

    def get_metric_value(
        self,
        metric_name: str,
        dates: Union[str, List[str]]
    ) -> pd.DataFrame:
        """
        Retrieve Metric_Value for given metric and date(s).

        Args:
            metric_name: "Total Activated" or "Total User Base Since Inception"
            dates: single date string "dd/mm/yy" or list of date strings

        Returns:
            DataFrame with Date, Metric_Name, Metric_Value
        """
        if isinstance(dates, str):
            dates = [dates]

        # Convert to datetime.date for matching
        parsed_dates = [pd.to_datetime(d, format="%d/%m/%y").date() for d in dates]

        result = self.df[
            (self.df["Metric_Name"] == metric_name) &
            (self.df["Date"].isin(parsed_dates))
        ][["Date", "Metric_Name", "Metric_Value"]]

        if result.empty:
            return pd.DataFrame({
                "Error": [f"No data found for {metric_name} on {', '.join(dates)}"]
            })

        return result.reset_index(drop=True)


# # ---- Example Usage ----
# if __name__ == "__main__":
#     csv_path = "s3://aws-logs-620144979924-ap-south-1/analytics-slack-agent/data/1A_Charts/1A_Charts_2025.csv"
#     tool = OneAChartsLookup(csv_path)

#     print(tool.get_metric_value("Total Activated", ["01/07/25", "02/07/25"]))
#     print(tool.get_metric_value("Total User Base Since Inception", "01/07/25"))
