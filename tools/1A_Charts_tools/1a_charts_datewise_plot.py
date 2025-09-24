#1a_charts_datewise_plot.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import boto3
from typing import Dict, List, Union

class OneAChartsLookup:
    def __init__(self, csv_path: str):
        """
        Initialize lookup tool for 1A_Charts.
        Supports both local and S3 CSVs.
        """
        storage_opts = {"anon": False} if csv_path.startswith("s3://") else None
        self.df = pd.read_csv(
            csv_path,
            parse_dates=["Date"],
            dayfirst=True,
            storage_options=storage_opts
        )
        self.df["Date"] = self.df["Date"].dt.date

        # Store original path for S3 uploads
        self.csv_path = csv_path

    def get_metric(self, metric_name: str, dates: List[str]) -> Dict[str, Union[int, None, str]]:
        """
        Retrieve Metric_Value(s) for given Metric_Name and date(s).

        Args:
            metric_name: metric like "Total Activated"
            dates: list of date strings in dd/mm/yy format

        Returns:
            Dict mapping {date_str: value or error}
        """
        results = {}
        for d in dates:
            try:
                date_obj = pd.to_datetime(d, format="%d/%m/%y").date()
                match = self.df[
                    (self.df["Date"] == date_obj) &
                    (self.df["Metric_Name"] == metric_name)
                ]
                if not match.empty:
                    results[d] = int(match["Metric_Value"].iloc[0])
                else:
                    results[d] = None
            except Exception as e:
                results[d] = f"Error: {e}"
        return results

    def plot_metric(
        self,
        metric_name: str,
        dates: List[str],
        output_dir: str = "./",
        upload_to_s3: bool = True
    ) -> str:
        """
        Plot line chart for given metric over specified dates and optionally upload to S3.

        Args:
            metric_name: metric like "Total Activated"
            dates: list of date strings
            output_dir: local folder for saving
            upload_to_s3: whether to upload chart to S3

        Returns:
            str: local file path (and S3 URI if uploaded)
        """
        results = self.get_metric(metric_name, dates)

        # Prepare DataFrame
        plot_df = pd.DataFrame({
            "Date": [pd.to_datetime(d, format="%d/%m/%y").date() for d in results.keys()],
            "Value": [v if isinstance(v, (int, float)) else None for v in results.values()]
        }).dropna().sort_values("Date")

        if plot_df.empty:
            raise ValueError(f"No valid values found for {metric_name} on given dates: {dates}")

        # Plot
        plt.figure(figsize=(10, 6))
        plt.plot(plot_df["Date"], plot_df["Value"], marker="o", label=metric_name)

        # Annotate values
        for x, y in zip(plot_df["Date"], plot_df["Value"]):
            plt.text(x, y, f"{int(y):,}", ha="center", va="bottom", fontsize=9)

        plt.title(f"1A_Charts – {metric_name} Over Time")
        plt.xlabel("Date")
        plt.ylabel("Metric Value")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        plt.xticks(plot_df["Date"], [d.strftime("%d/%m/%y") for d in plot_df["Date"]])

        # Save locally
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(
            output_dir,
            f"{metric_name.replace(' ', '_')}_chart.png"
        )
        plt.savefig(output_file)
        plt.close()

        result = f"📊 Chart saved locally at {output_file}"

        # Upload to S3 if needed
        if upload_to_s3 and self.csv_path.startswith("s3://"):
            bucket = self.csv_path.split("/")[2]
            prefix = "/".join(self.csv_path.split("/")[3:-1])
            s3_key = f"{prefix}/output/1A_Charts/{os.path.basename(output_file)}"

            s3 = boto3.client("s3")
            s3.upload_file(output_file, bucket, s3_key)

            s3_uri = f"s3://{bucket}/{s3_key}"
            result += f"\n☁️ Also uploaded to: {s3_uri}"
            return result

        return result
