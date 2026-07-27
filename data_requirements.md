# Data Requirements

## Purpose

This document defines the fields required for the Australian job market analysis project.

## Core Fields

| Field | Description | Example |
|---|---|---|
| job_id | Unique job vacancy identifier | 102345 |
| job_title | Original job title | Data Analyst |
| normalized_job_title | Standardized job title | Data Analyst |
| company | Employer name | Commonwealth Bank |
| location | Full job location | Sydney, NSW |
| city | City where the job is located | Sydney |
| state | Australian state or territory | NSW |
| industry | Employer industry | Banking |
| employment_type | Full-time, part-time, contract or casual | Full-time |
| work_arrangement | On-site, hybrid or remote | Hybrid |
| salary_min | Minimum annual salary | 80000 |
| salary_max | Maximum annual salary | 100000 |
| salary_period | Annual, monthly, daily or hourly | Annual |
| experience_level | Junior, mid-level or senior | Junior |
| job_description | Full vacancy description | Full text |
| skills | Skills extracted from the description | SQL, Python, Tableau |
| education | Required education level | Bachelor’s degree |
| posting_date | Date the vacancy was published | 2026-07-20 |
| source | Website or dataset source | SEEK |
| job_url | Link to the original vacancy | Vacancy URL |

## Important Skills to Track

- SQL
- Python
- Excel
- Tableau
- Power BI
- R
- Google Sheets
- AWS
- Azure
- Snowflake
- Databricks
- BigQuery
- Statistics
- Machine learning
- Data visualization
- ETL
- Data cleaning
- Communication
- Stakeholder management

## Data Quality Rules

1. Each vacancy should have a unique `job_id`.
2. Duplicate vacancies must be removed.
3. Job titles should be standardized.
4. Australian states should use consistent abbreviations.
5. Salary values should be numeric.
6. Missing values should be recorded as null, not as text such as "unknown".
7. Raw job descriptions should remain unchanged in the raw dataset.
8. Cleaned and transformed data should be stored separately.
9. The source and collection date must be recorded.
10. Personal or sensitive information must not be collected.

## Minimum Dataset Size

The target is at least 1,000 Australian data-related job vacancies.

A smaller dataset may be used for the initial prototype, but the final analysis should include enough records to compare:

- job titles
- locations
- industries
- experience levels
- technical skills
- salary ranges
- working arrangements
