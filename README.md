# Enterprise Business Intelligence Dashboard Suite — Tableau

**Author:** Naresh Sampangi

Multi-domain BI dashboard suite built with Tableau covering 8+ business domains. Includes Python data pipelines, statistical analysis, and interactive Tableau dashboards for executive decision-making.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    ENTERPRISE BI DASHBOARD SUITE                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌──────────────┐    ┌──────────────┐    ┌───────────────────────┐  │
│  │  Data Layer   │───▶│ Analysis     │───▶│  Tableau Dashboards   │  │
│  │              │    │  Layer       │    │                       │  │
│  │ • Sales      │    │ • Stats     │    │ • Executive Overview  │  │
│  │ • Marketing  │    │ • ML        │    │ • Sales Performance   │  │
│  │ • Customer   │    │ • Forecasts │    │ • Marketing Analytics │  │
│  │ • Supply Ch. │    │ • RFM       │    │ • Customer 360        │  │
│  │ • Finance    │    │ • Scoring   │    │ • Supply Chain Ops    │  │
│  │ • HR         │    │ • Clustering│    │ • Financial Perf.     │  │
│  │ • Gen AI     │    │             │    │ • HR & Workforce      │  │
│  │ • Operations │    │             │    │ • Gen AI Operations   │  │
│  └──────┬───────┘    └──────┬───────┘    └───────────┬───────────┘  │
│         │                   │                        │              │
│         ▼                   ▼                        ▼              │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                     data/ (CSV Exports)                      │   │
│  │  raw CSVs ──▶ analysis summaries ──▶ tableau-ready exports   │   │
│  └──────────────────────────────────────────────────────────────┘   │
│                                                                     │
│  Tech: Python │ Tableau │ pandas │ numpy │ scipy │ scikit-learn     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Dashboard Screenshots

| Dashboard | Screenshot |
|-----------|-----------|
| Executive Overview | ![Executive Overview](screenshots/01_executive_overview.png) |
| Sales Performance | ![Sales Performance](screenshots/02_sales_performance.png) |
| Marketing Analytics | ![Marketing Analytics](screenshots/03_marketing_analytics.png) |
| Customer 360 | ![Customer 360](screenshots/04_customer_360.png) |
| Supply Chain Operations | ![Supply Chain](screenshots/05_supply_chain.png) |
| Financial Performance | ![Financial Performance](screenshots/06_financial_performance.png) |
| HR & Workforce Analytics | ![HR Analytics](screenshots/07_hr_workforce.png) |
| Gen AI Operations | ![Gen AI](screenshots/08_genai_operations.png) |

---

## Dashboards

### 1. Executive Overview
High-level KPI tiles showing Revenue, Profit, Active Customers, and NPS with sparklines and YoY comparisons. Provides a single-pane-of-glass view for C-suite executives with drill-down capability into each domain.

**Key Metrics:** Total Revenue, Gross Profit Margin, Customer Count, Net Promoter Score, YoY Growth %, Operating Cash Flow

### 2. Sales Performance
Geospatial revenue analysis with interactive map, product mix treemap, channel comparison bar charts, sales rep leaderboard, and monthly trend lines with seasonal decomposition.

**Key Metrics:** Revenue by Region, Units Sold, Avg Deal Size, Win Rate, Discount Impact, Channel Mix %

### 3. Marketing Analytics
Multi-channel performance matrix comparing spend, impressions, clicks, and conversions. Campaign funnel visualization, ROAS by channel with benchmark lines, and budget allocation optimization scatterplot.

**Key Metrics:** ROAS, CTR, CPA, Conversion Rate, Leads Generated, Marketing Qualified Leads

### 4. Customer 360
RFM segmentation 3D scatter plot, churn risk heatmap by segment and region, CLV distribution histogram, cohort retention matrix, and NPS gauge with trend line.

**Key Metrics:** Customer Lifetime Value, Churn Rate, NPS, Avg Order Value, Retention Rate, Support Ticket Volume

### 5. Supply Chain Operations
Supplier performance scorecard with composite scoring, lead time distribution histograms, inventory level vs reorder point line charts, on-time delivery geographic map, and defect rate Pareto chart.

**Key Metrics:** On-Time Delivery %, Lead Time Days, Defect Rate, Stockout Frequency, Inventory Turnover, Supplier Score

### 6. Financial Performance
P&L waterfall chart, financial ratio gauges (liquidity, profitability, efficiency), cash flow trend area chart, budget vs actual variance bar chart, and revenue forecast with confidence intervals.

**Key Metrics:** Revenue, EBITDA, Net Income, Cash Flow, Debt Ratio, Current Ratio, ROE

### 7. HR & Workforce Analytics
Department headcount org chart, attrition funnel by stage, compensation box plots by level and department, engagement score heatmap, and diversity dashboard with demographic breakdowns.

**Key Metrics:** Headcount, Attrition Rate, Avg Salary, Engagement Score, Performance Rating, Training Hours, Diversity %

### 8. Gen AI Operations
Model usage trend lines, cost breakdown stacked area chart, latency heatmap by model and use case, hallucination rate tracker with alerts, and department adoption bubble chart.

**Key Metrics:** API Calls, Token Usage, Cost/Request, Latency P50/P95/P99, Hallucination Rate, User Satisfaction, Dept Adoption %

---

## Project Structure

```
tableau-business-intelligence-dashboard/
├── README.md
├── requirements.txt
├── Makefile
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   └── generate_all_data.py
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── sales_analysis.py
│   │   ├── customer_analysis.py
│   │   ├── marketing_analysis.py
│   │   ├── financial_analysis.py
│   │   ├── supply_chain_analysis.py
│   │   ├── hr_analysis.py
│   │   └── genai_analysis.py
│   └── export_tableau_ready.py
├── dashboards/
│   ├── README.md
│   └── calculated_fields.md
├── data/
│   ├── analysis/
│   └── tableau_ready/
└── screenshots/
```

---

## Setup & Usage

### Prerequisites
- Python 3.9+
- Tableau Desktop or Tableau Public (for dashboard visualization)

### Quick Start

```bash
# Clone the repository
git clone https://github.com/nareshsampangi/tableau-business-intelligence-dashboard.git
cd tableau-business-intelligence-dashboard

# Install dependencies
make install

# Generate all synthetic datasets
make generate-data

# Run all analysis scripts
make analyze

# Export Tableau-ready datasets
make export-tableau

# Or run everything at once
make all
```

### Manual Execution

```bash
pip install -r requirements.txt
python -m src.data.generate_all_data
python -m src.analysis.sales_analysis
python -m src.analysis.customer_analysis
python -m src.analysis.marketing_analysis
python -m src.analysis.financial_analysis
python -m src.analysis.supply_chain_analysis
python -m src.analysis.hr_analysis
python -m src.analysis.genai_analysis
python -m src.export_tableau_ready
```

### Connecting to Tableau
1. Open Tableau Desktop or Tableau Public
2. Connect to `data/tableau_ready/` CSV files
3. Use `dashboards/README.md` for dashboard design specifications
4. Reference `dashboards/calculated_fields.md` for calculated field formulas

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| Data Generation | Python, Faker, NumPy |
| Data Processing | pandas, NumPy |
| Statistical Analysis | SciPy, scikit-learn |
| Visualization | Tableau Desktop / Public |
| Export Format | CSV (Tableau-optimized) |

---

## Author

**Naresh Sampangi**

---

## License

This project is for portfolio and demonstration purposes.
