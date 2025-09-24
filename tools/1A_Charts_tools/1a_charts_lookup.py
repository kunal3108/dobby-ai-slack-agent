# 1A_Charts/1a_charts_lookup.py

from typing import Dict
from 1A_Charts.1a_charts_lookup import OneAChartsLookup

# Reuse your CSV path (can later move to config/secrets)
CSV_PATH = "s3://aws-logs-620144979924-ap-south-1/analytics-slack-agent/data/1A_Charts/1A_Charts_2025.csv"

# Initialize once
lookup_tool = OneAChartsLookup(CSV_PATH)

def lookup_node(state: Dict) -> Dict:
    """
    LangGraph node: perform a lookup in 1A_Charts.

    Expects:
        state["metric_name"]: str
        state["dates"]: list[str] or str

    Produces:
        state["result"]: str (user-friendly response)
    """
    metric = state.get("metric_name")
    dates = state.get("dates")

    if not metric or not dates:
        state["result"] = "⚠️ Missing 'metric_name' or 'dates' in state."
        return state

    try:
        df = lookup_tool.get_metric_value(metric, dates)

        if "Error" in df.columns:
            state["result"] = df["Error"].iloc[0]
        else:
            rows = [f"{row['Date']}: {row['Metric_Value']:,}" for _, row in df.iterrows()]
            state["result"] = f"📊 {metric} values:\n" + "\n".join(rows)

    except Exception as e:
        state["result"] = f"⚠️ Lookup failed: {e}"

    return state

