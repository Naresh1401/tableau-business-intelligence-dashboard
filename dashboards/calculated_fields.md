# Tableau Calculated Fields Reference

Complete list of calculated fields used across the Enterprise BI Dashboard Suite.

---

## Financial Metrics

### Profit Margin
```
[Profit] / [Revenue]
```

### Gross Profit Margin
```
([Revenue] - [COGS]) / [Revenue]
```

### Operating Margin
```
[EBITDA] / [Revenue]
```

### Net Margin
```
[Net Income] / [Revenue]
```

### YoY Revenue Growth
```
(ZN([Revenue]) - LOOKUP(ZN([Revenue]), -12)) / ABS(LOOKUP(ZN([Revenue]), -12))
```

### MoM Revenue Growth
```
(ZN([Revenue]) - LOOKUP(ZN([Revenue]), -1)) / ABS(LOOKUP(ZN([Revenue]), -1))
```

### Revenue Growth Rate (Table Calc)
```
(ZN(SUM([Revenue])) - LOOKUP(ZN(SUM([Revenue])), -1)) / ABS(LOOKUP(ZN(SUM([Revenue])), -1))
```

### Current Ratio
```
[Current Assets] / [Current Liabilities]
```

### Debt-to-Equity Ratio
```
[Total Debt] / [Total Equity]
```

### Return on Equity
```
[Net Income] / [Total Equity]
```

### Cumulative Cash Flow
```
RUNNING_SUM(SUM([Cash Flow]))
```

### Budget Variance %
```
(SUM([Actual]) - SUM([Budget])) / ABS(SUM([Budget]))
```

---

## Sales Metrics

### Revenue per Unit
```
SUM([Revenue]) / SUM([Units Sold])
```

### Avg Deal Size
```
SUM([Revenue]) / COUNTD([Order ID])
```

### Discount Impact on Profit
```
IF [Discount Pct] > 0.2 THEN "High Discount"
ELSEIF [Discount Pct] > 0.1 THEN "Medium Discount"
ELSEIF [Discount Pct] > 0 THEN "Low Discount"
ELSE "No Discount"
END
```

### Running Total Revenue
```
RUNNING_SUM(SUM([Revenue]))
```

### Moving Average Revenue (3-Month)
```
WINDOW_AVG(SUM([Revenue]), -2, 0)
```

### Sales Rep Rank
```
RANK(SUM([Revenue]))
```

### Channel Mix %
```
SUM([Revenue]) / TOTAL(SUM([Revenue]))
```

---

## Customer Metrics

### Customer Segment (by CLV)
```
IF [Lifetime Value] > 5000 THEN "Platinum"
ELSEIF [Lifetime Value] > 2000 THEN "Gold"
ELSEIF [Lifetime Value] > 500 THEN "Silver"
ELSE "Bronze"
END
```

### Churn Risk Score
```
IF [Days Since Last Purchase] > 365 THEN 5
ELSEIF [Days Since Last Purchase] > 180 THEN 4
ELSEIF [Days Since Last Purchase] > 90 THEN 3
ELSEIF [Days Since Last Purchase] > 30 THEN 2
ELSE 1
END
```

### Days Since Last Purchase
```
DATEDIFF('day', [Last Purchase Date], TODAY())
```

### NPS Category
```
IF [NPS Score] >= 9 THEN "Promoter"
ELSEIF [NPS Score] >= 7 THEN "Passive"
ELSE "Detractor"
END
```

### NPS Score (Calculated)
```
(COUNTD(IF [NPS Score] >= 9 THEN [Customer ID] END) -
 COUNTD(IF [NPS Score] <= 6 THEN [Customer ID] END))
/ COUNTD([Customer ID]) * 100
```

### Customer Tenure (Months)
```
DATEDIFF('month', [Signup Date], TODAY())
```

### RFM Recency Score
```
IF DATEDIFF('day', [Last Purchase Date], TODAY()) <= 30 THEN 5
ELSEIF DATEDIFF('day', [Last Purchase Date], TODAY()) <= 90 THEN 4
ELSEIF DATEDIFF('day', [Last Purchase Date], TODAY()) <= 180 THEN 3
ELSEIF DATEDIFF('day', [Last Purchase Date], TODAY()) <= 365 THEN 2
ELSE 1
END
```

### RFM Frequency Score
```
IF [Total Orders] >= 20 THEN 5
ELSEIF [Total Orders] >= 10 THEN 4
ELSEIF [Total Orders] >= 5 THEN 3
ELSEIF [Total Orders] >= 2 THEN 2
ELSE 1
END
```

### RFM Monetary Score
```
IF [Lifetime Value] >= 5000 THEN 5
ELSEIF [Lifetime Value] >= 2000 THEN 4
ELSEIF [Lifetime Value] >= 500 THEN 3
ELSEIF [Lifetime Value] >= 100 THEN 2
ELSE 1
END
```

### Cohort Month
```
DATETRUNC('month', [Signup Date])
```

### Cohort Retention Period
```
DATEDIFF('month', DATETRUNC('month', [Signup Date]), DATETRUNC('month', [Last Purchase Date]))
```

---

## Marketing Metrics

### ROAS (Return on Ad Spend)
```
SUM([Revenue Attributed]) / SUM([Spend])
```

