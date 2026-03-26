"""
HR & Workforce Analytics
Demographics, attrition, compensation equity, performance-engagement, training ROI.
"""

import os
import pandas as pd
import numpy as np
from scipy import stats as scipy_stats

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
ANALYSIS_DIR = os.path.join(DATA_DIR, "analysis")


def load_data():
    """Load HR workforce data."""
    return pd.read_csv(os.path.join(DATA_DIR, "hr_workforce_data.csv"), parse_dates=["hire_date"])


def workforce_demographics(df):
    """Analyze workforce demographics."""
    by_dept = df.groupby("department").agg(
        headcount=("employee_id", "count"),
        avg_salary=("salary", "mean"),
        avg_tenure=("tenure_months", "mean"),
        avg_age=("age", "mean"),
    ).round(2)

    by_level = df.groupby("role_level").agg(
        headcount=("employee_id", "count"),
        avg_salary=("salary", "mean"),
        avg_performance=("performance_score", "mean"),
    ).round(2)

    by_gender = df.groupby("gender").agg(
        headcount=("employee_id", "count"),
        pct=("employee_id", lambda x: round(len(x) / len(df), 4)),
        avg_salary=("salary", "mean"),
    ).round(2)

    by_location = df.groupby("location").agg(
        headcount=("employee_id", "count"),
        avg_salary=("salary", "mean"),
    ).round(2)

    return by_dept, by_level, by_gender, by_location


def attrition_analysis(df):
    """Analyze attrition by department and role level."""
    attrition_by_dept = df.groupby("department").agg(
        total=("employee_id", "count"),
        attrited=("attrition_flag", "sum"),
        attrition_rate=("attrition_flag", "mean"),
        avg_engagement=("engagement_score", "mean"),
        avg_performance=("performance_score", "mean"),
    ).round(4)

    attrition_by_level = df.groupby("role_level").agg(
        total=("employee_id", "count"),
        attrited=("attrition_flag", "sum"),
        attrition_rate=("attrition_flag", "mean"),
    ).round(4)

    attrition_by_tenure = df.groupby(
        pd.cut(df["tenure_months"], bins=[0, 12, 24, 48, 96, 200],
               labels=["0-12mo", "12-24mo", "24-48mo", "48-96mo", "96mo+"])
    ).agg(
        total=("employee_id", "count"),
        attrition_rate=("attrition_flag", "mean"),
    ).round(4)

    return attrition_by_dept, attrition_by_level, attrition_by_tenure


def compensation_equity(df):
    """Analyze compensation equity across demographics."""
    # Gender pay gap by role level
    pay_by_gender_level = df.groupby(["gender", "role_level"])["salary"].agg(
        ["mean", "median", "count"]
    ).round(2)

    # Overall gender pay gap
    avg_by_gender = df.groupby("gender")["salary"].mean()
    if "Male" in avg_by_gender.index and "Female" in avg_by_gender.index:
        gender_gap = round(
            (avg_by_gender["Male"] - avg_by_gender["Female"]) / avg_by_gender["Male"], 4
        )
    else:
        gender_gap = None

    # Pay ratio (highest level avg / lowest level avg)
    level_pay = df.groupby("role_level")["salary"].mean().sort_values()
    pay_ratio = round(level_pay.iloc[-1] / level_pay.iloc[0], 2) if len(level_pay) > 1 else None

    # Compensation by department and level
    comp_matrix = df.groupby(["department", "role_level"])["salary"].mean().round(2).unstack(fill_value=0)

    return pay_by_gender_level, gender_gap, pay_ratio, comp_matrix


def performance_engagement_correlation(df):
    """Analyze correlation between performance and engagement."""
    corr, p_value = scipy_stats.pearsonr(df["performance_score"], df["engagement_score"])

    pe_matrix = df.groupby([
        pd.cut(df["performance_score"], bins=[0, 2, 3, 4, 5],
               labels=["Low", "Below Avg", "Above Avg", "High"]),
        pd.cut(df["engagement_score"], bins=[0, 3, 5, 7, 10],
               labels=["Disengaged", "Neutral", "Engaged", "Highly Engaged"]),
    ]).size().unstack(fill_value=0)

    # Impact on attrition
    low_engagement = df[df["engagement_score"] < 4]["attrition_flag"].mean()
    high_engagement = df[df["engagement_score"] >= 8]["attrition_flag"].mean()

    stats = {
        "correlation": round(corr, 4),
        "p_value": round(p_value, 6),
        "low_engagement_attrition": round(low_engagement, 4),
        "high_engagement_attrition": round(high_engagement, 4),
    }

    return stats, pe_matrix


