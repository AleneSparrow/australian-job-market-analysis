# Australian IT Labour Market Intelligence Platform

> An end-to-end data analytics platform for exploring Australia's IT labour market through real-world job vacancies, government statistics, and labour market intelligence.

---

# Mission

Australia's IT labour market is constantly evolving.

New technologies emerge every year, employer requirements change rapidly, and demand for technical skills varies across occupations and regions. At the same time, labour market information is fragmented across multiple commercial platforms and government publications.

The mission of this project is to integrate these independent data sources into a single analytical platform that provides reliable, data-driven insights into Australia's IT labour market.

Rather than building another dashboard, this project aims to create a reproducible labour market intelligence system capable of supporting informed career, education and workforce decisions.

---

# Why This Project?

Most publicly available job market dashboards answer only one question:

> **"What is happening?"**

This project goes further by answering:

- Why is it happening?
- Which technologies are becoming more valuable?
- Which occupations are growing?
- Which skills command higher salaries?
- Where are employers hiring?
- How does current hiring compare with long-term government forecasts?

The project combines multiple independent data sources into a unified analytical environment that supports exploratory, descriptive and strategic labour market analysis.

---

# Research Questions

The platform is designed to answer questions such as:

## Labour Market

- Which IT occupations are currently the most in demand?
- Which occupations are growing the fastest?
- Which employers hire the most IT professionals?
- Which industries generate the highest demand?

## Skills

- Which technical skills appear most frequently?
- Which technologies are becoming industry standards?
- Which skills commonly appear together?
- Which skills differentiate junior, mid-level and senior roles?

## Salaries

- What salary ranges are offered across occupations?
- Which technologies are associated with higher salaries?
- Which locations offer the highest compensation?

## Geography

- Which Australian states have the highest hiring activity?
- Which cities are emerging technology hubs?
- How does regional demand differ?

## Government Perspective

- How closely does real employer demand align with official Jobs and Skills Australia forecasts?
- Which occupations may experience future shortages?

---

# Data Sources

This project combines multiple independent datasets.

## Commercial Job Market

- Adzuna API

Provides:

- Job advertisements
- Salary information
- Job descriptions
- Employer information
- Locations
- Categories

---

## Government Job Market

### Workforce Australia API

Provides:

- Public job vacancies
- Occupation information
- Employment types
- Regional distribution
- Vacancy metadata

---

## Labour Market Intelligence

### Jobs and Skills Australia (JSA)

Provides:

- Occupation outlook
- Employment projections
- Education requirements
- Workforce statistics
- Official labour market forecasts

---

## Official Statistics

### Australian Bureau of Statistics (ABS)

Provides:

- Labour market indicators
- Employment statistics
- Vacancy trends
- Economic context

---

# Project Architecture

```
                Public Data Sources
                        │
        ┌───────────────┼────────────────┐
        │               │                │
     Adzuna      Workforce AU        JSA / ABS
        │               │                │
        └───────────────┼────────────────┘
                        │
                 Python ETL Pipeline
                        │
                 Raw Data Repository
                        │
                 Data Profiling
                        │
              Data Cleaning & Validation
                        │
             Feature Engineering
                        │
                 PostgreSQL Database
                        │
                 SQL Analytics Layer
                        │
              Tableau Interactive Dashboard
                        │
             Business Insights & Reporting
```

---

# Technology Stack

## Data Collection

- Python
- Requests
- JSON APIs

## Data Processing

- Pandas
- NumPy

## Database

- PostgreSQL
- SQL

## Data Visualization

- Tableau

## Development

- Git
- GitHub
- VS Code

---

# Repository Structure

```
.
├── data
│   ├── raw
│   ├── interim
│   └── processed
│
├── src
│   ├── ingestion
│   ├── preprocessing
│   ├── database
│   ├── analysis
│   └── utils
│
├── sql
│
├── notebooks
│
├── tableau
│
├── reports
│
├── docs
│
└── README.md
```

---

# Analytical Workflow

## Phase 1 — Data Collection

- Collect vacancy data
- Collect labour market statistics
- Preserve immutable raw datasets

---

## Phase 2 — Data Understanding

- Profile datasets
- Assess completeness
- Identify inconsistencies
- Detect duplicates
- Evaluate data quality

---

## Phase 3 — Data Preparation

- Clean datasets
- Standardise fields
- Merge sources
- Create derived variables

---

## Phase 4 — Database

- Build PostgreSQL schema
- Load curated datasets
- Create analytical views

---

## Phase 5 — Analysis

- Exploratory Data Analysis
- SQL analysis
- Labour market analysis
- Salary analysis
- Skills analysis
- Geographic analysis
- Employer analysis

---

## Phase 6 — Visualisation

Interactive Tableau dashboards including:

- Labour Market Overview
- Salary Explorer
- Skills Explorer
- Employer Analysis
- Geographic Dashboard
- Technology Trends
- Occupation Insights

---

## Expected Deliverables

- Automated ETL pipeline
- Integrated analytical database
- Data quality report
- SQL analytical scripts
- Interactive Tableau dashboard
- Business recommendations
- Reproducible analytics workflow

---

# Current Status

| Stage | Status |
|--------|--------|
| Project Planning | ✅ Complete |
| Data Collection | 🟡 In Progress |
| Data Profiling | ⏳ Pending |
| Data Cleaning | ⏳ Pending |
| PostgreSQL | ⏳ Pending |
| SQL Analysis | ⏳ Pending |
| Tableau Dashboard | ⏳ Pending |
| Final Report | ⏳ Pending |

---

# Future Improvements

Potential future extensions include:

- Time-series monitoring
- Salary prediction models
- Skill demand forecasting
- NLP analysis of job descriptions
- Interactive web application
- Automated scheduled data updates

---

# About

This project is being developed as a portfolio project to demonstrate an end-to-end data analytics workflow, including data engineering, SQL, exploratory analysis, business intelligence and data visualisation using real-world Australian labour market data.

---

# Author

**Alena Vorobei**

Data Analyst | SQL | Python | Tableau
