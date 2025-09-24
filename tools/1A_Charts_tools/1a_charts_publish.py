# tools/1A_Charts/publish.py

import os
import pandas as pd
import boto3

class OneAChartsPublisher:
    def __init__(self, csv_path: str):
        """
        Initialize publisher for 1A_Charts.

        Args:
            csv_path: Path to the 1A_Charts CSV file
                      (local path OR s3://bucket/key.csv)
        """
        storage_opts = {"anon": False} if csv_path.startswith("s3://") else None
        self.df = pd.read_csv(csv_path, parse_dates=["Date"], dayfirst=True,
                              storage_options=storage_opts)
        self.df["Date"] = self.df["Date"].dt.date

        # Store for re-use (for S3 writes later)
        self.csv_path = csv_path

    def publish_dashboard(
        self, target_date: str,
        output_dir: str = "./",
        upload_to_s3: bool = True
    ):
        """
        Generate dashboard summary for a given date and export to Excel.

        Args:
            target_date: date string in dd/mm/yy format
            output_dir: folder where Excel will be saved (temp if S3 used)
            upload_to_s3: if True and csv_path was S3, uploads result back to S3

        Returns:
            str: local file path (and S3 URI if uploaded)
        """
        # Parse target date
        date_obj = pd.to_datetime(target_date, format="%d/%m/%y").date()

        # Current + previous month
        curr_month, year = date_obj.month, date_obj.year
        prev_month = curr_month - 1 if curr_month > 1 else 12
        prev_year = year if prev_month != 12 else year - 1

        # Filter
        curr_df = self.df[(self.df["Date"].apply(lambda d: d.month) == curr_month) &
                          (self.df["Date"].apply(lambda d: d.year) == year)]
        prev_df = self.df[(self.df["Date"].apply(lambda d: d.month) == prev_month) &
                          (self.df["Date"].apply(lambda d: d.year) == prev_year)]

        # Last available values
        curr_vals = curr_df.groupby("Metric_Name")["Metric_Value"].last()
        prev_vals = prev_df.groupby("Metric_Name")["Metric_Value"].last()

        rows = []
        for metric in ["Total User Base Since Inception", "Total Activated"]:
            curr_val = curr_vals.get(metric, None)
            prev_val = prev_vals.get(metric, None)

            change = None
            if curr_val and prev_val:
                change = ((curr_val - prev_val) / prev_val) * 100

            rows.append({
                "Particulars": metric,
                f"{date_obj.strftime('%b, %Y')}": f"{curr_val/1e6:.2f}M" if curr_val else "N/A",
                f"{pd.to_datetime(f'{prev_month}/{prev_year}', format='%m/%Y').strftime('%b, %Y')}": f"{prev_val/1e6:.2f}M" if prev_val else "N/A",
                "Change": f"{change:.2f}%" if change is not None else "N/A"
            })

        dashboard_df = pd.DataFrame(rows)

        # Ensure local output dir exists
        os.makedirs(output_dir, exist_ok=True)
        local_file = os.path.join(output_dir, f"1A_Charts_Dashboard_{date_obj}.xlsx")

        # Save to Excel
        with pd.ExcelWriter(local_file, engine="xlsxwriter") as writer:
            dashboard_df.to_excel(writer, index=False, sheet_name="Dashboard")

            # Formatting
            workbook = writer.book
            worksheet = writer.sheets["Dashboard"]

            header_fmt = workbook.add_format({"bold": True, "bg_color": "#DCE6F1", "align": "center"})
            for col_num, value in enumerate(dashboard_df.columns.values):
                worksheet.write(0, col_num, value, header_fmt)

            for i, col in enumerate(dashboard_df.columns):
                col_width = max(dashboard_df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, col_width)

        result = f"✅ Dashboard exported locally: {local_file}"

        # Upload to S3 if requested
        if upload_to_s3 and self.csv_path.startswith("s3://"):
            bucket = self.csv_path.split("/")[2]
            prefix = "/".join(self.csv_path.split("/")[3:-1])
            s3_key = f"{prefix}/output/1A_Charts/{os.path.basename(local_file)}"

            s3 = boto3.client("s3")
            s3.upload_file(local_file, bucket, s3_key)

            s3_uri = f"s3://{bucket}/{s3_key}"
            result += f"\n☁️ Also uploaded to: {s3_uri}"

        return result


# # Example usage
# if __name__ == "__main__":
#     csv_path = "s3://aws-logs-620144979924-ap-south-1/analytics-slack-agent/data/1A_Charts/1A_Charts_2025.csv"
#     tool = OneAChartsPublisher(csv_path)
#     print(tool.publish_dashboard("18/09/25"))
