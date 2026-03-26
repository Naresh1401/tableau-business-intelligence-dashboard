"""
Financial Analysis
P&L waterfall, trend forecasting, ratio analysis, variance analysis.
"""

import os
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")


def load_data():
    """Load financial data."""
    return pd.read_csv(os.path.join(DATA_DIR, "finance_data.csv"), parse_dates=["month"])


def pl_waterfall_prep(df):
    """Prepare P&L waterfall data for Tableau."""
    latest_year = df["month"].dt.year.max()
    yearly = df[df["month"].dt.year == latest_year]

    waterfall_items = [
        {"item": "Revenue", "value": yearly["revenue"].sum(), "type": "positive"},
        {"item": "COGS", "value": -yearly["cogs"].sum(), "type": "negative"},
        {"item": "Gross Profit", "value": yearly["gross_profit"].sum(), "type": "subtotal"},
        {"item": "Operating Expenses", "value": -yearly["operating_expenses"].sum(), "type": "negative"},
        {"item": "EBITDA", "value": yearly["ebitda"].sum(), "type": "subtotal"},
        {"item": "Net Income", "value": yearly["net_income"].sum(), "type": "total"},
    ]

    waterfall_df = pd.DataFrame(waterfall_items)
    waterfall_df["value"] = waterfall_df["value"].round(2)

    # Running totals for waterfall positioning
    running = 0
    starts = []
    for _, row in waterfall_df.iterrows():
        if row["type"] in ("subtotal", "total"):
            starts.append(0)
            running = row["value"]
        else:
            starts.append(running)
            running += row["value"]
    waterfall_df["start"] = starts

    return waterfall_df


def trend_analysis_with_forecast(df):
    """Analyze revenue trends and create linear forecast."""
    df = df.copy()
    df["month_num"] = np.arange(len(df))

    # Linear regression for trend
    slope, intercept, r_value, p_value, std_err = scipy_stats.linregress(
        df["month_num"], df["revenue"]
    )

    df["trend_line"] = intercept + slope * df["month_num"]
    df["residual"] = df["revenue"] - df["trend_line"]

    # 3-month forecast
    forecast_months = pd.date_range(
        start=df["month"].max() + pd.DateOffset(months=1), periods=3, freq="MS"
    )
    forecast_nums = np.arange(len(df), len(df) + 3)
    forecast_values = intercept + slope * forecast_nums

    residual_std = df["residual"].std()
    forecast_df = pd.DataFrame({
        "month": forecast_months,
        "forecast_revenue": forecast_values.round(2),
        "lower_bound": (forecast_values - 1.96 * residual_std).round(2),
        "upper_bound": (forecast_values + 1.96 * residual_std).round(2),
    })

    trend_stats = {
        "monthly_growth_rate": slope,
        "r_squared": r_value ** 2,
        "p_value": p_value,
        "std_error": std_err,
    }

    return trend_stats, forecast_df


def ratio_analysis(df):
    """Analyze financial ratios: liquidity, profitability, efficiency."""
    latest = df.iloc[-1]

    ratios = {
        # Profitability
        "gross_margin": round(latest["gross_profit"] / latest["revenue"], 4),
        "operating_margin": round(latest["ebitda"] / latest["revenue"], 4),
        "net_margin": round(latest["net_income"] / latest["revenue"], 4),
        "return_on_equity": round(latest["return_on_equity"], 4),
        # Liquidity
        "current_ratio": round(latest["current_ratio"], 4),
        "debt_ratio": round(latest["debt_ratio"], 4),
        # Efficiency
        "ar_days": round(latest["accounts_receivable"] / (latest["revenue"] / 30), 1),
        "ap_days": round(latest["accounts_payable"] / (latest["cogs"] / 30), 1),
        "inventory_days": round(latest["inventory_value"] / (latest["cogs"] / 30), 1),
    }

    # Ratio trends (quarterly averages)
    df = df.copy()
    df["quarter"] = df["month"].dt.to_period("Q")
    quarterly_ratios = df.groupby("quarter").agg(
        avg_gross_margin=("gross_profit", lambda x: (x.sum() / df.loc[x.index, "revenue"].sum())),
        avg_current_ratio=("current_ratio", "mean"),
        avg_debt_ratio=("debt_ratio", "mean"),
        avg_roe=("return_on_equity", "mean"),
    ).round(4)
    quarterly_ratios.index = quarterly_ratios.index.astype(str)

    return ratios, quarterly_ratios


