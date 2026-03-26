"""
Master data generation script for Enterprise BI Dashboard Suite.
Generates all synthetic datasets and saves them to data/ directory.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from faker import Faker

fake = Faker()
Faker.seed(42)
np.random.seed(42)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")


def ensure_dirs():
    """Create data directories if they don't exist."""
    for subdir in ["", "analysis", "tableau_ready"]:
        path = os.path.join(DATA_DIR, subdir)
        os.makedirs(path, exist_ok=True)


def generate_sales_data():
    """Generate 50K rows of sales data with seasonality and trends."""
    print("Generating sales data...")
    n = 50000
    regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books",
                  "Food & Beverage", "Health & Beauty", "Automotive"]
    channels = ["Online", "Retail", "Wholesale"]

    products = {
        "Electronics": ["Laptop", "Smartphone", "Tablet", "Headphones", "Smart Watch"],
        "Clothing": ["T-Shirt", "Jeans", "Jacket", "Dress", "Sneakers"],
        "Home & Garden": ["Lamp", "Sofa", "Garden Tool Set", "Rug", "Plant Pot"],
        "Sports": ["Yoga Mat", "Dumbbells", "Running Shoes", "Tennis Racket", "Bicycle"],
        "Books": ["Fiction Novel", "Textbook", "Cookbook", "Self-Help", "Biography"],
        "Food & Beverage": ["Coffee Beans", "Protein Bars", "Organic Tea", "Snack Box", "Juice Pack"],
        "Health & Beauty": ["Moisturizer", "Vitamin Pack", "Shampoo", "Sunscreen", "Perfume"],
        "Automotive": ["Car Wax", "Dash Cam", "Seat Cover", "Floor Mats", "Phone Mount"],
    }

    sales_reps = [fake.name() for _ in range(30)]

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days + 1

    dates = [start_date + timedelta(days=np.random.randint(0, total_days)) for _ in range(n)]
    dates.sort()

    region_list = np.random.choice(regions, n, p=[0.35, 0.25, 0.20, 0.12, 0.08])
    category_list = np.random.choice(categories, n, p=[0.20, 0.15, 0.13, 0.12, 0.10, 0.12, 0.10, 0.08])
    channel_list = np.random.choice(channels, n, p=[0.45, 0.35, 0.20])

    product_list = [np.random.choice(products[cat]) for cat in category_list]
    rep_list = np.random.choice(sales_reps, n)

    base_prices = {
        "Electronics": (150, 1200), "Clothing": (20, 200), "Home & Garden": (30, 500),
        "Sports": (25, 400), "Books": (10, 80), "Food & Beverage": (5, 60),
        "Health & Beauty": (10, 150), "Automotive": (15, 300),
    }

    units = np.zeros(n, dtype=int)
    prices = np.zeros(n)
    for i in range(n):
        low, high = base_prices[category_list[i]]
        prices[i] = round(np.random.uniform(low, high), 2)
        units[i] = max(1, int(np.random.lognormal(1.5, 0.8)))

    # Seasonality: boost Q4 (holiday season)
    for i, d in enumerate(dates):
        if d.month in [11, 12]:
            units[i] = int(units[i] * np.random.uniform(1.2, 1.8))
        elif d.month in [6, 7]:
            units[i] = int(units[i] * np.random.uniform(1.05, 1.3))

    # Trend: slight growth over years
    for i, d in enumerate(dates):
        year_factor = 1 + 0.05 * (d.year - 2023)
        units[i] = int(units[i] * year_factor)

    revenue = np.round(units * prices, 2)
    cost_ratio = np.random.uniform(0.4, 0.75, n)
    cost = np.round(revenue * cost_ratio, 2)
    profit = np.round(revenue - cost, 2)
    discount_pct = np.round(np.random.choice(
        [0, 0, 0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30], n,
        p=[0.35, 0.10, 0.10, 0.10, 0.10, 0.08, 0.07, 0.05, 0.05]
    ), 2)

    df = pd.DataFrame({
        "date": dates,
        "region": region_list,
        "product_category": category_list,
        "product": product_list,
        "units_sold": units,
        "unit_price": prices,
        "revenue": revenue,
        "cost": cost,
        "profit": profit,
        "discount_pct": discount_pct,
        "sales_channel": channel_list,
        "sales_rep": rep_list,
    })

    df.to_csv(os.path.join(DATA_DIR, "sales_data.csv"), index=False)
    print(f"  Sales data: {len(df)} rows")
    return df