def training_roi_analysis(df):
    """Analyze training hours impact on performance."""
    df["training_category"] = pd.cut(
        df["training_hours"],
        bins=[-1, 5, 15, 30, 200],
        labels=["Minimal (0-5h)", "Low (6-15h)", "Moderate (16-30h)", "High (30h+)"]
    )

    training_impact = df.groupby("training_category").agg(
        employee_count=("employee_id", "count"),
        avg_performance=("performance_score", "mean"),
        avg_engagement=("engagement_score", "mean"),
        promotion_rate=("promotion_flag", "mean"),
        attrition_rate=("attrition_flag", "mean"),
    ).round(4)

    by_dept = df.groupby("department").agg(
        avg_training_hours=("training_hours", "mean"),
        avg_performance=("performance_score", "mean"),
        promotion_rate=("promotion_flag", "mean"),
    ).round(4)

    return training_impact, by_dept


def main():
    """Run all HR analyses and export summary."""
    print("Running HR & Workforce Analysis...")
    os.makedirs(ANALYSIS_DIR, exist_ok=True)

    df = load_data()

    by_dept, by_level, by_gender, by_location = workforce_demographics(df)
    att_dept, att_level, att_tenure = attrition_analysis(df)
    pay_gl, gender_gap, pay_ratio, comp_matrix = compensation_equity(df)
    pe_stats, pe_matrix = performance_engagement_correlation(df)
    training_impact, training_dept = training_roi_analysis(df)

    # Build summary
    summary_rows = []

    # Overall metrics
    for metric, value in [
        ("total_headcount", len(df)),
        ("overall_attrition_rate", df["attrition_flag"].mean()),
        ("avg_salary", df["salary"].mean()),
        ("median_salary", df["salary"].median()),
        ("avg_performance", df["performance_score"].mean()),
        ("avg_engagement", df["engagement_score"].mean()),
        ("avg_tenure_months", df["tenure_months"].mean()),
        ("avg_training_hours", df["training_hours"].mean()),
        ("promotion_rate", df["promotion_flag"].mean()),
        ("perf_engagement_correlation", pe_stats["correlation"]),
    ]:
        summary_rows.append({"metric": metric, "dimension": "overall", "value": round(value, 4)})

    if gender_gap is not None:
        summary_rows.append({"metric": "gender_pay_gap", "dimension": "overall", "value": gender_gap})
    if pay_ratio is not None:
        summary_rows.append({"metric": "director_to_junior_pay_ratio", "dimension": "overall", "value": pay_ratio})

    # Headcount by department
    for dept, row in by_dept.iterrows():
        summary_rows.append({"metric": "headcount_by_dept", "dimension": dept, "value": row["headcount"]})

    # Attrition by department
    for dept, row in att_dept.iterrows():
        summary_rows.append({"metric": "attrition_by_dept", "dimension": dept, "value": row["attrition_rate"]})

    # Salary by level
    for level, row in by_level.iterrows():
        summary_rows.append({"metric": "avg_salary_by_level", "dimension": level, "value": row["avg_salary"]})

    # Gender distribution
    for gender, row in by_gender.iterrows():
        summary_rows.append({"metric": "gender_distribution", "dimension": gender, "value": row["pct"]})

    summary_df = pd.DataFrame(summary_rows)
    summary_df.to_csv(os.path.join(ANALYSIS_DIR, "hr_summary.csv"), index=False)

    print(f"  Total Headcount: {len(df):,}")
    print(f"  Attrition Rate: {df['attrition_flag'].mean():.2%}")
    print(f"  Avg Salary: ${df['salary'].mean():,.2f}")
    print(f"  Perf-Engagement Correlation: {pe_stats['correlation']:.4f}")
    print(f"  Summary exported to: {os.path.join(ANALYSIS_DIR, 'hr_summary.csv')}")


if __name__ == "__main__":
    main()
