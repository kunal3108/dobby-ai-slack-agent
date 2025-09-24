# 1A_Charts/1a_charts_lookup.py

import pandas as pd
from typing import List, Union

class OneAChartsLookup:
    def __init__(self, csv_path: str):
        """
        Initialize lookup tool for 1A_Charts.

        Args:
            csv_path: Path to the 1A_Charts CSV file
        """
        self.df = pd.read_csv(csv_path, parse_dates=["Date"], dayfirst=True)

    def get_metric_value(
        self, 
        metric_name: str, 
        dates: Union[str, List[str]]
    ) -> pd.DataFrame:
        """
        Retrieve Metric_Value for given metric and date(s).

        Args:
            metric_name: "Total Activated" or "Total User Base Since Inception"
            dates: single date string "dd/mm/yyyy" or list of date strings

        Returns:
            DataFrame with Date, Metric_Name, Metric_Value
        """
        if isinstance(dates, str):
            dates = [dates]

        # Convert to datetime for matching
        dates = pd.to_datetime(dates, format="%d/%m/%y")

        result = self.df[
            (self.df["Metric_Name"] == metric_name) &
            (self.df["Date"].isin(dates))
        ][["Date", "Metric_Name", "Metric_Value"]]

        if result.empty:
            return pd.DataFrame({"Error": [f"No data found for {metric_name} on {dates}"]})

        return result.reset_index(drop=True)


if __name__ == "__main__":
    # Example usage
    lookup = OneAChartsLookup("1A_Charts_2025.csv")

    print("\n--- Single date ---")
    print(lookup.get_metric_value("Total Activated", "01/07/25"))

    print("\n--- Multiple dates ---")
    print(lookup.get_metric_value("Total User Base Since Inception", ["01/07/25", "03/07/25"]))
