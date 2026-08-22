# Global Superstore - Executive Power BI & Sales Analytics Suite

[![Power BI](https://img.shields.io/badge/Power_BI-Desktop-F2C811?logo=powerbi&logoColor=black&style=for-the-badge)](https://powerbi.microsoft.com/)
[![DAX](https://img.shields.io/badge/DAX-Measures_Library-0078D4?logo=microsoft&logoColor=white&style=for-the-badge)](DAX_Measures.dax)
[![PDF Report](https://img.shields.io/badge/Executive_Report-PDF-E11D48?logo=adobeacrobatreader&logoColor=white&style=for-the-badge)](Global_Sales_Executive_Report.pdf)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge)](LICENSE)

An enterprise-grade **Power BI Sales & Profitability Analytics Dashboard** and **Executive PDF Report** built on the **Global Superstore** dataset (51,290 transactions across 147 countries, 4 fiscal years, and $12.64M in gross sales).

---

## 📊 Executive Scorecard & Macro Results (2011 – 2014)

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                                    MACRO SCORECARD                                     │
├────────────────────────────────────────────────────────────────────────────────────────┤
│  Gross Revenue:         $12,642,501.91    │  Total Unique Orders:        25,035        │
│  Net Profit:            $1,467,457.29     │  Active Customer Base:       1,590         │
│  Net Profit Margin:     11.61%            │  Catalog Product Count:      10,292        │
│  Total Units Sold:      178,312 units     │  Total Shipping Cost:        $1,352,815.70 │
│  Average Order Value:   $504.99           │  Avg Order-to-Ship Cycle:    3.97 Days     │
│  Identified Profit Leak: $521,419.00      │  Tables Sub-Category Loss:   -$64,083.39   │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📄 Key Project Deliverables

### 1. 📊 Enterprise Power BI Report ([`Global_Sales_Analytics_Dashboard.pbix`](Global_Sales_Analytics_Dashboard.pbix))
- **Page 1: Executive Sales & Profit Overview**
  - KPI Cards: Total Sales, Net Profit, Total Quantity, and **Average Discount %** (fixing legacy invalid `Sum(Discount)`).
  - Sub-Category Profitability Line & Clustered Column Combo Chart.
  - Donut Chart: Market Revenue Share (APAC, EU, US, LATAM, EMEA, Africa, Canada).
  - Donut Chart: Shipping Cost by Ship Mode (Standard, Second, First, Same Day).
  - Clean Slicers for Fiscal Year, Market Hub, and Category.
- **Page 2: Geographic & Shipping Performance**
  - Sub-Category Units Sold Spectrum Bar Chart.
  - Country Average Shipping Cost & Lead Time Progression.
  - Sales by Market Hub Bar Chart.
  - Sales by Customer Segment (Consumer, Corporate, Home Office).
  - Sales by Ship Mode.

### 2. 📑 Publication-Grade Executive PDF Report ([`Global_Sales_Executive_Report.pdf`](Global_Sales_Executive_Report.pdf))
- 4-page high-resolution C-suite report with vector plots:
  - **Page 1:** Executive Scorecard, Monthly 4-Year Trend, and Macro YoY Table.
  - **Page 2:** Geographic Intelligence, Market Hub Rankings, and Country Deficit Breakdown.
  - **Page 3:** Profit Leak Diagnostic on the -$64k Tables loss and Discount % vs. Margin % Scatter Plot.
  - **Page 4:** Fulfillment Logistics Breakdown and 4 Strategic C-Suite Initiatives.

### 3. 📐 Enterprise DAX Measures Library ([`DAX_Measures.dax`](DAX_Measures.dax))
Complete suite of 25+ production DAX formulas including:
- **Core Financials:** `[Total Sales]`, `[Total Profit]`, `[Profit Margin %]`, `[Average Order Value (AOV)]`
- **Time Intelligence:** `[Sales PY]`, `[Sales YoY Growth %]`, `[Profit PY]`, `[Profit YoY Growth %]`, `[Sales YTD]`
- **Discount & Profit Leaks:** `[Average Discount %]`, `[Loss Making Orders Count]`, `[Total Profit Lost ($)]`
- **Dynamic Ranking:** `[Product Rank by Sales]`, `[Top 10 Products Filter]`, `[Pareto Cumulative Sales %]`

---

## 🔍 Critical Business Insights & Profit Leaks

### 1. Structural Deficit in "Tables" Sub-Category
Across 17 product sub-categories, **Tables is the sole loss-maker enterprise-wide**:
- **Gross Revenue:** $757,041.90 | **Units Sold:** 3,083
- **Net Profit:** **-$64,083.39** (Profit Margin: **-8.46%**)
- **Root Cause:** A heavy average discount rate of **29.07%** combined with high freight fulfillment costs for bulky furniture completely erodes unit margins.

### 2. Severe Margin Destruction from Emerging Market Discounting
Discretionary discounting policies in several international markets created catastrophic margin erosion:
- **Turkey (EMEA):** -$98,447 Profit on $108k sales (Avg discount: **60.0%** | Margin: **-90.73%**)
- **Nigeria (Africa):** -$80,751 Profit on $54k sales (Avg discount: **70.0%** | Margin: **-148.57%**)
- **Netherlands (EU):** -$41,070 Profit on $77k sales (Avg discount: **48.2%** | Margin: **-52.98%**)
- **Honduras (LATAM):** -$29,482 Profit on $90k sales (Avg discount: **40.7%** | Margin: **-32.71%**)

> **Actionable Impact:** Capping regional discounts at 15–20% will immediately recover over **+$220,000 in net profit** annually.

---

## 📈 Year-Over-Year Macro Growth (2011–2014)

| Fiscal Year | Gross Sales ($) | YoY Sales % | Net Profit ($) | YoY Profit % | Profit Margin % | Total Orders |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **2011** | $2,259,451 | — | $248,941 | — | 11.02% | 4,440 |
| **2012** | $2,677,439 | **+18.50%** | $307,415 | **+23.49%** | 11.48% | 5,343 |
| **2013** | $3,405,746 | **+27.20%** | $406,935 | **+32.37%** | 11.95% | 6,721 |
| **2014** | $4,299,866 | **+26.25%** | $504,166 | **+23.89%** | 11.73% | 8,531 |

---

## 📁 Clean Repository Structure

```text
├── Global Superstore - Orders.csv             # Raw transactional dataset (51,290 rows)
├── Global_Sales_Analytics_Dashboard.pbix      # Production Power BI Report file
├── Global_Sales_Executive_Report.pdf          # 4-page Executive PDF Report with charts & strategy
├── DAX_Measures.dax                           # Complete library of 25+ enterprise DAX measures
├── README.md                                  # Repository documentation & insights
└── .gitignore                                 # Standard git ignore rules
```

---

## 💡 Strategic Executive Recommendations

1. **Enforce Global Discount Guardrails:** Cap discretionary sales discounts at 15% to eliminate $220k+ in emerging market losses (Turkey, Nigeria, Netherlands).
2. **Re-engineer "Tables" Product Line:** Implement a 12% price adjustment, delist negative-margin SKUs, and apply a mandatory bulky freight surcharge.
3. **Target High-CLV B2B Corporate Clients:** Corporate & Home Office accounts demonstrate higher margin stability (11.5%–12.0%) and repeat purchasing.
4. **Logistics Optimization:** Migrate eligible low-priority shipments to Standard Class (5-day cycle) to reduce expedited carrier surcharges.

---

## 👤 Author & Contribution
- **Author:** Senior Business Intelligence & Commercial Strategy Specialist
- **Contact / GitHub:** [@Abhiram1213](https://github.com/Abhiram1213)
