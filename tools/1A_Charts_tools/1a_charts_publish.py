# tools/1A_Charts/publish.py
import os
import pandas as pd

class OneAChartsPublisher:
    def __init__(self, csv_path: str):
        """
        Initialize publisher for 1A_Charts.

        Args:
            csv_path: Path to the 1A_Charts CSV file
        """
        self.df = pd.read_csv(csv_path, parse_dates=["Date"], dayfirst=True)
        self.df["Date"] = self.df["Date"].dt.date

    def publish_dashboard(self, target_date: str, output_dir: str = "/Users/kunaltalukdar/Downloads"):
        """
        Generate dashboard summary for a given date and export to Excel.
        
        Args:
            target_date: date string in dd/mm/yy format
            output_dir: folder where Excel will be saved

        Returns:
            str: path of saved Excel file
        """
        # Parse target date
        date_obj = pd.to_datetime(target_date, format="%d/%m/%y").date()

        # Current and previous month
        curr_month = date_obj.month
        prev_month = curr_month - 1 if curr_month > 1 else 12
        year = date_obj.year
        prev_year = year if prev_month != 12 else year - 1

        # Filter current + prev month
        curr_df = self.df[(self.df["Date"].apply(lambda d: d.month) == curr_month) & 
                          (self.df["Date"].apply(lambda d: d.year) == year)]
        prev_df = self.df[(self.df["Date"].apply(lambda d: d.month) == prev_month) & 
                          (self.df["Date"].apply(lambda d: d.year) == prev_year)]

        # Last available values for each metric
        curr_vals = curr_df.groupby("Metric_Name")["Metric_Value"].last()
        prev_vals = prev_df.groupby("Metric_Name")["Metric_Value"].last()

        rows = []
        for metric in ["Total User Base Since Inception", "Total Activated"]:
            curr_val = curr_vals.get(metric, None)
            prev_val = prev_vals.get(metric, None)

            if curr_val and prev_val:
                change = ((curr_val - prev_val) / prev_val) * 100
            else:
                change = None

            rows.append({
                "Particulars": metric,
                f"{date_obj.strftime('%b, %Y')}": f"{curr_val/1e6:.2f}M" if curr_val else "N/A",
                f"{pd.to_datetime(f'{prev_month}/{prev_year}', format='%m/%Y').strftime('%b, %Y')}": f"{prev_val/1e6:.2f}M" if prev_val else "N/A",
                "Change": f"{change:.2f}%" if change is not None else "N/A"
            })

        dashboard_df = pd.DataFrame(rows)

        # Ensure output dir exists
        os.makedirs(output_dir, exist_ok=True)
        output_file = os.path.join(output_dir, f"1A_Charts_Dashboard_{date_obj}.xlsx")

        # Save to Excel
        with pd.ExcelWriter(output_file, engine="xlsxwriter") as writer:
            dashboard_df.to_excel(writer, index=False, sheet_name="Dashboard")

            # Format the sheet
            workbook = writer.book
            worksheet = writer.sheets["Dashboard"]

            # Header style
            header_fmt = workbook.add_format({"bold": True, "bg_color": "#DCE6F1", "align": "center"})
            for col_num, value in enumerate(dashboard_df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)

            # Auto column width
            for i, col in enumerate(dashboard_df.columns):
                col_width = max(dashboard_df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, col_width)

        return output_file


# Example usage
if __name__ == "__main__":
    tool = OneAChartsPublisher("/Users/kunaltalukdar/Downloads/1A_Charts_2025.csv")
    file_path = tool.publish_dashboard("18/09/25")
    print(f"✅ Dashboard exported: {file_path}")