def variance_analysis(df):
    """Budget vs actual variance analysis (using prior year as budget proxy)."""
    df = df.copy()
    df["year"] = df["month"].dt.year
    df["month_num"] = df["month"].dt.month

    years = sorted(df["year"].unique())
    if len(years) < 2:
        return pd.DataFrame()

    # Use prior year as "budget" for current year
    current_year = years[-1]
    prior_year = years[-2]

    actual = df[df["year"] == current_year][["month_num", "revenue", "cogs", "operating_expenses", "net_income"]]
    actual.columns = ["month", "actual_revenue", "actual_cogs", "actual_opex", "actual_net_income"]

    budget = df[df["year"] == prior_year][["month_num", "revenue", "cogs", "operating_expenses", "net_income"]]
    budget.columns = ["month", "budget_revenue", "budget_cogs", "budget_opex", "budget_net_income"]

    # Apply 5% growth target to prior year as budget
    budget["budget_revenue"] = (budget["budget_revenue"] * 1.05).round(2)

    variance = actual.merge(budget, on="month", how="inner")
    variance["revenue_variance"] = (variance["actual_revenue"] - variance["budget_revenue"]).round(2)
    variance["revenue_variance_pct"] = (
        variance["revenue_variance"] / variance["budget_revenue"].abs()
    ).round(4)

    return variance


def main():
    """Run all financial analyses and export summary."""
    print("Running Financial Analysis...")
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    df = load_data()

    waterfall = pl_waterfall_prep(df)
    trend_stats, forecast = trend_analysis_with_forecast(df)
    ratios, quarterly_ratios = ratio_analysis(df)
    variance = variance_analysis(df)

    # Build summary
    summary_rows = []

    # Overall metrics
    total_rev = df["revenue"].sum()
    total_ni = df["net_income"].sum()
    for metric, value in [
        ("total_revenue_3yr", total_rev),
        ("total_net_income_3yr", total_ni),
        ("avg_monthly_revenue", df["revenue"].mean()),
        ("latest_revenue", df["revenue"].iloc[-1]),
        ("latest_net_income", df["net_income"].iloc[-1]),
        ("trend_r_squared", trend_stats["r_squared"]),
        ("monthly_growth_rate", trend_stats["monthly_growth_rate"]),
    ]:
        summary_rows.append({"metric": metric, "dimension": "overall", "value": round(value, 4)})

    # Ratios
    for ratio_name, value in ratios.items():
        summary_rows.append({"metric": f"ratio_{ratio_name}", "dimension": "latest", "value": value})

    # Waterfall
    for _, row in waterfall.iterrows():
        summary_rows.append({
            "metric": "pl_waterfall",
            "dimension": row["item"],
            "value": row["value"],
        })

    # Forecast
    for _, row in forecast.iterrows():
        summary_rows.append({
            "metric": "forecast_revenue",
            "dimension": str(row["month"].date()),
            "value": row["forecast_revenue"],
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(ANALYSIS_DIR, "financial_summary.csv"), index=False)

    print(f"  3-Year Revenue: ${total_rev:,.2f}")
    print(f"  3-Year Net Income: ${total_ni:,.2f}")
    print(f"  Latest Gross Margin: {ratios['gross_margin']:.2%}")
    print(f"  Trend R²: {trend_stats['r_squared']:.4f}")
    print(f"  Summary exported to: {os.path.join(ANALYSIS_DIR, 'financial_summary.csv')}")


if __name__ == "__main__":
    main()
