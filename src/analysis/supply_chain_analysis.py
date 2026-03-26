"""
Supply Chain Analysis
Supplier scorecard, lead time, inventory optimization, on-time delivery, defects.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")


def load_data():
    """Load supply chain data."""
    return pd.read_csv(os.path.join(DATA_DIR, "supply_chain_data.csv"),
                       parse_dates=["order_date", "ship_date", "delivery_date"])


def supplier_performance_scorecard(df):
    """Create composite supplier performance scorecard."""
    supplier_stats = df.groupby("supplier").agg(
        total_orders=("order_id", "count"),
        total_quantity=("quantity", "sum"),
        avg_unit_cost=("unit_cost", "mean"),
        avg_lead_time=("lead_time_days", "mean"),
        on_time_rate=("on_time_delivery", "mean"),
        avg_defect_rate=("defect_rate", "mean"),
        stockout_rate=("stockout_flag", "mean"),
        avg_shipping_cost=("shipping_cost", "mean"),
    ).round(4)

    # Composite score (0-100)
    supplier_stats["quality_score"] = ((1 - supplier_stats["avg_defect_rate"]) * 100).round(1)
    supplier_stats["delivery_score"] = (supplier_stats["on_time_rate"] * 100).round(1)
    supplier_stats["lead_time_score"] = (
        (1 - (supplier_stats["avg_lead_time"] - supplier_stats["avg_lead_time"].min()) /
         (supplier_stats["avg_lead_time"].max() - supplier_stats["avg_lead_time"].min())) * 100
    ).round(1)

    supplier_stats["composite_score"] = (
        supplier_stats["delivery_score"] * 0.4 +
        supplier_stats["quality_score"] * 0.3 +
        supplier_stats["lead_time_score"] * 0.3
    ).round(1)

    # Grade
    supplier_stats["grade"] = supplier_stats["composite_score"].apply(
        lambda x: "A" if x >= 85 else "B" if x >= 70 else "C" if x >= 55 else "D"
    )

    return supplier_stats.sort_values("composite_score", ascending=False)


def lead_time_analysis(df):
    """Analyze lead time distribution and categories."""
    lead_time_stats = {
        "mean": df["lead_time_days"].mean(),
        "median": df["lead_time_days"].median(),
        "std": df["lead_time_days"].std(),
        "p90": df["lead_time_days"].quantile(0.90),
        "p95": df["lead_time_days"].quantile(0.95),
        "min": df["lead_time_days"].min(),
        "max": df["lead_time_days"].max(),
    }

    df["lead_time_category"] = pd.cut(
        df["lead_time_days"],
        bins=[0, 3, 7, 14, 100],
        labels=["Express (1-3)", "Standard (4-7)", "Extended (8-14)", "Delayed (15+)"]
    )

    category_dist = df["lead_time_category"].value_counts(normalize=True).round(4)

    lead_by_supplier = df.groupby("supplier")["lead_time_days"].agg(
        ["mean", "median", "std"]
    ).round(2).sort_values("mean")

    return lead_time_stats, category_dist, lead_by_supplier


def inventory_optimization(df):
    """Calculate EOQ and safety stock for inventory optimization."""
    category_stats = df.groupby("product_category").agg(
        avg_daily_demand=("quantity", lambda x: x.sum() / df["order_date"].nunique()),
        demand_std=("quantity", "std"),
        avg_unit_cost=("unit_cost", "mean"),
        avg_lead_time=("lead_time_days", "mean"),
        lead_time_std=("lead_time_days", "std"),
        avg_inventory=("inventory_level", "mean"),
        avg_reorder_point=("reorder_point", "mean"),
    ).round(2)

    # EOQ = sqrt(2 * D * S / H) where D=annual demand, S=order cost, H=holding cost
    ordering_cost = 50  # Fixed cost per order
    holding_rate = 0.25  # 25% of unit cost
    service_level_z = 1.65  # 95% service level

    category_stats["annual_demand"] = (category_stats["avg_daily_demand"] * 365).round(0)
    category_stats["holding_cost"] = (category_stats["avg_unit_cost"] * holding_rate).round(2)
    category_stats["eoq"] = np.sqrt(
        2 * category_stats["annual_demand"] * ordering_cost / category_stats["holding_cost"]
    ).round(0)

    # Safety stock = z * sqrt(LT * σd² + d² * σLT²)
    category_stats["safety_stock"] = (service_level_z * np.sqrt(
        category_stats["avg_lead_time"] * category_stats["demand_std"] ** 2 +
        category_stats["avg_daily_demand"] ** 2 * category_stats["lead_time_std"] ** 2
    )).round(0)

    category_stats["optimal_reorder_point"] = (
        category_stats["avg_daily_demand"] * category_stats["avg_lead_time"] +
        category_stats["safety_stock"]
    ).round(0)

    return category_stats


def on_time_delivery_analysis(df):
    """Analyze on-time delivery rates by various dimensions."""
    otd_by_warehouse = df.groupby("warehouse").agg(
        total_orders=("order_id", "count"),
        on_time=("on_time_delivery", "sum"),
        otd_rate=("on_time_delivery", "mean"),
    ).round(4)

    otd_by_category = df.groupby("product_category").agg(
        total_orders=("order_id", "count"),
        otd_rate=("on_time_delivery", "mean"),
    ).round(4)

    df["order_month"] = df["order_date"].dt.to_period("M")
    otd_trend = df.groupby("order_month").agg(
        otd_rate=("on_time_delivery", "mean"),
        order_count=("order_id", "count"),
    ).round(4)
    otd_trend.index = otd_trend.index.astype(str)

    return otd_by_warehouse, otd_by_category, otd_trend


def defect_rate_analysis(df):
    """Analyze defect rates for Pareto analysis."""
    defect_by_supplier = df.groupby("supplier").agg(
        avg_defect_rate=("defect_rate", "mean"),
        total_orders=("order_id", "count"),
        total_quantity=("quantity", "sum"),
    ).sort_values("avg_defect_rate", ascending=False).round(4)

    defect_by_supplier["defect_contribution"] = (
        defect_by_supplier["avg_defect_rate"] * defect_by_supplier["total_quantity"]
    )
    total_defect_contribution = defect_by_supplier["defect_contribution"].sum()
    defect_by_supplier["pct_contribution"] = (
        defect_by_supplier["defect_contribution"] / total_defect_contribution
    ).round(4)
    defect_by_supplier["cumulative_pct"] = defect_by_supplier["pct_contribution"].cumsum().round(4)

    defect_by_category = df.groupby("product_category")["defect_rate"].mean().round(4).sort_values(ascending=False)

    return defect_by_supplier, defect_by_category


def main():
    """Run all supply chain analyses and export summary."""
    print("Running Supply Chain Analysis...")
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    df = load_data()

    scorecard = supplier_performance_scorecard(df)
    lt_stats, lt_dist, lt_supplier = lead_time_analysis(df)
    inventory = inventory_optimization(df)
    otd_wh, otd_cat, otd_trend = on_time_delivery_analysis(df)
    defect_supplier, defect_cat = defect_rate_analysis(df)

    # Build summary
    summary_rows = []

    # Overall metrics
    for metric, value in [
        ("total_orders", len(df)),
        ("overall_otd_rate", df["on_time_delivery"].mean()),
        ("avg_lead_time_days", df["lead_time_days"].mean()),
        ("avg_defect_rate", df["defect_rate"].mean()),
        ("stockout_rate", df["stockout_flag"].mean()),
        ("total_shipping_cost", df["shipping_cost"].sum()),
    ]:
        summary_rows.append({"metric": metric, "dimension": "overall", "value": round(value, 4)})

    # Top 5 suppliers by score
    for supplier, row in scorecard.head(5).iterrows():
        summary_rows.append({
            "metric": "top_supplier_score",
            "dimension": supplier,
            "value": row["composite_score"],
        })

    # Lead time stats
    for stat, value in lt_stats.items():
        summary_rows.append({"metric": f"lead_time_{stat}", "dimension": "overall", "value": round(value, 2)})

    # OTD by warehouse
    for wh, row in otd_wh.iterrows():
        summary_rows.append({"metric": "otd_by_warehouse", "dimension": wh, "value": row["otd_rate"]})

    # Inventory optimization
    for cat, row in inventory.iterrows():
        summary_rows.append({"metric": "eoq", "dimension": cat, "value": row["eoq"]})
        summary_rows.append({"metric": "safety_stock", "dimension": cat, "value": row["safety_stock"]})

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(ANALYSIS_DIR, "supply_chain_summary.csv"), index=False)

    print(f"  Total Orders: {len(df):,}")
    print(f"  Overall OTD Rate: {df['on_time_delivery'].mean():.2%}")
    print(f"  Avg Lead Time: {df['lead_time_days'].mean():.1f} days")
    print(f"  Summary exported to: {os.path.join(ANALYSIS_DIR, 'supply_chain_summary.csv')}")


if __name__ == "__main__":
    main()
