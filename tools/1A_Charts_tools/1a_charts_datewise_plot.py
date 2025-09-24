import os
import pandas as pd
import matplotlib.pyplot as plt
import boto3

class OneAChartsLookup:
    def __init__(self, csv_path: str):
        """
        Initialize lookup tool for 1A_Charts.
        """
        # Load CSV directly from S3 or local path
        self.df = pd.read_csv(
            csv_path,
            parse_dates=["Date"],
            dayfirst=True,
            storage_options={"anon": False} if csv_path.startswith("s3://") else None
        )

        # Keep only the date (not time)
        self.df["Date"] = self.df["Date"].dt.date

    def get_metric(self, metric_name: str, dates: list[str]):
        """
        Retrieve Metric_Value(s) for given Metric_Name and date(s).
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

    def plot_metric(self, metric_name: str, dates: list[str], 
                    output_dir: str = "./", 
                    upload_to_s3: bool = True):
        """
        Plot line chart for given metric over specified dates and upload to S3.
        """
        results = self.get_metric(metric_name, dates)

        # Convert to DataFrame for plotting
        plot_df = pd.DataFrame({
            "Date": [pd.to_datetime(d, format="%d/%m/%y").date() for d in results.keys()],
            "Value": [v for v in results.values()]
        })

        plot_df = plot_df.dropna().sort_values("Date")

        plt.figure(figsize=(10, 6))
        plt.plot(plot_df["Date"], plot_df["Value"], marker="o", label=metric_name)

        # Annotate each point with its value
        for x, y in zip(plot_df["Date"], plot_df["Value"]):
            plt.text(x, y, f"{y:,}", ha="center", va="bottom", fontsize=9)

        plt.title(f"1A_Charts – {metric_name} Over Time")
        plt.xlabel("Date")
        plt.ylabel("Metric Value")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()

        # Show only dates on x-axis
        plt.xticks(plot_df["Date"], [d.strftime("%d/%m/%y") for d in plot_df["Date"]])

        # Save locally first
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{metric_name.replace(' ', '_')}_chart.png")
        plt.savefig(output_file)
        plt.close()

        print(f"📊 Chart saved locally at {output_file}")

        # Upload to S3 if enabled
        if upload_to_s3:
            s3 = boto3.client("s3")
            bucket = "aws-logs-620144979924-ap-south-1"
            key = "analytics-slack-agent/output/1A_Charts/" + os.path.basename(output_file)
            s3.upload_file(output_file, bucket, key)
            print(f"✅ Chart uploaded to s3://{bucket}/{key}")

        return output_file
