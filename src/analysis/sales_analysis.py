"""
Sales Performance Analysis
Analyzes revenue trends, growth, seasonality, and profitability.
"""

import os
import pandas as pd
import numpy as np
from scipy import stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")


def load_data():
    """Load sales data."""
    return pd.read_csv(os.path.join(DATA_DIR, "sales_data.csv"), parse_dates=["date"])


def revenue_trends(df):
    """Analyze revenue trends by region, product, and channel."""
    by_region = df.groupby("region").agg(
        total_revenue=("revenue", "sum"),
        total_units=("units_sold", "sum"),
        avg_profit_margin=("profit", lambda x: (x.sum() / df.loc[x.index, "revenue"].sum())),
        transaction_count=("revenue", "count"),
    ).round(2)

    by_product = df.groupby("product_category").agg(
        total_revenue=("revenue", "sum"),
        total_units=("units_sold", "sum"),
        avg_unit_price=("unit_price", "mean"),
        avg_discount=("discount_pct", "mean"),
    ).round(2)

    by_channel = df.groupby("sales_channel").agg(
        total_revenue=("revenue", "sum"),
        total_units=("units_sold", "sum"),
        avg_deal_size=("revenue", "mean"),
    ).round(2)

    return by_region, by_product, by_channel


def yoy_growth(df):
    """Calculate year-over-year growth."""
    df["year"] = df["date"].dt.year
    yearly = df.groupby("year").agg(
        revenue=("revenue", "sum"),
        units=("units_sold", "sum"),
        profit=("profit", "sum"),
    ).round(2)
    yearly["revenue_growth_pct"] = yearly["revenue"].pct_change().round(4)
    yearly["profit_growth_pct"] = yearly["profit"].pct_change().round(4)
    return yearly


def top_bottom_performers(df):
    """Identify top and bottom performing products and reps."""
    product_perf = df.groupby("product").agg(
        total_revenue=("revenue", "sum"),
        total_profit=("profit", "sum"),
        units_sold=("units_sold", "sum"),
    ).sort_values("total_revenue", ascending=False).round(2)

    rep_perf = df.groupby("sales_rep").agg(
        total_revenue=("revenue", "sum"),
        total_profit=("profit", "sum"),
        deal_count=("revenue", "count"),
        avg_deal_size=("revenue", "mean"),
    ).sort_values("total_revenue", ascending=False).round(2)

    return product_perf, rep_perf


def seasonality_detection(df):
    """Detect monthly seasonality patterns."""
    df["month"] = df["date"].dt.month
    monthly = df.groupby("month").agg(
        avg_revenue=("revenue", "mean"),
        avg_units=("units_sold", "mean"),
    ).round(2)

    overall_mean = monthly["avg_revenue"].mean()
    monthly["seasonality_index"] = (monthly["avg_revenue"] / overall_mean).round(4)

    return monthly


def profit_margin_analysis(df):
    """Analyze profit margins across dimensions."""
    df["profit_margin"] = (df["profit"] / df["revenue"]).round(4)

    margin_by_category = df.groupby("product_category").agg(
        avg_margin=("profit_margin", "mean"),
        median_margin=("profit_margin", "median"),
        std_margin=("profit_margin", "std"),
        min_margin=("profit_margin", "min"),
        max_margin=("profit_margin", "max"),
    ).round(4)

    margin_by_channel = df.groupby("sales_channel").agg(
        avg_margin=("profit_margin", "mean"),
        median_margin=("profit_margin", "median"),
    ).round(4)

    margin_by_discount = df.groupby(
        pd.cut(df["discount_pct"], bins=[-0.01, 0.05, 0.10, 0.20, 0.30, 1.0],
               labels=["0-5%", "5-10%", "10-20%", "20-30%", "30%+"], right=True)
    ).agg(
        avg_margin=("profit_margin", "mean"),
        count=("profit_margin", "count"),
    ).round(4)

    return margin_by_category, margin_by_channel, margin_by_discount


def main():
    """Run all sales analyses and export summary."""
    print("Running Sales Analysis...")
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    df = load_data()

    by_region, by_product, by_channel = revenue_trends(df)
    yearly = yoy_growth(df)
    product_perf, rep_perf = top_bottom_performers(df)
    monthly_seasonality = seasonality_detection(df)
    margin_cat, margin_ch, margin_disc = profit_margin_analysis(df)

    # Build summary export
    summary_data = {
        "metric": [],
        "dimension": [],
        "value": [],
    }

    # Overall metrics
    for metric, value in [
        ("total_revenue", df["revenue"].sum()),
        ("total_profit", df["profit"].sum()),
        ("total_units", df["units_sold"].sum()),
        ("avg_profit_margin", df["profit"].sum() / df["revenue"].sum()),
        ("total_transactions", len(df)),
        ("avg_deal_size", df["revenue"].mean()),
    ]:
        summary_data["metric"].append(metric)
        summary_data["dimension"].append("overall")
        summary_data["value"].append(round(value, 2))

    # Top regions
    for region, row in by_region.iterrows():
        summary_data["metric"].append("revenue_by_region")
        summary_data["dimension"].append(region)
        summary_data["value"].append(row["total_revenue"])

    # Top products
    for cat, row in by_product.iterrows():
        summary_data["metric"].append("revenue_by_category")
        summary_data["dimension"].append(cat)
        summary_data["value"].append(row["total_revenue"])

    # YoY growth
    for year, row in yearly.iterrows():
        if pd.notna(row.get("revenue_growth_pct")):
            summary_data["metric"].append("yoy_revenue_growth")
            summary_data["dimension"].append(str(year))
            summary_data["value"].append(row["revenue_growth_pct"])

    # Seasonality
    for month, row in monthly_seasonality.iterrows():
        summary_data["metric"].append("seasonality_index")
        summary_data["dimension"].append(str(month))
        summary_data["value"].append(row["seasonality_index"])

    summary_df = pd.DataFrame(summary_data)
    summary_df.to_csv(os.path.join(ANALYSIS_DIR, "sales_summary.csv"), index=False)

    print(f"  Total Revenue: ${df['revenue'].sum():,.2f}")
    print(f"  Total Profit: ${df['profit'].sum():,.2f}")
    print(f"  Avg Profit Margin: {df['profit'].sum() / df['revenue'].sum():.2%}")
    print(f"  Summary exported to: {os.path.join(ANALYSIS_DIR, 'sales_summary.csv')}")


if __name__ == "__main__":
    main()
