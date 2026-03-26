# Tableau Dashboard Design Specifications

This document provides detailed design specifications for each of the 8 Tableau dashboards in the Enterprise BI Dashboard Suite.

---

## Dashboard 1: Executive Overview

**Purpose:** Single-pane-of-glass view for C-suite executives with top-level KPIs and drill-down navigation.

### Layout
- **Size:** 1920 x 1080 (Fixed)
- **Background:** #F7F7F7
- **Header Bar:** Dark navy (#1B2A4A) with white text

### Components

| Component | Chart Type | Position | Data Source |
|-----------|-----------|----------|-------------|
| Revenue KPI Tile | Text + Sparkline | Top-left | finance_data.csv |
| Profit KPI Tile | Text + Sparkline | Top-center-left | finance_data.csv |
| Customer Count KPI Tile | Text + Sparkline | Top-center-right | customer_data.csv |
| NPS Score KPI Tile | Text + Gauge | Top-right | customer_data.csv |
| Revenue Trend (12mo) | Line Chart | Middle-left | finance_data.csv |
| Revenue by Region | Filled Map | Middle-right | sales_data.csv |
| Top Products | Horizontal Bar | Bottom-left | sales_data.csv |
| Department Spend | Donut Chart | Bottom-right | finance_data.csv |

### Dimensions
- Date (Month/Quarter/Year)
- Region
- Product Category
- Department

### Measures
- Revenue, Profit, Customer Count, NPS Score
- YoY Growth %, MoM Growth %
- Operating Cash Flow

### Filters
- Date Range (relative filter — last 12 months default)
- Region (multi-select)
- Product Category (multi-select)

### Color Scheme
- Primary: #1B2A4A (navy), #2E86AB (teal)
- Positive: #28A745, Negative: #DC3545
- Neutral: #6C757D

### Interactivity
- KPI tiles act as filter actions to other sheets
- Sparklines show 12-month trend
- Map supports lasso selection
- All components linked via dashboard actions

### Calculated Fields Used
- YoY Revenue Growth
- Profit Margin %
- Customer Growth Rate
- NPS Category (Promoter/Passive/Detractor)

---

## Dashboard 2: Sales Performance

**Purpose:** Deep-dive into sales performance across regions, products, channels, and reps.

### Layout
- **Size:** 1920 x 1080 (Fixed)
- **Orientation:** 2x3 grid with filters panel on left

### Components

| Component | Chart Type | Position | Data Source |
|-----------|-----------|----------|-------------|
| Revenue by Region | Filled Map | Top-left | sales_data.csv |
| Product Mix | Treemap | Top-center | sales_data.csv |
| Channel Comparison | Grouped Bar | Top-right | sales_data.csv |
| Monthly Revenue Trend | Dual-axis Line | Middle (full width) | sales_data.csv |
| Sales Rep Leaderboard | Horizontal Bar | Bottom-left | sales_data.csv |
| Discount vs Profit Scatter | Scatter Plot | Bottom-right | sales_data.csv |

### Dimensions
- Date (Day/Week/Month/Quarter/Year)
- Region (North America, Europe, Asia Pacific, Latin America, Middle East)
- Product Category (8 categories)
- Sales Channel (Online/Retail/Wholesale)
- Sales Rep

### Measures
- Revenue, Units Sold, Profit, Cost
- Discount %, Profit Margin %
- Avg Deal Size, Revenue per Rep

### Filters
- Date Range, Region, Product Category, Sales Channel
- Top N Sales Reps (parameter)

### Color Scheme
- Region: diverging blue palette
- Channel: categorical (#2E86AB, #A23B72, #F18F01)
- Treemap: sequential green

### Interactivity
- Map click filters all other charts
- Treemap drill-down: Category → Product
- Leaderboard highlights rep's data across all charts
- Parameter control for Top N reps

### Calculated Fields Used
- Profit Margin, YoY Growth, Revenue per Unit
- Running Total Revenue, Moving Average (3-month)
- Rank by Revenue

---

## Dashboard 3: Marketing Analytics

**Purpose:** Multi-channel marketing performance analysis with ROI optimization insights.

### Layout
- **Size:** 1920 x 1080 (Fixed)
- **Orientation:** Header + 2x2 grid + filter bar

### Components

| Component | Chart Type | Position | Data Source |
|-----------|-----------|----------|-------------|
| Channel Performance Matrix | Highlight Table | Top-left | marketing_data.csv |
| Campaign Funnel | Funnel Chart | Top-right | marketing_data.csv |
| ROAS by Channel | Bar + Reference Line | Bottom-left | marketing_data.csv |
| Budget vs Results | Scatter Plot | Bottom-right | marketing_data.csv |

### Dimensions
- Date (Month/Quarter)
- Channel (Email, Social, Search, Display, Affiliate)
- Campaign Name

### Measures
- Impressions, Clicks, Conversions, Spend
- Revenue Attributed, Leads Generated
- CTR, Conversion Rate, CPA, ROAS

### Filters
- Date Range, Channel (multi-select), Campaign (search filter)

### Color Scheme
- Channel colors: Email (#4285F4), Social (#EA4335), Search (#FBBC05), Display (#34A853), Affiliate (#FF6D01)
- ROAS benchmark: red dashed line at 1.0

### Interactivity
- Highlight table uses color intensity for performance
- Funnel shows drop-off percentages
- Scatter supports quadrant analysis (high spend/high return vs low spend/low return)
- Tooltip shows campaign details

### Calculated Fields Used
- ROAS, CTR, Conversion Rate, CPA
- Budget Utilization %, Efficiency Score
- Channel Rank by ROAS

---

## Dashboard 4: Customer 360

**Purpose:** Comprehensive customer analytics with segmentation, churn, and lifetime value insights.

### Layout
- **Size:** 1920 x 1080 (Fixed)
- **Orientation:** Top KPIs + 2x2 grid + bottom cohort matrix

### Components

| Component | Chart Type | Position | Data Source |
|-----------|-----------|----------|-------------|
| Customer KPIs | KPI Tiles | Top row | customer_data.csv |
| RFM Segmentation | Scatter Plot | Middle-left | customer_data.csv |
| Churn Risk Heatmap | Heatmap | Middle-right | customer_data.csv |
| CLV Distribution | Histogram | Bottom-left | customer_data.csv |
| Cohort Retention | Matrix/Heatmap | Bottom-center | customer_data.csv |
| NPS Gauge | Gauge Chart | Bottom-right | customer_data.csv |

### Dimensions
- Customer Segment (Enterprise/SMB/Consumer)
- Region, Acquisition Channel
- Signup Cohort (Month/Quarter)

### Measures
- Lifetime Value, Total Orders, Avg Order Value
- Satisfaction Score, NPS Score
- Support Tickets, Churn Flag

### Filters
- Segment, Region, Acquisition Channel, Date Range

### Color Scheme
- RFM Segments: diverging red-yellow-green
- Churn Risk: sequential red (low to high risk)
- NPS: Green (Promoter), Yellow (Passive), Red (Detractor)

### Interactivity
- RFM scatter supports segment selection
- Heatmap click shows customer list
- Cohort matrix shows retention % with color intensity
- NPS gauge animates on filter change

### Calculated Fields Used
- RFM Score, Customer Segment, Churn Risk Score
- Days Since Last Purchase, Customer Tenure
- NPS Category, Cohort Month

---

## Dashboard 5: Supply Chain Operations

**Purpose:** End-to-end supply chain visibility with supplier performance, inventory, and delivery metrics.

### Layout
- **Size:** 1920 x 1080 (Fixed)
- **Orientation:** Scorecard top + 2x2 grid + Pareto bottom

### Components

| Component | Chart Type | Position | Data Source |
|-----------|-----------|----------|-------------|
| Supplier Scorecard | Highlight Table | Top (full width) | supply_chain_data.csv |
| Lead Time Distribution | Histogram | Middle-left | supply_chain_data.csv |
| Inventory vs Reorder | Dual-axis Line | Middle-right | supply_chain_data.csv |
| On-Time Delivery Map | Filled Map | Bottom-left | supply_chain_data.csv |
| Defect Rate Pareto | Combo (Bar+Line) | Bottom-right | supply_chain_data.csv |

### Dimensions
- Supplier (20 suppliers), Warehouse (5)
- Product Category, Order Date
- On-Time Delivery Flag

### Measures
- Quantity, Unit Cost, Shipping Cost
- Lead Time Days, Defect Rate
- Inventory Level, Reorder Point

### Filters
- Supplier, Warehouse, Product Category, Date Range

### Color Scheme
- Scorecard: Green/Yellow/Red performance tiers
- Lead time: sequential blue
- Defect: red-orange gradient

### Interactivity
- Scorecard row click filters supplier details
- Histogram bin selection filters orders
- Dual-axis shows inventory level vs reorder point with alert zones
- Pareto shows cumulative line for 80/20 analysis

### Calculated Fields Used
- Supplier Score, Lead Time Category
- Inventory Days on Hand, Stockout Risk
- Defect Cumulative %, On-Time Delivery Rate

---

## Dashboard 6: Financial Performance

**Purpose:** Financial analysis with P&L waterfall, ratio analysis, and forecasting.

### Layout
- **Size:** 1920 x 1080 (Fixed)
- **Orientation:** Waterfall top + gauges + trend + variance

### Components

| Component | Chart Type | Position | Data Source |
|-----------|-----------|----------|-------------|
| P&L Waterfall | Waterfall Chart | Top (full width) | finance_data.csv |
| Ratio Gauges | Gauge Charts (3) | Middle-left | finance_data.csv |
| Cash Flow Trend | Area Chart | Middle-right | finance_data.csv |
| Budget vs Actual | Bullet/Bar Chart | Bottom-left | finance_data.csv |
| Revenue Forecast | Line + CI Band | Bottom-right | finance_data.csv |

### Dimensions
- Month, Quarter, Year
- Account Category (Revenue, COGS, OpEx, etc.)

### Measures
- Revenue, COGS, Gross Profit, Operating Expenses
- EBITDA, Net Income, Cash Flow
- Accounts Receivable/Payable, Inventory Value
- Debt Ratio, Current Ratio, ROE

### Filters
- Year, Quarter, Comparison Period

### Color Scheme
- Waterfall: Green (additions), Red (subtractions), Blue (totals)
- Gauges: Red/Yellow/Green zones
- Forecast: Blue line with light blue confidence band

### Interactivity
- Waterfall segments clickable for drill-down
- Gauges show threshold alerts
- Forecast shows 3-month projection with parameters
- Budget variance shows absolute and percentage

### Calculated Fields Used
- Gross Profit Margin, Operating Margin, Net Margin
- Current Ratio, Quick Ratio, Debt-to-Equity
- Revenue Growth YoY, Forecast (linear regression)
- Budget Variance %, Cumulative Cash Flow

---

## Dashboard 7: HR & Workforce Analytics

**Purpose:** People analytics covering headcount, attrition, compensation, engagement, and diversity.

### Layout
- **Size:** 1920 x 1080 (Fixed)
- **Orientation:** KPIs + 3x2 grid

### Components

| Component | Chart Type | Position | Data Source |
|-----------|-----------|----------|-------------|
| Workforce KPIs | KPI Tiles | Top row | hr_workforce_data.csv |
| Headcount by Dept | Stacked Bar | Middle-left | hr_workforce_data.csv |
| Attrition Funnel | Funnel Chart | Middle-center | hr_workforce_data.csv |
| Compensation Box Plot | Box-and-Whisker | Middle-right | hr_workforce_data.csv |
| Engagement Heatmap | Heatmap | Bottom-left | hr_workforce_data.csv |
| Diversity Dashboard | Donut + Bar | Bottom-right | hr_workforce_data.csv |

### Dimensions
- Department (8), Role Level (5), Location
- Gender, Age Band, Hire Year

### Measures
- Salary, Performance Score, Engagement Score
- Tenure Months, Training Hours, Overtime Hours
- Attrition Flag, Promotion Flag

### Filters
- Department, Role Level, Location, Gender, Date Range

### Color Scheme
- Department: categorical palette (8 colors)
- Engagement: diverging red-green
- Diversity: accessible color palette
- Performance: sequential purple

### Interactivity
- Department click filters all charts
- Box plot shows salary outliers and medians
- Heatmap shows dept x level engagement
- Diversity charts support demographic drill-down

### Calculated Fields Used
- Attrition Rate, Avg Tenure, Revenue per Employee
- Compensation Ratio, Pay Equity Index
- Engagement Category, Performance Band
- Training ROI, Promotion Rate

---

## Dashboard 8: Gen AI Operations

**Purpose:** Monitor Gen AI usage, costs, quality, and adoption across the organization.

### Layout
- **Size:** 1920 x 1080 (Fixed)
- **Orientation:** KPIs + 2x2 grid + adoption panel

### Components

| Component | Chart Type | Position | Data Source |
|-----------|-----------|----------|-------------|
| Gen AI KPIs | KPI Tiles | Top row | genai_usage_data.csv |
| Model Usage Trends | Line Chart | Middle-left | genai_usage_data.csv |
| Cost Breakdown | Stacked Area | Middle-right | genai_usage_data.csv |
| Latency Heatmap | Heatmap | Bottom-left | genai_usage_data.csv |
| Hallucination Tracker | Line + Alert | Bottom-center | genai_usage_data.csv |
| Dept Adoption | Bubble Chart | Bottom-right | genai_usage_data.csv |

### Dimensions
- Model (gpt-4, gpt-3.5, claude, llama)
- Use Case (code_gen, summarization, qa, translation, analysis)
- Department, Date (daily/weekly/monthly)

### Measures
- Tokens Input/Output, Latency (ms)
- Cost (USD), User Satisfaction
- Error Flag, Hallucination Detected
- Request Count

### Filters
- Model, Use Case, Department, Date Range

### Color Scheme
- Models: GPT-4 (#10A37F), GPT-3.5 (#74AA9C), Claude (#D4A574), LLaMA (#7C3AED)
- Cost: sequential orange
- Latency: diverging blue-red
- Hallucination: red alert on threshold breach

### Interactivity
- Model trend lines with toggle on/off
- Cost area shows cumulative and per-request views
- Heatmap shows model × use case latency matrix
- Bubble size = request volume, color = satisfaction
- Hallucination tracker shows 7-day rolling average with alert threshold

### Calculated Fields Used
- Cost per Request, Cost per 1K Tokens
- Latency P50/P95/P99, Avg Satisfaction
- Hallucination Rate (7-day rolling)
- Department Adoption Rate, Total Token Usage
- Error Rate, Model Efficiency Score

---

## General Design Guidelines

### Typography
- **Title Font:** Tableau Bold, 18pt
- **Subtitle:** Tableau Book, 12pt, #6C757D
- **Body:** Tableau Book, 10pt
- **KPI Values:** Tableau Bold, 36pt

### Color Accessibility
- All palettes tested for colorblind accessibility (deuteranopia, protanopia)
- Minimum contrast ratio 4.5:1 for text
- Use shapes and patterns as secondary visual encodings

### Performance Optimization
- Use extracts (.hyper) for datasets > 10K rows
- Implement context filters before dimension filters
- Limit marks to <10K per view
- Use FIXED LOD calculations sparingly

### Dashboard Actions
- **Filter Actions:** Source Sheet → Target Sheet(s)
- **Highlight Actions:** On hover for related data
- **URL Actions:** Link to detail views or external systems
- **Parameter Actions:** Dynamic Top N, date range controls
