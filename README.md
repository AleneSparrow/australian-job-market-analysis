# Australian IT Labour Market Intelligence Platform

An end-to-end data analytics project exploring the Australian IT job market using real job advertisements from multiple sources.

Instead of relying on salary reports or aggregated statistics, this project works directly with vacancy data. The goal is to build a reproducible analytics pipeline that transforms raw job postings into a structured database suitable for SQL analysis and interactive dashboards.

Current dataset: **105,337 Australian job advertisements**

---

# Why I built this project

Most labour market reports tell you what has already happened.

I wanted to work with the underlying data instead.

That meant collecting vacancies from different sources, cleaning completely different datasets, standardising their structure and building a single database that can answer practical questions about Australia's IT labour market.

Rather than analysing one dataset in isolation, the project combines multiple sources into one analytical model that can be extended over time.

---

# Questions I'm trying to answer

Using the current dataset, the project explores questions such as:

- Which IT roles are currently the most in demand?
- Which technical skills appear most frequently?
- Which skills are commonly requested together?
- Which Australian cities and states have the highest hiring activity?
- How common are remote, hybrid and on-site roles?
- Which employers advertise the largest number of IT vacancies?
- How do salary ranges differ across occupations and locations?

As additional government datasets are integrated, the analysis will also compare employer demand with long-term labour market forecasts.

---

# Current Dataset

The unified database currently contains:

- **105,337** job advertisements
- Multiple Australian job data sources
- Standardised occupation and location fields
- Cleaned salary information
- Employer information
- Vacancy descriptions
- Employment types

The project is focused exclusively on the Australian IT labour market.

---

# Project Pipeline

```
Job APIs
     │
     ▼
Raw datasets
     │
     ▼
Data cleaning
     │
     ▼
Standardisation
     │
     ▼
Feature engineering
     │
     ▼
PostgreSQL
     │
     ▼
SQL analysis
     │
     ▼
Tableau dashboards
```

---

# Feature Engineering

The project automatically extracts additional information from vacancy titles and descriptions.

Current engineered features include:

- technical skills
- programming languages
- cloud platforms
- BI tools
- experience level
- employment type
- visa sponsorship
- education requirements
- remote / hybrid / onsite classification

Feature engineering results are stored separately from the original dataset, making the pipeline reproducible.

---

# Data Quality

Before starting the analysis, every build is validated using SQL quality checks.

Completed checks include:

- duplicate job IDs
- missing job IDs
- row count validation
- feature table consistency
- remote work classification
- experience level extraction
- skill extraction validation

---

# Technology

The project is built with:

- Python
- PostgreSQL
- SQL
- Pandas
- Tableau
- Git

---

# Repository Structure

```
data/
│
├── raw/
├── processed/
│
src/
│
├── ingestion/
├── preprocessing/
├── feature_engineering/
├── quality_checks/
│
sql/
│
tableau/
│
README.md
```

---

# Project Status

Completed

- ✔ Data collection
- ✔ Database design
- ✔ Data cleaning
- ✔ Data integration
- ✔ Feature engineering
- ✔ Data quality validation

Current stage

- 🚧 Exploratory Data Analysis (EDA)

Next

- Tableau dashboards
- Business insights
- Final documentation

---

# Design Decisions

A few implementation choices were made intentionally.

- Raw datasets are never modified.
- Data cleaning and integration are performed primarily in SQL.
- Python is used for data collection and feature engineering.
- Engineered features are stored separately from the original vacancy data.
- The project focuses only on IT occupations to keep the analysis consistent.

---

# What's next

The next stage is exploratory analysis using SQL and Tableau to identify patterns in demand, salaries, skills and geography across the Australian IT labour market.

---

# Author

**Alena Vorobei**

Data Analytics Portfolio Project
