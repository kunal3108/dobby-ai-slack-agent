# Table Context: 1A_Charts

## Overview
The `1A_Charts` dataset is published **daily** and stored in S3 at:  
`s3://aws-logs-620144979924-ap-south-1/analytics-slack-agent/data/1A_Charts/1A_Charts_2025.csv`

It provides **aggregated user metrics** across all products.

---

## Columns
- **Date** → Date of publication (`dd/mm/yy`)  
- **Data_Source** → Always `"1A_Charts"`  
- **Product** → `"Overall"`  
- **Metric_Name**  
  - `Total User Base Since Inception` → cumulative user base count since launch  
  - `Total Activated` → count of total activated users  
- **Metric_Type** → `"Count"`  
- **Metric_Value** → numeric values (8-digit integers, e.g., `13478049`)

---

## Example Queries
- **Lookup**
  - "Give me the Total User Base Since Inception for 01/07/25"  
  - "What was the Total Activated on 18/09/25?"  

- **Comparison**
  - "Compare the July and August end data of 1A_Charts"  
  - "Show the change in Total Activated between Sep and Aug"  

- **Trends / Aggregates**
  - "What is the trend of Total Activated in August?"  
  - "What is the average change of Total User Base Since Inception last month?"  

- **Publish**
  - "Publish the dashboard for 18/09/25"  

- **Visualization**
  - "Plot Total Activated over 01/07/25–07/07/25"  

---

## Tools Available
Located under `tools/1A_Charts_tools/`:

- **`1a_charts_lookup.py`**  
  - Fetches metric values for one or more specific dates  

- **`1a_charts_datewise_plot.py`**  
  - Generates line charts over time (metric vs. date)  

- **`1a_charts_publish.py`**  
  - Publishes dashboards (Excel) for a given date, showing current vs. previous month and % change  

---

## Outputs
- Local (default: `./`)  
- S3 output path:  
  `s3://aws-logs-620144979924-ap-south-1/analytics-slack-agent/output/1A_Charts/`

---

## Notes
- Values are raw counts (integers). For presentation, tools may convert to shorthand (e.g., `26.31M`).  
- % Change = `((Current Month Value - Previous Month Value) / Previous Month Value) × 100`  
- When publishing, dashboards follow Excel format with headers:  
  `Particulars | Sep, 2025 | Aug, 2025 | Change`