### CTR (Click-Through Rate)
```
SUM([Clicks]) / SUM([Impressions])
```

### Conversion Rate
```
SUM([Conversions]) / SUM([Clicks])
```

### CPA (Cost per Acquisition)
```
SUM([Spend]) / SUM([Conversions])
```

### Cost per Click
```
SUM([Spend]) / SUM([Clicks])
```

### Cost per Lead
```
SUM([Spend]) / SUM([Leads Generated])
```

### Budget Utilization %
```
SUM([Spend]) / SUM([Budget Allocated])
```

### Efficiency Score
```
(SUM([Revenue Attributed]) / SUM([Spend])) * (SUM([Conversions]) / SUM([Clicks]))
```

### Channel Rank by ROAS
```
RANK(SUM([Revenue Attributed]) / SUM([Spend]))
```

---

## Supply Chain Metrics

### On-Time Delivery Rate
```
SUM([On Time Delivery]) / COUNT([Order ID])
```

### Lead Time Category
```
IF [Lead Time Days] <= 3 THEN "Express"
ELSEIF [Lead Time Days] <= 7 THEN "Standard"
ELSEIF [Lead Time Days] <= 14 THEN "Extended"
ELSE "Delayed"
END
```

### Supplier Score (Composite)
```
([On-Time Delivery Rate] * 0.4) +
((1 - [Defect Rate]) * 0.3) +
(1 / [Avg Lead Time Days] * 10 * 0.3)
```

### Inventory Days on Hand
```
[Inventory Level] / ([Quantity] / 30)
```

### Stockout Risk Flag
```
IF [Inventory Level] <= [Reorder Point] THEN "At Risk"
ELSEIF [Inventory Level] <= [Reorder Point] * 1.2 THEN "Warning"
ELSE "OK"
END
```

### Defect Cumulative %
```
RUNNING_SUM(SUM([Defect Count])) / TOTAL(SUM([Defect Count]))
```

### Shipping Cost per Unit
```
SUM([Shipping Cost]) / SUM([Quantity])
```

---

## HR & Workforce Metrics

### Attrition Rate
```
SUM([Attrition Flag]) / COUNT([Employee ID])
```

### Revenue per Employee
```
SUM([Company Revenue]) / COUNTD([Employee ID])
```

### Compensation Ratio
```
[Salary] / WINDOW_AVG(AVG([Salary]), 0, 0)
```

### Pay Equity Index
```
{ FIXED [Gender], [Role Level] : AVG([Salary]) }
/ { FIXED [Role Level] : AVG([Salary]) }
```

### Engagement Category
```
IF [Engagement Score] >= 8 THEN "Highly Engaged"
ELSEIF [Engagement Score] >= 6 THEN "Engaged"
ELSEIF [Engagement Score] >= 4 THEN "Neutral"
ELSE "Disengaged"
END
```

### Performance Band
```
IF [Performance Score] >= 4.5 THEN "Exceptional"
ELSEIF [Performance Score] >= 3.5 THEN "Exceeds Expectations"
ELSEIF [Performance Score] >= 2.5 THEN "Meets Expectations"
ELSEIF [Performance Score] >= 1.5 THEN "Needs Improvement"
ELSE "Underperforming"
END
```

### Training ROI
```
([Performance Score After Training] - [Performance Score Before Training])
/ [Training Cost]
```

### Promotion Rate
```
SUM([Promotion Flag]) / COUNT([Employee ID])
```

### Overtime Utilization
```
SUM([Overtime Hours]) / SUM([Standard Hours])
```

### Tenure Band
```
IF [Tenure Months] >= 60 THEN "5+ Years"
ELSEIF [Tenure Months] >= 36 THEN "3-5 Years"
ELSEIF [Tenure Months] >= 12 THEN "1-3 Years"
ELSE "< 1 Year"
END
```

---

## Gen AI Metrics

### Gen AI Cost per Request
```
SUM([Cost USD]) / COUNT([Request ID])
```

### Cost per 1K Tokens
```
SUM([Cost USD]) / (SUM([Tokens Input]) + SUM([Tokens Output])) * 1000
```

### Latency P50
```
PERCENTILE([Latency Ms], 0.50)
```

### Latency P95
```
PERCENTILE([Latency Ms], 0.95)
```

### Latency P99
```
PERCENTILE([Latency Ms], 0.99)
```

### Hallucination Rate
```
SUM([Hallucination Detected]) / COUNT([Request ID])
```

### Hallucination Rate (7-Day Rolling)
```
WINDOW_SUM(SUM([Hallucination Detected]), -6, 0)
/ WINDOW_SUM(COUNT([Request ID]), -6, 0)
```

### Avg User Satisfaction
```
AVG([User Satisfaction])
```

### Error Rate
```
SUM([Error Flag]) / COUNT([Request ID])
```

### Department Adoption Rate
```
COUNTD([User ID]) / { FIXED [Department] : COUNTD([Total Users]) }
```

### Model Efficiency Score
```
(AVG([User Satisfaction]) / 5)
* (1 - SUM([Error Flag]) / COUNT([Request ID]))
* (1000 / AVG([Latency Ms]))
```

### Total Token Usage
```
SUM([Tokens Input]) + SUM([Tokens Output])
```

### Token Efficiency Ratio
```
SUM([Tokens Output]) / SUM([Tokens Input])
```