def generate_marketing_data():
    """Generate 10K rows of marketing campaign data."""
    print("Generating marketing data...")
    n = 10000
    channels = ["Email", "Social", "Search", "Display", "Affiliate"]

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days + 1

    dates = [start_date + timedelta(days=np.random.randint(0, total_days)) for _ in range(n)]
    dates.sort()

    channel_list = np.random.choice(channels, n, p=[0.22, 0.25, 0.23, 0.18, 0.12])

    campaign_names = []
    for ch in channel_list:
        campaign_names.append(f"{ch}_{fake.bs().replace(' ', '_')[:20]}_{np.random.randint(100, 999)}")

    # Channel-specific performance patterns
    channel_params = {
        "Email": {"imp_range": (5000, 50000), "ctr": (0.02, 0.08), "conv": (0.03, 0.12), "cpm": (2, 8)},
        "Social": {"imp_range": (10000, 500000), "ctr": (0.005, 0.03), "conv": (0.01, 0.06), "cpm": (5, 15)},
        "Search": {"imp_range": (1000, 100000), "ctr": (0.03, 0.10), "conv": (0.02, 0.10), "cpm": (10, 40)},
        "Display": {"imp_range": (50000, 1000000), "ctr": (0.001, 0.01), "conv": (0.005, 0.03), "cpm": (1, 5)},
        "Affiliate": {"imp_range": (2000, 80000), "ctr": (0.01, 0.05), "conv": (0.02, 0.08), "cpm": (3, 12)},
    }

    records = []
    for i in range(n):
        ch = channel_list[i]
        params = channel_params[ch]
        impressions = np.random.randint(*params["imp_range"])
        ctr = np.random.uniform(*params["ctr"])
        clicks = int(impressions * ctr)
        conv_rate = np.random.uniform(*params["conv"])
        conversions = max(0, int(clicks * conv_rate))
        cpm = np.random.uniform(*params["cpm"])
        spend = round(impressions / 1000 * cpm, 2)
        avg_rev_per_conv = np.random.uniform(30, 200)
        revenue_attributed = round(conversions * avg_rev_per_conv, 2)
        leads = max(0, int(conversions * np.random.uniform(0.5, 2.0)))
        actual_ctr = round(clicks / impressions, 6) if impressions > 0 else 0
        actual_conv = round(conversions / clicks, 6) if clicks > 0 else 0
        cpa = round(spend / conversions, 2) if conversions > 0 else 0
        roas = round(revenue_attributed / spend, 4) if spend > 0 else 0

        records.append({
            "campaign_id": f"CMP-{i+1:05d}",
            "date": dates[i],
            "channel": ch,
            "campaign_name": campaign_names[i],
            "impressions": impressions,
            "clicks": clicks,
            "conversions": conversions,
            "spend": spend,
            "revenue_attributed": revenue_attributed,
            "leads_generated": leads,
            "ctr": actual_ctr,
            "conversion_rate": actual_conv,
            "cpa": cpa,
            "roas": roas,
        })

    df = pd.DataFrame(records)
    df.to_csv(os.path.join(DATA_DIR, "marketing_data.csv"), index=False)
    print(f"  Marketing data: {len(df)} rows")
    return df


