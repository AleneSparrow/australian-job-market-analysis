# Data Inventory

## Project

Australian Job Market Intelligence Platform

## Purpose

This document records all datasets collected for the project, including their source, file format, storage layer, collection status, and intended analytical use.

---

## Dataset Inventory

| Dataset ID | Dataset | Source | Format | Storage Location | Status | Intended Use |
|---|---|---|---|---|---|---|
| DS-001 | Adzuna Data Analyst Vacancies | Adzuna API | CSV | `data/interim/` | Collected | Job title, location, salary, employer and vacancy analysis |
| DS-002 | Adzuna Multiple IT Roles | Adzuna API | CSV | `data/interim/` | Collected | Comparison of demand across selected IT occupations |
| DS-003 | Adzuna Raw Landing Data | Adzuna API | CSV | `data/interim/` | Collected | Source validation and transformation audit |
| DS-004 | Jooble Landing Data | Jooble | CSV | `data/interim/` | Collected | Supplementary vacancy source and cross-source comparison |
| DS-005 | Jobs and Skills Australia IVI | Jobs and Skills Australia | CSV | `data/interim/jsa/` | Collected | State and occupation-level vacancy demand trends |
| DS-006 | ABS Employee Earnings and Hours | Australian Bureau of Statistics | CSV | `data/interim/abs/` | Collected | Official earnings benchmark by occupation |
| DS-007 | Workforce Australia Vacancies | Workforce Australia | HTML / JSON / binary network responses | `data/raw/workforce_australia/` | Collecting | Primary government vacancy source |
| DS-008 | Job Title Classification Output | Internal transformation | CSV | `data/interim/` | Collected | Standardised job-title classification for later analysis |

---

## Data Layers

### Raw

Original source files preserved without analytical modification.

Location:

`data/raw/`

### Interim

Extracted, partially structured, or transformed datasets that have not yet completed final cleaning and validation.

Location:

`data/interim/`

### Processed

Cleaned, standardised, validated datasets prepared for PostgreSQL, SQL analysis, and Tableau.

Location:

`data/processed/`

---

## Current Collection Status

- Adzuna: collected
- Jooble: collected
- Jobs and Skills Australia: collected
- Australian Bureau of Statistics: collected
- Workforce Australia: collection in progress

---

## Data Governance Rules

1. Raw source files must not be manually edited.
2. Transformations must be performed through reproducible scripts.
3. Original source fields must be retained where practical.
4. Derived fields must be documented.
5. File names must include source, subject, and collection date where applicable.
6. Processed data must not be created until profiling, cleaning, and validation are complete.

---

## Next Stage

After Workforce Australia collection is complete:

1. verify collection completion;
2. count files and records;
3. inspect schemas;
4. begin Data Profiling.