"""
Marketing Analytics
Channel ROI, campaign performance, attribution analysis, budget optimization.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")


def load_data():
    """Load marketing data."""
    return pd.read_csv(os.path.join(DATA_DIR, "marketing_data.csv"), parse_dates=["date"])


def channel_roi_comparison(df):
    """Compare ROI across marketing channels."""
    channel_stats = df.groupby("channel").agg(
        total_spend=("spend", "sum"),
        total_revenue=("revenue_attributed", "sum"),
        total_impressions=("impressions", "sum"),
        total_clicks=("clicks", "sum"),
        total_conversions=("conversions", "sum"),
        total_leads=("leads_generated", "sum"),
        campaign_count=("campaign_id", "nunique"),
    ).round(2)

    channel_stats["roas"] = (channel_stats["total_revenue"] / channel_stats["total_spend"]).round(4)
    channel_stats["ctr"] = (channel_stats["total_clicks"] / channel_stats["total_impressions"]).round(6)
    channel_stats["conversion_rate"] = (channel_stats["total_conversions"] / channel_stats["total_clicks"]).round(6)
    channel_stats["cpa"] = (channel_stats["total_spend"] / channel_stats["total_conversions"]).round(2)
    channel_stats["cpl"] = (channel_stats["total_spend"] / channel_stats["total_leads"]).round(2)
    channel_stats["revenue_per_conversion"] = (
        channel_stats["total_revenue"] / channel_stats["total_conversions"]
    ).round(2)

    return channel_stats


def campaign_performance_funnel(df):
    """Analyze campaign funnel: impressions → clicks → conversions."""
    funnel = {
        "stage": ["Impressions", "Clicks", "Conversions", "Leads"],
        "total": [
            df["impressions"].sum(),
            df["clicks"].sum(),
            df["conversions"].sum(),
            df["leads_generated"].sum(),
        ],
    }
    funnel_df = pd.DataFrame(funnel)
    funnel_df["conversion_from_previous"] = (
        funnel_df["total"] / funnel_df["total"].shift(1)
    ).round(6)
    funnel_df["pct_of_top"] = (funnel_df["total"] / funnel_df["total"].iloc[0]).round(8)

    return funnel_df


def attribution_analysis(df):
    """Analyze attribution and channel contribution."""
    monthly_channel = df.groupby([df["date"].dt.to_period("M"), "channel"]).agg(
        spend=("spend", "sum"),
        revenue=("revenue_attributed", "sum"),
        conversions=("conversions", "sum"),
    ).reset_index()
    monthly_channel["date"] = monthly_channel["date"].astype(str)

    # Channel contribution share
    total_revenue = df["revenue_attributed"].sum()
    channel_share = df.groupby("channel")["revenue_attributed"].sum() / total_revenue
    channel_share = channel_share.round(4).reset_index(name="revenue_share")

    return monthly_channel, channel_share


def budget_optimization(df):
    """Generate budget optimization recommendations."""
    channel_efficiency = df.groupby("channel").agg(
        total_spend=("spend", "sum"),
        total_revenue=("revenue_attributed", "sum"),
        total_conversions=("conversions", "sum"),
    ).round(2)

    channel_efficiency["roas"] = (
        channel_efficiency["total_revenue"] / channel_efficiency["total_spend"]
    ).round(4)
    channel_efficiency["marginal_cpa"] = (
        channel_efficiency["total_spend"] / channel_efficiency["total_conversions"]
    ).round(2)

    # Rank channels by efficiency
    channel_efficiency["efficiency_rank"] = channel_efficiency["roas"].rank(ascending=False).astype(int)

    # Recommendation: shift budget toward higher ROAS channels
    avg_roas = channel_efficiency["roas"].mean()
    channel_efficiency["recommendation"] = channel_efficiency["roas"].apply(
        lambda x: "Increase Budget" if x > avg_roas * 1.2
        else "Maintain Budget" if x > avg_roas * 0.8
        else "Decrease Budget"
    )

    return channel_efficiency


def main():
    """Run all marketing analyses and export summary."""
    print("Running Marketing Analysis...")
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    df = load_data()

    channel_roi = channel_roi_comparison(df)
    funnel_df = campaign_performance_funnel(df)
    monthly_channel, channel_share = attribution_analysis(df)
    budget_recs = budget_optimization(df)

    # Build summary
    summary_rows = []

    # Overall metrics
    for metric, value in [
        ("total_spend", df["spend"].sum()),
        ("total_revenue_attributed", df["revenue_attributed"].sum()),
        ("overall_roas", df["revenue_attributed"].sum() / df["spend"].sum()),
        ("total_impressions", df["impressions"].sum()),
        ("total_clicks", df["clicks"].sum()),
        ("total_conversions", df["conversions"].sum()),
        ("overall_ctr", df["clicks"].sum() / df["impressions"].sum()),
        ("overall_conversion_rate", df["conversions"].sum() / df["clicks"].sum()),
        ("overall_cpa", df["spend"].sum() / df["conversions"].sum()),
        ("total_campaigns", df["campaign_id"].nunique()),
    ]:
        summary_rows.append({"metric": metric, "dimension": "overall", "value": round(value, 4)})

    # Channel ROAS
    for channel, row in channel_roi.iterrows():
        summary_rows.append({"metric": "channel_roas", "dimension": channel, "value": row["roas"]})

    # Channel CPA
    for channel, row in channel_roi.iterrows():
        summary_rows.append({"metric": "channel_cpa", "dimension": channel, "value": row["cpa"]})

    # Revenue share
    for _, row in channel_share.iterrows():
        summary_rows.append({
            "metric": "channel_revenue_share",
            "dimension": row["channel"],
            "value": row["revenue_share"],
        })

    # Budget recommendations
    for channel, row in budget_recs.iterrows():
        summary_rows.append({
            "metric": "budget_recommendation",
            "dimension": channel,
            "value": row["recommendation"],
        })

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(ANALYSIS_DIR, "marketing_summary.csv"), index=False)

    print(f"  Total Spend: ${df['spend'].sum():,.2f}")
    print(f"  Total Revenue Attributed: ${df['revenue_attributed'].sum():,.2f}")
    print(f"  Overall ROAS: {df['revenue_attributed'].sum() / df['spend'].sum():.2f}x")
    print(f"  Summary exported to: {os.path.join(ANALYSIS_DIR, 'marketing_summary.csv')}")


if __name__ == "__main__":
    main()
