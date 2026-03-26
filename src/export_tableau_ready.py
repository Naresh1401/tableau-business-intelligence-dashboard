"""
Export Tableau-Ready Datasets
Reads generated CSVs, creates joined/denormalized views, adds calculated columns,
and exports optimized CSVs for Tableau consumption.
"""

import os
import pandas as pd
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
TABLEAU_DIR = os.path.join(DATA_DIR, "tableau_ready")


def ensure_dirs():
    """Create output directories."""
    os.makedirs(TABLEAU_DIR, exist_ok=True)


def export_sales_tableau():
    """Export enriched sales data for Tableau."""
    print("  Exporting sales data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "sales_data.csv"), parse_dates=["date"])

    # Add calculated columns
    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.quarter
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.day_name()
    df["profit_margin"] = (df["profit"] / df["revenue"]).round(4)
    df["revenue_after_discount"] = (df["revenue"] * (1 - df["discount_pct"])).round(2)

    df["discount_tier"] = pd.cut(
        df["discount_pct"],
        bins=[-0.01, 0, 0.05, 0.10, 0.20, 1.0],
        labels=["No Discount", "0-5%", "5-10%", "10-20%", "20%+"]
    )

    df["revenue_band"] = pd.cut(
        df["revenue"],
        bins=[0, 100, 500, 2000, 10000, float("inf")],
        labels=["<$100", "$100-500", "$500-2K", "$2K-10K", "$10K+"]
    )

    df.to_csv(os.path.join(TABLEAU_DIR, "sales_enriched.csv"), index=False)
    return df


def export_marketing_tableau():
    """Export enriched marketing data for Tableau."""
    print("  Exporting marketing data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "marketing_data.csv"), parse_dates=["date"])

    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.quarter
    df["month"] = df["date"].dt.month

    df["roas_category"] = pd.cut(
        df["roas"],
        bins=[-0.01, 1.0, 2.0, 5.0, float("inf")],
        labels=["Negative ROI", "Low (1-2x)", "Good (2-5x)", "Excellent (5x+)"]
    )

    df["efficiency_score"] = (df["roas"] * df["conversion_rate"]).round(6)

    df["cost_per_click"] = np.where(df["clicks"] > 0, (df["spend"] / df["clicks"]).round(4), 0)
    df["cost_per_lead"] = np.where(
        df["leads_generated"] > 0,
        (df["spend"] / df["leads_generated"]).round(4),
        0
    )
    df["revenue_per_conversion"] = np.where(
        df["conversions"] > 0,
        (df["revenue_attributed"] / df["conversions"]).round(2),
        0
    )

    df.to_csv(os.path.join(TABLEAU_DIR, "marketing_enriched.csv"), index=False)
    return df


def export_customer_tableau():
    """Export enriched customer data for Tableau."""
    print("  Exporting customer data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "customer_data.csv"),
                     parse_dates=["signup_date", "last_purchase_date"])

    reference_date = df["last_purchase_date"].max() + pd.Timedelta(days=1)
    df["recency_days"] = (reference_date - df["last_purchase_date"]).dt.days
    df["tenure_months"] = ((reference_date - df["signup_date"]).dt.days / 30).round(0).astype(int)

    # RFM scores
    df["r_score"] = pd.qcut(df["recency_days"], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    df["f_score"] = pd.qcut(df["total_orders"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    df["m_score"] = pd.qcut(df["lifetime_value"].rank(method="first"), q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    df["rfm_score"] = df["r_score"] + df["f_score"] + df["m_score"]

    df["rfm_segment"] = df["rfm_score"].apply(
        lambda x: "Champions" if x >= 13
        else "Loyal" if x >= 10
        else "Potential Loyalist" if x >= 8
        else "At Risk" if x >= 6
        else "Needs Attention" if x >= 4
        else "Lost"
    )

    df["clv_tier"] = pd.cut(
        df["lifetime_value"],
        bins=[0, 200, 1000, 5000, float("inf")],
        labels=["Bronze", "Silver", "Gold", "Platinum"]
    )

    df["nps_category"] = df["nps_score"].apply(
        lambda x: "Promoter" if x >= 9 else "Passive" if x >= 7 else "Detractor"
    )

    df["churn_risk"] = df["recency_days"].apply(
        lambda x: "High" if x > 365 else "Medium" if x > 180 else "Low" if x > 90 else "Active"
    )

    df["signup_cohort"] = df["signup_date"].dt.to_period("Q").astype(str)

    df.to_csv(os.path.join(TABLEAU_DIR, "customer_enriched.csv"), index=False)
    return df


def export_supply_chain_tableau():
    """Export enriched supply chain data for Tableau."""
    print("  Exporting supply chain data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "supply_chain_data.csv"),
                     parse_dates=["order_date", "ship_date", "delivery_date"])

    df["year"] = df["order_date"].dt.year
    df["quarter"] = df["order_date"].dt.quarter
    df["month"] = df["order_date"].dt.month

    df["processing_time"] = (df["ship_date"] - df["order_date"]).dt.days
    df["transit_time"] = (df["delivery_date"] - df["ship_date"]).dt.days
    df["total_cost"] = (df["quantity"] * df["unit_cost"] + df["shipping_cost"]).round(2)
    df["cost_per_unit"] = ((df["total_cost"]) / df["quantity"]).round(2)

    df["lead_time_category"] = pd.cut(
        df["lead_time_days"],
        bins=[0, 3, 7, 14, 100],
        labels=["Express", "Standard", "Extended", "Delayed"]
    )

    df["inventory_status"] = np.where(
        df["inventory_level"] <= df["reorder_point"] * 0.5, "Critical",
        np.where(df["inventory_level"] <= df["reorder_point"], "Low",
                 np.where(df["inventory_level"] <= df["reorder_point"] * 1.5, "Adequate", "Excess"))
    )

    df["defect_category"] = pd.cut(
        df["defect_rate"],
        bins=[-0.01, 0.01, 0.03, 0.05, 1.0],
        labels=["Excellent (<1%)", "Good (1-3%)", "Acceptable (3-5%)", "Poor (5%+)"]
    )

    df.to_csv(os.path.join(TABLEAU_DIR, "supply_chain_enriched.csv"), index=False)
    return df


def export_finance_tableau():
    """Export enriched finance data for Tableau."""
    print("  Exporting finance data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "finance_data.csv"), parse_dates=["month"])

    df["year"] = df["month"].dt.year
    df["quarter"] = df["month"].dt.quarter
    df["month_num"] = df["month"].dt.month
    df["month_name"] = df["month"].dt.strftime("%B")

    df["gross_margin"] = (df["gross_profit"] / df["revenue"]).round(4)
    df["operating_margin"] = (df["ebitda"] / df["revenue"]).round(4)
    df["net_margin"] = (df["net_income"] / df["revenue"]).round(4)

    df["cumulative_revenue"] = df["revenue"].cumsum().round(2)
    df["cumulative_cash_flow"] = df["cash_flow"].cumsum().round(2)

    df["revenue_mom_growth"] = df["revenue"].pct_change().round(4)

    # Waterfall components for latest year
    df["cogs_negative"] = -df["cogs"]
    df["opex_negative"] = -df["operating_expenses"]

    df.to_csv(os.path.join(TABLEAU_DIR, "finance_enriched.csv"), index=False)
    return df


def export_hr_tableau():
    """Export enriched HR data for Tableau."""
    print("  Exporting HR data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "hr_workforce_data.csv"), parse_dates=["hire_date"])

    df["hire_year"] = df["hire_date"].dt.year
    df["hire_quarter"] = df["hire_date"].dt.quarter

    df["tenure_band"] = pd.cut(
        df["tenure_months"],
        bins=[0, 12, 24, 48, 96, 300],
        labels=["<1 Year", "1-2 Years", "2-4 Years", "4-8 Years", "8+ Years"]
    )

    df["age_band"] = pd.cut(
        df["age"],
        bins=[20, 25, 30, 35, 40, 50, 70],
        labels=["22-25", "26-30", "31-35", "36-40", "41-50", "51+"]
    )

    df["performance_band"] = pd.cut(
        df["performance_score"],
        bins=[0, 2, 3, 4, 5.1],
        labels=["Needs Improvement", "Meets Expectations", "Exceeds Expectations", "Exceptional"]
    )

    df["engagement_category"] = pd.cut(
        df["engagement_score"],
        bins=[0, 4, 6, 8, 10.1],
        labels=["Disengaged", "Neutral", "Engaged", "Highly Engaged"]
    )

    df["overtime_category"] = pd.cut(
        df["overtime_hours"],
        bins=[-0.1, 2, 8, 20, 200],
        labels=["Minimal", "Low", "Moderate", "High"]
    )

    df["salary_band"] = pd.cut(
        df["salary"],
        bins=[0, 60000, 90000, 130000, 200000, 500000],
        labels=["<$60K", "$60-90K", "$90-130K", "$130-200K", "$200K+"]
    )

    df.to_csv(os.path.join(TABLEAU_DIR, "hr_enriched.csv"), index=False)
    return df


def export_genai_tableau():
    """Export enriched Gen AI data for Tableau."""
    print("  Exporting Gen AI data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "genai_usage_data.csv"), parse_dates=["timestamp"])

    df["date"] = df["timestamp"].dt.date
    df["year"] = df["timestamp"].dt.year
    df["month"] = df["timestamp"].dt.month
    df["week"] = df["timestamp"].dt.isocalendar().week.astype(int)
    df["hour"] = df["timestamp"].dt.hour
    df["day_of_week"] = df["timestamp"].dt.day_name()

    df["total_tokens"] = df["tokens_input"] + df["tokens_output"]
    df["cost_per_1k_tokens"] = np.where(
        df["total_tokens"] > 0,
        (df["cost_usd"] / df["total_tokens"] * 1000).round(4),
        0
    )
    df["token_ratio"] = np.where(
        df["tokens_input"] > 0,
        (df["tokens_output"] / df["tokens_input"]).round(4),
        0
    )

    df["latency_category"] = pd.cut(
        df["latency_ms"],
        bins=[0, 500, 1000, 2000, 5000, float("inf")],
        labels=["Fast (<500ms)", "Good (500ms-1s)", "Moderate (1-2s)", "Slow (2-5s)", "Very Slow (5s+)"]
    )

    df["satisfaction_category"] = df["user_satisfaction"].map(
        {1: "Very Unsatisfied", 2: "Unsatisfied", 3: "Neutral", 4: "Satisfied", 5: "Very Satisfied"}
    )

    df["quality_flag"] = np.where(
        (df["error_flag"] == 0) & (df["hallucination_detected"] == 0), "Clean",
        np.where(df["hallucination_detected"] == 1, "Hallucination",
                 "Error")
    )

    df.to_csv(os.path.join(TABLEAU_DIR, "genai_enriched.csv"), index=False)
    return df


def export_operations_tableau():
    """Export enriched operations KPI data for Tableau."""
    print("  Exporting operations data...")
    df = pd.read_csv(os.path.join(DATA_DIR, "operations_kpi_data.csv"), parse_dates=["date"])

    df["year"] = df["date"].dt.year
    df["quarter"] = df["date"].dt.quarter
    df["month"] = df["date"].dt.month
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_of_week"] = df["date"].dt.day_name()
    df["is_weekend"] = df["date"].dt.dayofweek.isin([5, 6]).astype(int)

    df["ticket_backlog"] = (df["tickets_created"] - df["tickets_resolved"]).cumsum()
    df["resolution_rate"] = np.where(
        df["tickets_created"] > 0,
        (df["tickets_resolved"] / df["tickets_created"]).round(4),
        1
    )
    df["total_incidents"] = df["incidents_p1"] + df["incidents_p2"] + df["incidents_p3"]
    df["rollback_rate"] = np.where(
        df["deployment_count"] > 0,
        (df["rollback_count"] / df["deployment_count"]).round(4),
        0
    )

    df["sla_status"] = np.where(df["sla_compliance_pct"] >= 95, "Meeting",
                                np.where(df["sla_compliance_pct"] >= 90, "At Risk", "Breached"))

    df["uptime_status"] = np.where(df["system_uptime_pct"] >= 99.9, "Excellent",
                                   np.where(df["system_uptime_pct"] >= 99.5, "Good",
                                            np.where(df["system_uptime_pct"] >= 99, "Fair", "Poor")))

    df.to_csv(os.path.join(TABLEAU_DIR, "operations_enriched.csv"), index=False)
    return df


def create_data_dictionary():
    """Create a data dictionary for all datasets."""
    print("  Creating data dictionary...")

    dictionary = [
        # Sales
        {"dataset": "sales_enriched", "column": "date", "type": "Date", "description": "Transaction date"},
        {"dataset": "sales_enriched", "column": "region", "type": "String", "description": "Geographic sales region"},
        {"dataset": "sales_enriched", "column": "product_category", "type": "String", "description": "Product category (8 categories)"},
        {"dataset": "sales_enriched", "column": "product", "type": "String", "description": "Specific product name"},
        {"dataset": "sales_enriched", "column": "units_sold", "type": "Integer", "description": "Number of units sold"},
        {"dataset": "sales_enriched", "column": "unit_price", "type": "Float", "description": "Price per unit in USD"},
        {"dataset": "sales_enriched", "column": "revenue", "type": "Float", "description": "Total revenue (units × price)"},
        {"dataset": "sales_enriched", "column": "cost", "type": "Float", "description": "Total cost of goods sold"},
        {"dataset": "sales_enriched", "column": "profit", "type": "Float", "description": "Profit (revenue - cost)"},
        {"dataset": "sales_enriched", "column": "discount_pct", "type": "Float", "description": "Discount percentage applied (0-0.30)"},
        {"dataset": "sales_enriched", "column": "sales_channel", "type": "String", "description": "Sales channel: Online, Retail, Wholesale"},
        {"dataset": "sales_enriched", "column": "sales_rep", "type": "String", "description": "Sales representative name"},
        {"dataset": "sales_enriched", "column": "profit_margin", "type": "Float", "description": "Calculated: profit / revenue"},
        # Marketing
        {"dataset": "marketing_enriched", "column": "campaign_id", "type": "String", "description": "Unique campaign identifier"},
        {"dataset": "marketing_enriched", "column": "channel", "type": "String", "description": "Marketing channel: Email, Social, Search, Display, Affiliate"},
        {"dataset": "marketing_enriched", "column": "impressions", "type": "Integer", "description": "Number of ad impressions"},
        {"dataset": "marketing_enriched", "column": "clicks", "type": "Integer", "description": "Number of clicks"},
        {"dataset": "marketing_enriched", "column": "conversions", "type": "Integer", "description": "Number of conversions"},
        {"dataset": "marketing_enriched", "column": "spend", "type": "Float", "description": "Campaign spend in USD"},
        {"dataset": "marketing_enriched", "column": "revenue_attributed", "type": "Float", "description": "Revenue attributed to campaign"},
        {"dataset": "marketing_enriched", "column": "roas", "type": "Float", "description": "Return on ad spend (revenue/spend)"},
        # Customer
        {"dataset": "customer_enriched", "column": "customer_id", "type": "String", "description": "Unique customer identifier"},
        {"dataset": "customer_enriched", "column": "segment", "type": "String", "description": "Customer segment: Enterprise, SMB, Consumer"},
        {"dataset": "customer_enriched", "column": "lifetime_value", "type": "Float", "description": "Customer lifetime value in USD"},
        {"dataset": "customer_enriched", "column": "churn_flag", "type": "Integer", "description": "Churn indicator: 1=churned, 0=active"},
        {"dataset": "customer_enriched", "column": "nps_score", "type": "Integer", "description": "Net Promoter Score (0-10)"},
        {"dataset": "customer_enriched", "column": "rfm_segment", "type": "String", "description": "RFM segment: Champions, Loyal, etc."},
        {"dataset": "customer_enriched", "column": "clv_tier", "type": "String", "description": "CLV tier: Bronze, Silver, Gold, Platinum"},
        # Supply Chain
        {"dataset": "supply_chain_enriched", "column": "order_id", "type": "String", "description": "Unique order identifier"},
        {"dataset": "supply_chain_enriched", "column": "supplier", "type": "String", "description": "Supplier name (20 suppliers)"},
        {"dataset": "supply_chain_enriched", "column": "warehouse", "type": "String", "description": "Warehouse location"},
        {"dataset": "supply_chain_enriched", "column": "lead_time_days", "type": "Integer", "description": "Order-to-delivery lead time in days"},
        {"dataset": "supply_chain_enriched", "column": "on_time_delivery", "type": "Integer", "description": "On-time delivery flag: 1=on-time, 0=late"},
        {"dataset": "supply_chain_enriched", "column": "defect_rate", "type": "Float", "description": "Product defect rate (0-1)"},
        {"dataset": "supply_chain_enriched", "column": "inventory_status", "type": "String", "description": "Inventory status: Critical, Low, Adequate, Excess"},
        # Finance
        {"dataset": "finance_enriched", "column": "month", "type": "Date", "description": "First day of the month"},
        {"dataset": "finance_enriched", "column": "revenue", "type": "Float", "description": "Monthly revenue in USD"},
        {"dataset": "finance_enriched", "column": "ebitda", "type": "Float", "description": "Earnings before interest, taxes, depreciation, amortization"},
        {"dataset": "finance_enriched", "column": "net_income", "type": "Float", "description": "Net income after all deductions"},
        {"dataset": "finance_enriched", "column": "gross_margin", "type": "Float", "description": "Gross profit / revenue"},
        {"dataset": "finance_enriched", "column": "current_ratio", "type": "Float", "description": "Current assets / current liabilities"},
        # HR
        {"dataset": "hr_enriched", "column": "employee_id", "type": "String", "description": "Unique employee identifier"},
        {"dataset": "hr_enriched", "column": "department", "type": "String", "description": "Department (8 departments)"},
        {"dataset": "hr_enriched", "column": "role_level", "type": "String", "description": "Job level: Junior, Mid, Senior, Lead, Director"},
        {"dataset": "hr_enriched", "column": "salary", "type": "Float", "description": "Annual salary in USD"},
        {"dataset": "hr_enriched", "column": "performance_score", "type": "Float", "description": "Performance rating (1-5)"},
        {"dataset": "hr_enriched", "column": "engagement_score", "type": "Float", "description": "Employee engagement score (1-10)"},
        {"dataset": "hr_enriched", "column": "attrition_flag", "type": "Integer", "description": "Attrition indicator: 1=left, 0=active"},
        # Gen AI
        {"dataset": "genai_enriched", "column": "request_id", "type": "String", "description": "Unique API request identifier"},
        {"dataset": "genai_enriched", "column": "model", "type": "String", "description": "AI model: gpt-4, gpt-3.5, claude, llama"},
        {"dataset": "genai_enriched", "column": "use_case", "type": "String", "description": "Use case: code_gen, summarization, qa, translation, analysis"},
        {"dataset": "genai_enriched", "column": "tokens_input", "type": "Integer", "description": "Number of input tokens"},
        {"dataset": "genai_enriched", "column": "tokens_output", "type": "Integer", "description": "Number of output tokens"},
        {"dataset": "genai_enriched", "column": "latency_ms", "type": "Integer", "description": "Response latency in milliseconds"},
        {"dataset": "genai_enriched", "column": "cost_usd", "type": "Float", "description": "Request cost in USD"},
        {"dataset": "genai_enriched", "column": "hallucination_detected", "type": "Integer", "description": "Hallucination flag: 1=yes, 0=no"},
        # Operations
        {"dataset": "operations_enriched", "column": "date", "type": "Date", "description": "Daily date"},
        {"dataset": "operations_enriched", "column": "tickets_created", "type": "Integer", "description": "Support tickets created"},
        {"dataset": "operations_enriched", "column": "tickets_resolved", "type": "Integer", "description": "Support tickets resolved"},
        {"dataset": "operations_enriched", "column": "sla_compliance_pct", "type": "Float", "description": "SLA compliance percentage"},
        {"dataset": "operations_enriched", "column": "system_uptime_pct", "type": "Float", "description": "System uptime percentage"},
        {"dataset": "operations_enriched", "column": "deployment_count", "type": "Integer", "description": "Number of deployments"},
        {"dataset": "operations_enriched", "column": "customer_impact_minutes", "type": "Float", "description": "Total customer impact time in minutes"},
    ]

    dict_df = pd.DataFrame(dictionary)
    dict_df.to_csv(os.path.join(DATA_DIR, "data_dictionary.csv"), index=False)


def main():
    """Export all Tableau-ready datasets."""
    print("=" * 60)
    print("Exporting Tableau-Ready Datasets")
    print("=" * 60)

    ensure_dirs()

    export_sales_tableau()
    export_marketing_tableau()
    export_customer_tableau()
    export_supply_chain_tableau()
    export_finance_tableau()
    export_hr_tableau()
    export_genai_tableau()
    export_operations_tableau()
    create_data_dictionary()

    print("\n" + "=" * 60)
    print("All Tableau-ready datasets exported!")
    print(f"Output directory: {TABLEAU_DIR}")
    print(f"Data dictionary: {os.path.join(DATA_DIR, 'data_dictionary.csv')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