def generate_customer_data():
    """Generate 20K rows of customer data."""
    print("Generating customer data...")
    n = 20000
    regions = ["North America", "Europe", "Asia Pacific", "Latin America", "Middle East"]
    segments = ["Enterprise", "SMB", "Consumer"]
    acq_channels = ["Organic", "Paid Search", "Social Media", "Referral", "Direct", "Email"]

    start_date = datetime(2020, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days + 1

    signup_dates = [start_date + timedelta(days=np.random.randint(0, total_days)) for _ in range(n)]
    region_list = np.random.choice(regions, n, p=[0.35, 0.25, 0.20, 0.12, 0.08])
    segment_list = np.random.choice(segments, n, p=[0.15, 0.35, 0.50])
    acq_list = np.random.choice(acq_channels, n, p=[0.20, 0.18, 0.22, 0.15, 0.13, 0.12])

    # Segment-specific CLV patterns
    clv_params = {"Enterprise": (2000, 15000), "SMB": (500, 5000), "Consumer": (50, 2000)}
    order_params = {"Enterprise": (10, 100), "SMB": (5, 50), "Consumer": (1, 25)}

    records = []
    for i in range(n):
        seg = segment_list[i]
        clv_low, clv_high = clv_params[seg]
        lifetime_value = round(np.random.lognormal(np.log((clv_low + clv_high) / 2), 0.6), 2)
        lifetime_value = max(clv_low * 0.5, min(lifetime_value, clv_high * 2))

        ord_low, ord_high = order_params[seg]
        total_orders = max(1, int(np.random.lognormal(np.log((ord_low + ord_high) / 2), 0.5)))
        total_orders = min(total_orders, ord_high * 2)
        avg_order_value = round(lifetime_value / total_orders, 2)

        days_since_signup = (end_date - signup_dates[i]).days
        last_purchase_offset = np.random.randint(0, max(1, days_since_signup))
        last_purchase_date = signup_dates[i] + timedelta(days=last_purchase_offset)

        days_since_purchase = (end_date - last_purchase_date).days
        churn_prob = min(0.8, days_since_purchase / 365 * 0.5)
        churn_flag = int(np.random.random() < churn_prob)

        satisfaction = max(1, min(10, int(np.random.normal(7 if not churn_flag else 4.5, 1.5))))
        nps = max(0, min(10, int(np.random.normal(7.5 if not churn_flag else 4, 2))))
        tickets = max(0, int(np.random.exponential(3 if churn_flag else 1.5)))

        records.append({
            "customer_id": f"CUST-{i+1:06d}",
            "signup_date": signup_dates[i],
            "region": region_list[i],
            "segment": seg,
            "lifetime_value": lifetime_value,
            "total_orders": total_orders,
            "avg_order_value": avg_order_value,
            "last_purchase_date": last_purchase_date,
            "churn_flag": churn_flag,
            "satisfaction_score": satisfaction,
            "nps_score": nps,
            "support_tickets": tickets,
            "acquisition_channel": acq_list[i],
        })

    df = pd.DataFrame(records)
    df.to_csv(os.path.join(DATA_DIR, "customer_data.csv"), index=False)
    print(f"  Customer data: {len(df)} rows")
    return df


def generate_supply_chain_data():
    """Generate 30K rows of supply chain data."""
    print("Generating supply chain data...")
    n = 30000
    suppliers = [f"Supplier_{chr(65 + i // 2)}{i+1}" for i in range(20)]
    warehouses = ["Warehouse_East", "Warehouse_West", "Warehouse_Central",
                  "Warehouse_South", "Warehouse_North"]
    categories = ["Electronics", "Clothing", "Home & Garden", "Sports", "Books",
                  "Food & Beverage", "Health & Beauty", "Automotive"]

    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days + 1

    order_dates = sorted([start_date + timedelta(days=np.random.randint(0, total_days)) for _ in range(n)])

    supplier_quality = {s: np.random.uniform(0.7, 0.98) for s in suppliers}
    supplier_lead = {s: np.random.uniform(2, 15) for s in suppliers}

    records = []
    for i in range(n):
        supplier = np.random.choice(suppliers)
        warehouse = np.random.choice(warehouses)
        category = np.random.choice(categories)

        base_lead = supplier_lead[supplier]
        lead_time = max(1, int(np.random.normal(base_lead, base_lead * 0.3)))
        ship_date = order_dates[i] + timedelta(days=max(1, int(lead_time * 0.3)))
        delivery_date = order_dates[i] + timedelta(days=lead_time)

        quality = supplier_quality[supplier]
        on_time = int(np.random.random() < quality)
        if not on_time:
            delivery_date += timedelta(days=np.random.randint(1, 7))

        quantity = max(1, int(np.random.lognormal(3, 0.8)))
        unit_cost = round(np.random.uniform(5, 200), 2)
        shipping_cost = round(quantity * np.random.uniform(0.5, 5) + np.random.uniform(5, 30), 2)

        defect_base = 1 - quality
        defect_rate = round(max(0, np.random.normal(defect_base * 0.1, 0.02)), 4)

        inventory_level = max(0, int(np.random.normal(500, 200)))
        reorder_point = int(np.random.uniform(100, 400))
        stockout_flag = int(inventory_level < reorder_point * 0.5)

        records.append({
            "order_id": f"ORD-{i+1:06d}",
            "order_date": order_dates[i],
            "ship_date": ship_date,
            "delivery_date": delivery_date,
            "supplier": supplier,
            "warehouse": warehouse,
            "product_category": category,
            "quantity": quantity,
            "unit_cost": unit_cost,
            "shipping_cost": shipping_cost,
            "lead_time_days": lead_time,
            "on_time_delivery": on_time,
            "defect_rate": defect_rate,
            "inventory_level": inventory_level,
            "reorder_point": reorder_point,
            "stockout_flag": stockout_flag,
        })

    df = pd.DataFrame(records)
    df.to_csv(os.path.join(DATA_DIR, "supply_chain_data.csv"), index=False)
    print(f"  Supply chain data: {len(df)} rows")
    return df


def generate_finance_data():
    """Generate 36 rows of monthly financial data (3 years)."""
    print("Generating finance data...")
    months = pd.date_range("2023-01-01", periods=36, freq="MS")

    base_revenue = 5_000_000
    records = []
    for i, month in enumerate(months):
        # Revenue with growth trend + seasonality
        growth = 1 + 0.015 * i  # ~1.5% monthly growth
        seasonality = 1 + 0.1 * np.sin(2 * np.pi * (month.month - 1) / 12)
        noise = np.random.normal(1, 0.03)
        revenue = round(base_revenue * growth * seasonality * noise, 2)

        cogs = round(revenue * np.random.uniform(0.40, 0.50), 2)
        gross_profit = round(revenue - cogs, 2)
        opex = round(revenue * np.random.uniform(0.25, 0.35), 2)
        ebitda = round(gross_profit - opex, 2)
        net_income = round(ebitda * np.random.uniform(0.55, 0.75), 2)
        cash_flow = round(net_income * np.random.uniform(0.8, 1.3), 2)

        ar = round(revenue * np.random.uniform(0.08, 0.15), 2)
        ap = round(cogs * np.random.uniform(0.10, 0.18), 2)
        inventory_value = round(cogs * np.random.uniform(0.15, 0.25), 2)
        debt_ratio = round(np.random.uniform(0.25, 0.45), 4)
        current_ratio = round(np.random.uniform(1.2, 2.5), 4)
        roe = round(net_income / (revenue * 0.4) * np.random.uniform(0.9, 1.1), 4)

        if i >= 12:
            prev_rev = records[i - 12]["revenue"]
            yoy_growth = round((revenue - prev_rev) / abs(prev_rev), 4)
        else:
            yoy_growth = None

        records.append({
            "month": month.strftime("%Y-%m-%d"),
            "revenue": revenue,
            "cogs": cogs,
            "gross_profit": gross_profit,
            "operating_expenses": opex,
            "ebitda": ebitda,
            "net_income": net_income,
            "cash_flow": cash_flow,
            "accounts_receivable": ar,
            "accounts_payable": ap,
            "inventory_value": inventory_value,
            "debt_ratio": debt_ratio,
            "current_ratio": current_ratio,
            "return_on_equity": roe,
            "revenue_growth_yoy": yoy_growth,
        })

    df = pd.DataFrame(records)
    df.to_csv(os.path.join(DATA_DIR, "finance_data.csv"), index=False)
    print(f"  Finance data: {len(df)} rows")
    return df


def generate_hr_workforce_data():
    """Generate 5K rows of HR workforce data."""
    print("Generating HR workforce data...")
    n = 5000
    departments = ["Engineering", "Sales", "Marketing", "Finance",
                    "HR", "Operations", "Product", "Customer Support"]
    role_levels = ["Junior", "Mid", "Senior", "Lead", "Director"]
    locations = ["New York", "San Francisco", "London", "Berlin",
                 "Singapore", "Toronto", "Sydney", "Mumbai"]
    genders = ["Male", "Female", "Non-Binary"]

    salary_ranges = {
        "Junior": (45000, 75000), "Mid": (65000, 105000), "Senior": (90000, 145000),
        "Lead": (120000, 180000), "Director": (160000, 280000),
    }

    start_date = datetime(2018, 1, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days + 1

    records = []
    for i in range(n):
        dept = np.random.choice(departments, p=[0.22, 0.15, 0.10, 0.10, 0.08, 0.13, 0.12, 0.10])
        level = np.random.choice(role_levels, p=[0.30, 0.30, 0.22, 0.12, 0.06])
        location = np.random.choice(locations)
        gender = np.random.choice(genders, p=[0.48, 0.46, 0.06])

        hire_date = start_date + timedelta(days=np.random.randint(0, total_days))
        tenure_months = max(1, (end_date - hire_date).days // 30)

        low, high = salary_ranges[level]
        loc_factor = {"San Francisco": 1.15, "New York": 1.10, "London": 1.05,
                      "Sydney": 1.0, "Toronto": 0.95, "Berlin": 0.93,
                      "Singapore": 1.0, "Mumbai": 0.70}
        salary = round(np.random.uniform(low, high) * loc_factor.get(location, 1.0), 2)

        performance = max(1, min(5, round(np.random.normal(3.5, 0.8), 1)))
        engagement = max(1, min(10, round(np.random.normal(6.8, 1.5), 1)))

        attrition_base = 0.12
        if engagement < 4:
            attrition_base += 0.15
        if performance < 2.5:
            attrition_base += 0.1
        if tenure_months > 60:
            attrition_base -= 0.05
        attrition_flag = int(np.random.random() < attrition_base)

        age = max(22, min(65, int(np.random.normal(35, 8))))
        training_hours = max(0, int(np.random.exponential(20)))
        promotion_flag = int(np.random.random() < 0.08)
        overtime_hours = max(0, round(np.random.exponential(5), 1))

        records.append({
            "employee_id": f"EMP-{i+1:05d}",
            "hire_date": hire_date,
            "department": dept,
            "role_level": level,
            "location": location,
            "salary": salary,
            "performance_score": performance,
            "engagement_score": engagement,
            "tenure_months": tenure_months,
            "attrition_flag": attrition_flag,
            "gender": gender,
            "age": age,
            "training_hours": training_hours,
            "promotion_flag": promotion_flag,
            "overtime_hours": overtime_hours,
        })

    df = pd.DataFrame(records)
    df.to_csv(os.path.join(DATA_DIR, "hr_workforce_data.csv"), index=False)
    print(f"  HR workforce data: {len(df)} rows")
    return df


def generate_genai_usage_data():
    """Generate 15K rows of Gen AI usage data."""
    print("Generating Gen AI usage data...")
    n = 15000
    models = ["gpt-4", "gpt-3.5", "claude", "llama"]
    use_cases = ["code_gen", "summarization", "qa", "translation", "analysis"]
    departments = ["Engineering", "Sales", "Marketing", "Finance",
                    "HR", "Operations", "Product", "Customer Support"]

    start_date = datetime(2023, 6, 1)
    end_date = datetime(2025, 12, 31)
    total_days = (end_date - start_date).days + 1

    timestamps = sorted([
        start_date + timedelta(
            days=np.random.randint(0, total_days),
            hours=np.random.randint(6, 22),
            minutes=np.random.randint(0, 60),
        )
        for _ in range(n)
    ])

    model_params = {
        "gpt-4": {"tokens_in": (500, 4000), "tokens_out": (200, 3000), "latency": (800, 5000), "cost_per_1k": 0.03},
        "gpt-3.5": {"tokens_in": (200, 3000), "tokens_out": (100, 2000), "latency": (200, 1500), "cost_per_1k": 0.002},
        "claude": {"tokens_in": (500, 5000), "tokens_out": (200, 4000), "latency": (600, 4000), "cost_per_1k": 0.015},
        "llama": {"tokens_in": (300, 3000), "tokens_out": (100, 2000), "latency": (300, 2000), "cost_per_1k": 0.001},
    }

    # Increasing adoption over time
    records = []
    for i in range(n):
        days_elapsed = (timestamps[i] - start_date).days
        adoption_factor = min(1.0, 0.3 + 0.7 * (days_elapsed / total_days))

        model = np.random.choice(models, p=[0.30, 0.28, 0.25, 0.17])
        use_case = np.random.choice(use_cases, p=[0.25, 0.22, 0.20, 0.13, 0.20])

        # Weight departments by adoption over time
        dept_probs = np.array([0.30, 0.12, 0.15, 0.10, 0.05, 0.08, 0.12, 0.08])
        dept_probs = dept_probs / dept_probs.sum()
        dept = np.random.choice(departments, p=dept_probs)

        params = model_params[model]
        tokens_in = np.random.randint(*params["tokens_in"])
        tokens_out = np.random.randint(*params["tokens_out"])
        latency = max(50, int(np.random.lognormal(
            np.log((params["latency"][0] + params["latency"][1]) / 2), 0.4
        )))
        cost = round((tokens_in + tokens_out) / 1000 * params["cost_per_1k"], 4)

        satisfaction = max(1, min(5, int(np.random.normal(3.8, 0.9))))
        error_flag = int(np.random.random() < 0.03)
        hallucination_flag = int(np.random.random() < (0.08 if model == "llama" else 0.04 if model == "gpt-3.5" else 0.02))

        records.append({
            "request_id": f"REQ-{i+1:06d}",
            "timestamp": timestamps[i],
            "model": model,
            "use_case": use_case,
            "department": dept,
            "tokens_input": tokens_in,
            "tokens_output": tokens_out,
            "latency_ms": latency,
            "cost_usd": cost,
            "user_satisfaction": satisfaction,
            "error_flag": error_flag,
            "hallucination_detected": hallucination_flag,
        })

    df = pd.DataFrame(records)
    df.to_csv(os.path.join(DATA_DIR, "genai_usage_data.csv"), index=False)
    print(f"  Gen AI usage data: {len(df)} rows")
    return df


def generate_operations_kpi_data():
    """Generate ~1K rows of daily operations KPI data (3 years)."""
    print("Generating operations KPI data...")
    dates = pd.date_range("2023-01-01", "2025-12-31", freq="D")

    records = []
    for i, date in enumerate(dates):
        day_of_week = date.dayofweek
        is_weekend = day_of_week >= 5

        # Lower activity on weekends
        base_tickets = 50 if not is_weekend else 15
        tickets_created = max(0, int(np.random.normal(base_tickets, base_tickets * 0.3)))
        resolution_rate = np.random.uniform(0.85, 1.05)
        tickets_resolved = min(tickets_created + 5, max(0, int(tickets_created * resolution_rate)))

        avg_resolution = max(0.5, round(np.random.lognormal(1.5, 0.5), 2))
        sla_compliance = round(min(100, max(80, np.random.normal(95, 3))), 2)
        uptime = round(min(100, max(95, np.random.normal(99.5, 0.5))), 3)

        p1 = max(0, int(np.random.poisson(0.3 if not is_weekend else 0.1)))
        p2 = max(0, int(np.random.poisson(1.5 if not is_weekend else 0.5)))
        p3 = max(0, int(np.random.poisson(5 if not is_weekend else 2)))

        deployments = max(0, int(np.random.poisson(3 if not is_weekend else 0.5)))
        rollbacks = max(0, int(np.random.poisson(0.1 * deployments))) if deployments > 0 else 0

        impact_minutes = max(0, round(p1 * np.random.uniform(10, 60) + p2 * np.random.uniform(2, 15), 1))

        records.append({
            "date": date,
            "tickets_created": tickets_created,
            "tickets_resolved": tickets_resolved,
            "avg_resolution_time_hrs": avg_resolution,
            "sla_compliance_pct": sla_compliance,
            "system_uptime_pct": uptime,
            "incidents_p1": p1,
            "incidents_p2": p2,
            "incidents_p3": p3,
            "deployment_count": deployments,
            "rollback_count": rollbacks,
            "customer_impact_minutes": impact_minutes,
        })

    df = pd.DataFrame(records)
    df.to_csv(os.path.join(DATA_DIR, "operations_kpi_data.csv"), index=False)
    print(f"  Operations KPI data: {len(df)} rows")
    return df


def main():
    """Generate all datasets."""
    print("=" * 60)
    print("Enterprise BI Dashboard Suite — Data Generation")
    print("=" * 60)

    ensure_dirs()

    generate_sales_data()
    generate_marketing_data()
    generate_customer_data()
    generate_supply_chain_data()
    generate_finance_data()
    generate_hr_workforce_data()
    generate_genai_usage_data()
    generate_operations_kpi_data()

    print("\n" + "=" * 60)
    print("All datasets generated successfully!")
    print(f"Output directory: {DATA_DIR}")
    print("=" * 60)


if __name__ == "__main__":
    main()
