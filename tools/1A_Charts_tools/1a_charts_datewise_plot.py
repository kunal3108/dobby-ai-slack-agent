import os
import pandas as pd
import matplotlib.pyplot as plt

class OneAChartsLookup:
    def __init__(self, csv_path: str):
        """
        Initialize lookup tool for 1A_Charts.
        """
        # Load CSV with proper date parsing
        self.df = pd.read_csv(csv_path, parse_dates=["Date"], dayfirst=True)

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

    def plot_metric(self, metric_name: str, dates: list[str], output_dir: str = "/Users/kunaltalukdar/Downloads"):
        """
        Plot line chart for given metric over specified dates and save to Downloads.
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

        # Ensure directory exists
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"{metric_name.replace(' ', '_')}_chart.png")

        plt.savefig(output_file)
        plt.close()

        return f"Chart saved to {output_file}"

#tool = OneAChartsLookup("/Users/kunaltalukdar/Downloads/1A_Charts_2025.csv")

#print(tool.plot_metric("Total Activated", ["01/07/25","02/07/25","03/07/25","04/07/25","05/07/25"]))


