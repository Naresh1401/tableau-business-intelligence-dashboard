"""
Gen AI Operations Analysis
Model usage, cost breakdown, latency, hallucination tracking, department adoption, ROI.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")


def load_data():
    """Load Gen AI usage data."""
    return pd.read_csv(os.path.join(DATA_DIR, "genai_usage_data.csv"), parse_dates=["timestamp"])


def model_usage_trends(df):
    """Analyze model usage trends over time."""
    df["month"] = df["timestamp"].dt.to_period("M")

    monthly_model = df.groupby(["month", "model"]).agg(
        request_count=("request_id", "count"),
        total_tokens=("tokens_input", lambda x: x.sum() + df.loc[x.index, "tokens_output"].sum()),
        total_cost=("cost_usd", "sum"),
    ).round(4)
    monthly_model.index = monthly_model.index.set_levels(
        monthly_model.index.levels[0].astype(str), level=0
    )

    model_summary = df.groupby("model").agg(
        total_requests=("request_id", "count"),
        total_tokens_in=("tokens_input", "sum"),
        total_tokens_out=("tokens_output", "sum"),
        total_cost=("cost_usd", "sum"),
        avg_latency=("latency_ms", "mean"),
        avg_satisfaction=("user_satisfaction", "mean"),
        error_rate=("error_flag", "mean"),
        hallucination_rate=("hallucination_detected", "mean"),
    ).round(4)

    return monthly_model, model_summary


def cost_breakdown(df):
    """Analyze cost breakdown by model, use case, and department."""
    cost_by_model = df.groupby("model")["cost_usd"].agg(["sum", "mean", "median"]).round(4)
    cost_by_model.columns = ["total_cost", "avg_cost", "median_cost"]

    cost_by_usecase = df.groupby("use_case")["cost_usd"].agg(["sum", "mean", "count"]).round(4)
    cost_by_usecase.columns = ["total_cost", "avg_cost", "request_count"]

    cost_by_dept = df.groupby("department")["cost_usd"].agg(["sum", "mean", "count"]).round(4)
    cost_by_dept.columns = ["total_cost", "avg_cost", "request_count"]

    # Monthly cost trend
    df["month"] = df["timestamp"].dt.to_period("M")
    monthly_cost = df.groupby("month")["cost_usd"].sum().round(4)
    monthly_cost.index = monthly_cost.index.astype(str)

    return cost_by_model, cost_by_usecase, cost_by_dept, monthly_cost


def latency_percentiles(df):
    """Analyze latency percentiles by model and use case."""
    latency_by_model = df.groupby("model")["latency_ms"].agg(
        p50=lambda x: x.quantile(0.50),
        p90=lambda x: x.quantile(0.90),
        p95=lambda x: x.quantile(0.95),
        p99=lambda x: x.quantile(0.99),
        mean="mean",
        std="std",
    ).round(1)

    latency_by_usecase = df.groupby("use_case")["latency_ms"].agg(
        p50=lambda x: x.quantile(0.50),
        p95=lambda x: x.quantile(0.95),
        mean="mean",
    ).round(1)

    # Latency heatmap: model x use_case
    latency_matrix = df.groupby(["model", "use_case"])["latency_ms"].median().unstack(fill_value=0).round(1)

    return latency_by_model, latency_by_usecase, latency_matrix


def hallucination_tracking(df):
    """Track hallucination rates over time and by model."""
    df["week"] = df["timestamp"].dt.to_period("W")

    weekly_hallucination = df.groupby("week").agg(
        hallucination_rate=("hallucination_detected", "mean"),
        total_requests=("request_id", "count"),
        hallucination_count=("hallucination_detected", "sum"),
    ).round(4)
    weekly_hallucination.index = weekly_hallucination.index.astype(str)

    halluc_by_model = df.groupby("model").agg(
        hallucination_rate=("hallucination_detected", "mean"),
        total=("request_id", "count"),
        hallucination_count=("hallucination_detected", "sum"),
    ).round(4)

    halluc_by_usecase = df.groupby("use_case").agg(
        hallucination_rate=("hallucination_detected", "mean"),
    ).round(4)

    return weekly_hallucination, halluc_by_model, halluc_by_usecase


def department_adoption(df):
    """Analyze department adoption rates and patterns."""
    dept_stats = df.groupby("department").agg(
        total_requests=("request_id", "count"),
        total_cost=("cost_usd", "sum"),
        avg_satisfaction=("user_satisfaction", "mean"),
        error_rate=("error_flag", "mean"),
        hallucination_rate=("hallucination_detected", "mean"),
        unique_use_cases=("use_case", "nunique"),
    ).round(4)

    dept_stats["request_share"] = (dept_stats["total_requests"] / dept_stats["total_requests"].sum()).round(4)
    dept_stats["cost_share"] = (dept_stats["total_cost"] / dept_stats["total_cost"].sum()).round(4)

    # Adoption trend by department (monthly request counts)
    df["month"] = df["timestamp"].dt.to_period("M")
    dept_monthly = df.groupby(["month", "department"])["request_id"].count().unstack(fill_value=0)
    dept_monthly.index = dept_monthly.index.astype(str)

    return dept_stats, dept_monthly


def roi_estimation(df):
    """Estimate ROI per use case based on productivity assumptions."""
    # Productivity multipliers (estimated hours saved per request)
    productivity_hours = {
        "code_gen": 0.5,
        "summarization": 0.3,
        "qa": 0.15,
        "translation": 0.4,
        "analysis": 0.35,
    }
    avg_hourly_cost = 75  # Estimated average employee hourly cost

    roi_data = []
    for use_case, hours_saved in productivity_hours.items():
        uc_data = df[df["use_case"] == use_case]
        total_requests = len(uc_data)
        total_cost = uc_data["cost_usd"].sum()
        total_hours_saved = total_requests * hours_saved
        productivity_value = total_hours_saved * avg_hourly_cost
        net_savings = productivity_value - total_cost
        roi = (net_savings / total_cost) if total_cost > 0 else 0

        roi_data.append({
            "use_case": use_case,
            "total_requests": total_requests,
            "total_cost": round(total_cost, 2),
            "hours_saved_per_request": hours_saved,
            "total_hours_saved": round(total_hours_saved, 1),
            "productivity_value": round(productivity_value, 2),
            "net_savings": round(net_savings, 2),
            "roi_pct": round(roi * 100, 2),
        })

    return pd.DataFrame(roi_data)


def main():
    """Run all Gen AI analyses and export summary."""
    print("Running Gen AI Analysis...")
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    df = load_data()

    monthly_model, model_summary = model_usage_trends(df)
    cost_model, cost_uc, cost_dept, monthly_cost = cost_breakdown(df)
    lat_model, lat_uc, lat_matrix = latency_percentiles(df)
    weekly_h, halluc_model, halluc_uc = hallucination_tracking(df)
    dept_stats, dept_monthly = department_adoption(df)
    roi = roi_estimation(df)

    # Build summary
    summary_rows = []

    # Overall metrics
    total_tokens = df["tokens_input"].sum() + df["tokens_output"].sum()
    for metric, value in [
        ("total_requests", len(df)),
        ("total_cost", df["cost_usd"].sum()),
        ("avg_cost_per_request", df["cost_usd"].mean()),
        ("total_tokens", total_tokens),
        ("avg_latency_ms", df["latency_ms"].mean()),
        ("median_latency_ms", df["latency_ms"].median()),
        ("latency_p95", df["latency_ms"].quantile(0.95)),
        ("latency_p99", df["latency_ms"].quantile(0.99)),
        ("overall_error_rate", df["error_flag"].mean()),
        ("overall_hallucination_rate", df["hallucination_detected"].mean()),
        ("avg_user_satisfaction", df["user_satisfaction"].mean()),
    ]:
        summary_rows.append({"metric": metric, "dimension": "overall", "value": round(value, 4)})

    # Model stats
    for model, row in model_summary.iterrows():
        summary_rows.append({"metric": "requests_by_model", "dimension": model, "value": row["total_requests"]})
        summary_rows.append({"metric": "cost_by_model", "dimension": model, "value": row["total_cost"]})
        summary_rows.append({"metric": "halluc_rate_by_model", "dimension": model, "value": row["hallucination_rate"]})
        summary_rows.append({"metric": "latency_by_model", "dimension": model, "value": row["avg_latency"]})

    # Department adoption
    for dept, row in dept_stats.iterrows():
        summary_rows.append({"metric": "adoption_by_dept", "dimension": dept, "value": row["request_share"]})

    # Use case ROI
    for _, row in roi.iterrows():
        summary_rows.append({"metric": "roi_by_use_case", "dimension": row["use_case"], "value": row["roi_pct"]})
        summary_rows.append({"metric": "net_savings_by_use_case", "dimension": row["use_case"], "value": row["net_savings"]})

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(ANALYSIS_DIR, "genai_summary.csv"), index=False)

    print(f"  Total Requests: {len(df):,}")
    print(f"  Total Cost: ${df['cost_usd'].sum():,.2f}")
    print(f"  Avg Latency: {df['latency_ms'].mean():.0f}ms")
    print(f"  Hallucination Rate: {df['hallucination_detected'].mean():.2%}")
    print(f"  Summary exported to: {os.path.join(ANALYSIS_DIR, 'genai_summary.csv')}")


if __name__ == "__main__":
    main()
