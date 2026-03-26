"""
Operations KPI Analysis.

Analyzes IT operations metrics: ticket resolution, SLA compliance,
system uptime, incident severity, and deployment reliability.
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[2]
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "analysis"


def load_data() -> pd.DataFrame:
    df = pd.read_csv(DATA_DIR / "raw" / "operations_kpi_data.csv", parse_dates=["date"])
    return df


def ticket_resolution_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Weekly ticket resolution rate and backlog trends."""
    df = df.copy()
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["year"] = df["date"].dt.year
    weekly = df.groupby(["year", "week"]).agg(
        tickets_created=("tickets_created", "sum"),
        tickets_resolved=("tickets_resolved", "sum"),
        avg_resolution_time=("avg_resolution_time_hrs", "mean"),
    ).reset_index()
    weekly["resolution_rate"] = (weekly["tickets_resolved"] / weekly["tickets_created"].replace(0, 1)).round(3)
    weekly["backlog_delta"] = weekly["tickets_created"] - weekly["tickets_resolved"]
    return weekly


def sla_compliance_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly SLA compliance trends."""
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month").agg(
        avg_sla_compliance=("sla_compliance_pct", "mean"),
        min_sla_compliance=("sla_compliance_pct", "min"),
        avg_uptime=("system_uptime_pct", "mean"),
        total_customer_impact_min=("customer_impact_minutes", "sum"),
    ).reset_index()
    monthly["avg_sla_compliance"] = monthly["avg_sla_compliance"].round(2)
    monthly["avg_uptime"] = monthly["avg_uptime"].round(4)
    return monthly


def incident_analysis(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly incident counts by severity."""
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month").agg(
        p1_incidents=("incidents_p1", "sum"),
        p2_incidents=("incidents_p2", "sum"),
        p3_incidents=("incidents_p3", "sum"),
    ).reset_index()
    monthly["total_incidents"] = monthly["p1_incidents"] + monthly["p2_incidents"] + monthly["p3_incidents"]
    monthly["critical_ratio"] = (monthly["p1_incidents"] / monthly["total_incidents"].replace(0, 1)).round(3)
    return monthly


def deployment_reliability(df: pd.DataFrame) -> pd.DataFrame:
    """Monthly deployment success rate and rollback frequency."""
    df = df.copy()
    df["month"] = df["date"].dt.to_period("M").astype(str)
    monthly = df.groupby("month").agg(
        total_deployments=("deployment_count", "sum"),
        total_rollbacks=("rollback_count", "sum"),
    ).reset_index()
    monthly["success_rate"] = (
        (monthly["total_deployments"] - monthly["total_rollbacks"])
        / monthly["total_deployments"].replace(0, 1)
    ).round(3)
    monthly["rollback_rate"] = (monthly["total_rollbacks"] / monthly["total_deployments"].replace(0, 1)).round(3)
    return monthly


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = load_data()

    tickets = ticket_resolution_analysis(df)
    sla = sla_compliance_analysis(df)
    incidents = incident_analysis(df)
    deployments = deployment_reliability(df)

    # Combine into summary
    summary = sla.merge(incidents, on="month", how="outer").merge(deployments, on="month", how="outer")
    summary.to_csv(OUTPUT_DIR / "operations_summary.csv", index=False)

    print(f"Operations analysis saved ({len(summary)} months)")
    print(f"  Avg SLA compliance: {summary['avg_sla_compliance'].mean():.1f}%")
    print(f"  Avg uptime: {summary['avg_uptime'].mean():.4f}")
    print(f"  Total P1 incidents: {summary['p1_incidents'].sum():.0f}")
    print(f"  Avg deployment success rate: {summary['success_rate'].mean():.1%}")


if __name__ == "__main__":
    main()
