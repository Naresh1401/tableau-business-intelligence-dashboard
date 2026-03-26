"""
Customer Analytics
RFM segmentation, churn analysis, CLV distribution, NPS, and cohort retention.
"""

import os
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")


def load_data():
    """Load customer data."""
    df = pd.read_csv(os.path.join(DATA_DIR, "customer_data.csv"),
                     parse_dates=["signup_date", "last_purchase_date"])
    return df


def rfm_analysis(df):
    """Perform RFM (Recency, Frequency, Monetary) segmentation."""
    reference_date = df["last_purchase_date"].max() + pd.Timedelta(days=1)

    df["recency_days"] = (reference_date - df["last_purchase_date"]).dt.days
    df["frequency"] = df["total_orders"]
    df["monetary"] = df["lifetime_value"]

    # Score each dimension 1-5
    df["r_score"] = pd.qcut(df["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    df["f_score"] = pd.qcut(df["frequency"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    df["m_score"] = pd.qcut(df["monetary"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    df["rfm_score"] = df["r_score"] + df["f_score"] + df["m_score"]

    # Segment labels
    def rfm_segment(row):
        if row["rfm_score"] >= 13:
            return "Champions"
        elif row["rfm_score"] >= 10:
            return "Loyal"
        elif row["rfm_score"] >= 8:
            return "Potential Loyalist"
        elif row["rfm_score"] >= 6:
            return "At Risk"
        elif row["rfm_score"] >= 4:
            return "Needs Attention"
        else:
            return "Lost"

    df["rfm_segment"] = df.apply(rfm_segment, axis=1)

    segment_summary = df.groupby("rfm_segment").agg(
        customer_count=("customer_id", "count"),
        avg_recency=("recency_days", "mean"),
        avg_frequency=("frequency", "mean"),
        avg_monetary=("monetary", "mean"),
        avg_rfm_score=("rfm_score", "mean"),
    ).round(2)

    return df, segment_summary


def churn_analysis(df):
    """Analyze churn by segment and other dimensions."""
    churn_by_segment = df.groupby("segment").agg(
        total_customers=("customer_id", "count"),
        churned=("churn_flag", "sum"),
        churn_rate=("churn_flag", "mean"),
        avg_satisfaction=("satisfaction_score", "mean"),
        avg_tickets=("support_tickets", "mean"),
    ).round(4)

    churn_by_region = df.groupby("region").agg(
        total_customers=("customer_id", "count"),
        churned=("churn_flag", "sum"),
        churn_rate=("churn_flag", "mean"),
    ).round(4)

    churn_by_channel = df.groupby("acquisition_channel").agg(
        total_customers=("customer_id", "count"),
        churned=("churn_flag", "sum"),
        churn_rate=("churn_flag", "mean"),
        avg_clv=("lifetime_value", "mean"),
    ).round(4)

    return churn_by_segment, churn_by_region, churn_by_channel


def clv_distribution(df):
    """Analyze customer lifetime value distribution."""
    clv_stats = {
        "mean": df["lifetime_value"].mean(),
        "median": df["lifetime_value"].median(),
        "std": df["lifetime_value"].std(),
        "p25": df["lifetime_value"].quantile(0.25),
        "p75": df["lifetime_value"].quantile(0.75),
        "p90": df["lifetime_value"].quantile(0.90),
        "p99": df["lifetime_value"].quantile(0.99),
    }

    clv_by_segment = df.groupby("segment").agg(
        mean_clv=("lifetime_value", "mean"),
        median_clv=("lifetime_value", "median"),
        total_clv=("lifetime_value", "sum"),
    ).round(2)

    return clv_stats, clv_by_segment


def nps_analysis(df):
    """Analyze Net Promoter Score."""
    df["nps_category"] = pd.cut(
        df["nps_score"],
        bins=[-1, 6, 8, 10],
        labels=["Detractor", "Passive", "Promoter"]
    )

    nps_dist = df["nps_category"].value_counts(normalize=True).round(4)
    promoters = (df["nps_score"] >= 9).mean()
    detractors = (df["nps_score"] <= 6).mean()
    nps_overall = round((promoters - detractors) * 100, 2)

    nps_by_segment = df.groupby("segment").apply(
        lambda g: round(((g["nps_score"] >= 9).mean() - (g["nps_score"] <= 6).mean()) * 100, 2)
    ).reset_index(name="nps_score")

    return nps_overall, nps_dist, nps_by_segment


def cohort_retention(df):
    """Perform cohort retention analysis."""
    df["cohort_month"] = df["signup_date"].dt.to_period("M")
    df["last_active_month"] = df["last_purchase_date"].dt.to_period("M")
    df["cohort_index"] = (df["last_active_month"] - df["cohort_month"]).apply(lambda x: x.n if pd.notna(x) else 0)

    cohort_data = df.groupby(["cohort_month", "cohort_index"]).agg(
        customers=("customer_id", "nunique"),
    ).reset_index()

    cohort_sizes = df.groupby("cohort_month")["customer_id"].nunique().reset_index(name="cohort_size")
    cohort_data = cohort_data.merge(
        cohort_sizes, on="cohort_month", how="left"
    )
    cohort_data["retention_rate"] = (cohort_data["customers"] / cohort_data["cohort_size"]).round(4)

    return cohort_data


def main():
    """Run all customer analyses and export summary."""
    print("Running Customer Analysis...")
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    df = load_data()

    df, rfm_summary = rfm_analysis(df)
    churn_seg, churn_reg, churn_ch = churn_analysis(df)
    clv_stats, clv_seg = clv_distribution(df)
    nps_overall, nps_dist, nps_by_seg = nps_analysis(df)
    cohort_data = cohort_retention(df)

    # Build summary
    summary_rows = []

    # Overall metrics
    for metric, value in [
        ("total_customers", len(df)),
        ("overall_churn_rate", df["churn_flag"].mean()),
        ("avg_clv", df["lifetime_value"].mean()),
        ("median_clv", df["lifetime_value"].median()),
        ("nps_overall", nps_overall),
        ("avg_satisfaction", df["satisfaction_score"].mean()),
        ("avg_orders", df["total_orders"].mean()),
    ]:
        summary_rows.append({"metric": metric, "dimension": "overall", "value": round(value, 4)})

    # RFM segment distribution
    for seg, row in rfm_summary.iterrows():
        summary_rows.append({"metric": "rfm_segment_count", "dimension": seg, "value": row["customer_count"]})

    # Churn by segment
    for seg, row in churn_seg.iterrows():
        summary_rows.append({"metric": "churn_rate_by_segment", "dimension": seg, "value": row["churn_rate"]})

    # CLV by segment
    for seg, row in clv_seg.iterrows():
        summary_rows.append({"metric": "avg_clv_by_segment", "dimension": seg, "value": row["mean_clv"]})

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(ANALYSIS_DIR, "customer_summary.csv"), index=False)

    print(f"  Total Customers: {len(df):,}")
    print(f"  Overall Churn Rate: {df['churn_flag'].mean():.2%}")
    print(f"  Average CLV: ${df['lifetime_value'].mean():,.2f}")
    print(f"  NPS: {nps_overall}")
    print(f"  Summary exported to: {os.path.join(ANALYSIS_DIR, 'customer_summary.csv')}")


if __name__ == "__main__":
    main()
