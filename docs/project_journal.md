Australian Job Market Analysis — Project Journal

Purpose of this file

This document records the project step by step: what was done, why it was done, how the code works, what decisions were made, what problems appeared, and how they were solved.

The file should be updated throughout the project and can later be used to:

• prepare for interviews;
• write the final GitHub README;
• explain the project architecture;
• describe technical decisions;
• prepare a portfolio case study;
• remember commands, scripts, and data-processing steps.

────────

1. Project idea

Project name

Australian Job Market Analysis

Main goal

Build an end-to-end data analytics project that examines the Australian job market for data-related roles.

The project should answer questions such as:

• Which data-related job titles are most common?
• Which technical skills are requested most often?
• Which Australian cities and states have the most vacancies?
• Which industries hire the most data professionals?
• What salary ranges are offered?
• How do requirements differ by experience level?
• How common are remote, hybrid, and on-site roles?
• Which skills should an entry-level analyst prioritise?

Target roles

• Data Analyst
• Junior Data Analyst
• Business Analyst
• BI Analyst
• Reporting Analyst
• Insights Analyst
• Analytics Consultant

────────

2. GitHub repository

A public GitHub repository was created for the project.

Repository structure

```text
australian-job-market-analysis/
├── data/
│   ├── raw/
│   └── processed/
├── notebooks/
├── reports/
├── sql/
├── src/
├── visualizations/
├── README.md
├── business_questions.md
├── data_requirements.md
└── data_sources.md
```

Purpose of each folder

data/raw

Contains original data received from the source.

Raw data should not be manually edited because it serves as the original reference point.

data/processed

Contains cleaned, transformed, standardised, and analysis-ready data.

notebooks

Contains Jupyter notebooks for exploration, cleaning, analysis, and visualisation.

sql

Contains SQL queries used for data cleaning, transformation, and analysis.

src

Contains reusable Python scripts.

The first script created was:

```text
src/collect_adzuna_jobs.py
```

visualizations

Contains charts, dashboard screenshots, and other visual outputs.

reports

Contains analytical reports, summaries, presentations, and final findings.

────────

3. Project documentation files

README.md

The main presentation page of the project.

It currently includes:

• project overview;
• goals;
• tools;
• project structure;
• planned workflow;
• author information.

The README will be expanded later with:

• final dataset description;
• data-cleaning process;
• analysis results;
• dashboard screenshots;
• key findings;
• recommendations;
• instructions for reproducing the project.

business_questions.md

Defines the main research question and supporting analytical questions.

data_requirements.md

Defines which fields are needed in the dataset.

Examples:

• job_id
• job_title
• company
• location
• city
• state
• industry
• salary_min
• salary_max
• job_description
• skills
• experience_level
• posting_date
• source
• job_url

It also records basic data-quality rules.

data_sources.md

Documents the selected sources.

The primary source is the Adzuna Jobs API.

Supporting sources may include:

• Australian Bureau of Statistics;
• Jobs and Skills Australia.

────────

4. Why Adzuna API was selected

The project needed current Australian job-advertisement data.

Adzuna API was selected because it provides structured job data through an official API.

This is preferable to using an unknown CSV because:

• the data can be collected again;
• the collection parameters are known;
• the collection date can be recorded;
• the process is reproducible;
• the source is documented;
• the project demonstrates API and Python skills.

Direct scraping of job websites was not selected for the initial version because it introduces additional legal, technical, and maintenance problems.

────────

5. API registration and credentials

An Adzuna developer account was created.

The account provided:

```text
APP_ID
APP_KEY
```

These values authenticate requests to the API.

Security decision

The credentials are not written directly into the Python script.

They are stored locally in:

```text
.env
```

Example structure:

```env
ADZUNA_APP_ID=your_application_id
ADZUNA_APP_KEY=your_application_key
```

The .env file must not be uploaded to GitHub.

For this reason, the following entry is added to .gitignore:

```gitignore
.env
```

This separates public code from private credentials.

────────

6. Local project setup

The GitHub repository was cloned to the Mac.

Command used

```bash
git clone https://github.com/USERNAME/australian-job-market-analysis.git
```

What git clone did

It downloaded a local copy of the GitHub repository onto the computer.

The GitHub repository is the remote version.

The folder on the Mac is the local working copy.

The local copy is needed because Python code is executed on the computer, not automatically on the GitHub website.

Entering the project folder

```bash
cd ~/Documents/australian-job-market-analysis
```

Checking the current folder

```bash
pwd
```

Viewing files

```bash
ls
```

Viewing hidden files

```bash
ls -la
```

Hidden files include files whose names begin with a dot, such as:

```text
.env
.gitignore
.git
```

────────

7. Python dependencies

The script requires two external libraries:

```text
requests
python-dotenv
```

They were installed with:

```bash
python3 -m pip install requests python-dotenv
```

Why they are needed

requests

Sends HTTP requests to the Adzuna API.

python-dotenv

Reads the API credentials from the local .env file.

────────

8. Data collection script

The script is stored at:

```text
src/collect_adzuna_jobs.py
```

Main workflow

```text
Load libraries
→ locate the project folder
→ read API credentials from .env
→ build an API request
→ send the request to Adzuna
→ receive JSON
→ validate the server response
→ extract selected fields
→ create data/raw if necessary
→ save the original JSON
→ save a flat CSV
```

────────

9. How the script works

Imports

```python
import csv
import json
import os
from datetime import datetime
from pathlib import Path

import requests
from dotenv import load_dotenv
```

csv

Creates CSV files.

json

Reads and writes JSON data.

os

Reads environment variables such as ADZUNA_APP_ID.

datetime

Creates collection dates and date-based filenames.

Path

Builds file paths in a reliable and readable way.

requests

Sends the API request.

load_dotenv

Loads values from .env.

────────

10. Project paths

```python
PROJECT_ROOT = Path(__file__).resolve().parent.parent
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
```

Meaning

__file__ refers to the currently running Python file:

```text
src/collect_adzuna_jobs.py
```

The first .parent moves to:

```text
src/
```

The second .parent moves to:

```text
australian-job-market-analysis/
```

That location becomes PROJECT_ROOT.

Then this line:

```python
RAW_DATA_DIR = PROJECT_ROOT / "data" / "raw"
```

builds the destination path:

```text
australian-job-market-analysis/data/raw
```

The data was saved in raw because the code explicitly defined that location.

Python did not choose the folder automatically.

────────

11. Loading the credentials

```python
load_dotenv(PROJECT_ROOT / ".env")
```

This tells Python to open the .env file located in the project root.

The script then reads the credentials:

```python
app_id = os.getenv("ADZUNA_APP_ID")
app_key = os.getenv("ADZUNA_APP_KEY")
```

The names must exactly match the names inside .env.

The script checks whether both values exist.

If one is missing, it stops with a readable error instead of sending an invalid request.

────────

12. API request

The endpoint used is similar to:

```text
https://api.adzuna.com/v1/api/jobs/au/search/1
```

Endpoint meaning

• jobs — job advertisements;
• au — Australia;
• search — search endpoint;
• 1 — first page of results.

Request parameters

```python
params = {
    "app_id": app_id,
    "app_key": app_key,
    "results_per_page": 20,
    "what": "data analyst",
    "content-type": "application/json",
}
```

results_per_page

Requests up to 20 vacancies.

This was a test extraction rather than the final full dataset.

what

Defines the search phrase:

```text
data analyst
```

Credentials

app_id and app_key prove that the request is authorised.

────────

13. Sending the request

```python
response = requests.get(url, params=params, timeout=30)
```

This sends an HTTP GET request.

A GET request asks a server to return data.

The timeout=30 setting prevents the script from waiting forever if the server does not respond.

The response is stored in the variable:

```text
response
```

────────

14. Response validation

```python
response.raise_for_status()
```

This checks the HTTP response status.

Examples:

• 200 — success;
• 401 — authentication problem;
• 404 — invalid endpoint;
• 429 — request limit exceeded;
• 500 — server error.

If an error status is returned, the script stops instead of saving an invalid response.

────────

15. Converting JSON into Python data

```python
data = response.json()
```

The API sends JSON text.

response.json() converts it into Python objects:

• JSON objects become dictionaries;
• JSON arrays become lists;
• JSON strings become Python strings;
• JSON numbers become Python numbers;
• JSON null becomes Python None.

The full API response is stored in:

```text
data
```

────────

16. Flattening nested data for CSV

The API response is nested.

Example:

```json
{
  "company": {
    "display_name": "Example Company"
  }
}
```

A CSV needs a flat column:

```text
company = Example Company
```

The script loops through the vacancies:

```python
for job in data.get("results", []):
```

Each vacancy is temporarily stored in job.

The script extracts fields such as:

• job ID;
• title;
• company;
• location;
• category;
• description;
• posting date;
• minimum salary;
• maximum salary;
• contract type;
• redirect URL.

It also adds metadata:

• search term;
• collection date;
• source.

────────

17. Why .get() is used

Example:

```python
job.get("salary_min")
```

If the salary exists, the value is returned.

If the field is missing, Python returns None.

This prevents the script from crashing when a vacancy does not contain every possible field.

For nested fields, the script uses safe fallbacks:

```python
company = job.get("company") or {}
```

If the company object is missing, an empty dictionary is used.

────────

18. Creating the output folder

```python
RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
```

This creates data/raw if it does not exist.

parents=True

Creates missing parent folders.

exist_ok=True

Does not produce an error if the folder already exists.

────────

19. Output filenames

The current date is added to the filenames:

```python
date_stamp = datetime.now().strftime("%Y-%m-%d")
```

Example:

```text
2026-07-27
```

The output paths are then created:

```text
data/raw/adzuna_data_analyst_2026-07-27.json
data/raw/adzuna_data_analyst_2026-07-27.csv
```

This makes each extraction traceable by date.

────────

20. Saving JSON

The full API response is saved as JSON.

Why:

• preserves the original nested structure;
• keeps fields not selected for CSV;
• allows the transformation to be repeated without calling the API again;
• provides a raw reference copy.

────────

21. Saving CSV

The selected fields are written to a flat CSV table.

Why:

• easier to inspect;
• easier to load into Excel;
• easier to query with SQL;
• easier to analyse with pandas;
• easier to connect to Tableau.

The first dictionary provides the column names.

Each vacancy becomes one row.

────────

22. Why both files were initially placed in data/raw

The JSON is clearly raw data.

The CSV is already flattened, but it has not yet been cleaned, standardised, deduplicated, or enriched.

For the initial prototype, both were stored in data/raw.

A more precise future structure may be:

```text
data/raw/
└── original API JSON

data/interim/
└── flattened CSV

data/processed/
└── cleaned analysis-ready CSV
```

This decision should be revisited before the final portfolio version.

────────

23. Running the script

The command used was:

```bash
python3 src/collect_adzuna_jobs.py
```

Meaning

python3

Starts the Python interpreter.

src/collect_adzuna_jobs.py

Tells Python which file to execute.

Python reads the file and runs the instructions.

The script does not execute merely because it exists on GitHub.

It runs only when Python is told to execute it.

────────

24. Interview explanation

20-second version

> I automated the collection of Australian Data Analyst job advertisements using Python and the Adzuna API. The script reads API credentials from a local `.env` file, sends a GET request with the search parameters, validates the response, saves the original JSON in `data/raw`, and creates a flattened CSV for later analysis.

Longer version

> I needed a current and reproducible dataset for the Australian job-market project, so I used the official Adzuna API rather than relying on an undocumented CSV. I wrote a Python script that reads credentials from a local `.env` file so that secrets are not exposed in the public repository. The script sends an HTTP GET request for Australian Data Analyst jobs, checks the response status, converts the returned JSON into Python objects, preserves the complete response as raw JSON, and extracts selected fields into a flat CSV. The raw and processed layers are kept separate so that the transformation process remains traceable and reproducible.

Why API instead of a downloaded dataset?

> An API provides current data, documented parameters, a known source, and a reproducible collection process.

Why .env?

> To keep credentials separate from public code and prevent API keys from being committed to GitHub.

Why data/raw?

> To preserve the original source data and make it possible to audit or repeat later transformations.

Why JSON and CSV?

> JSON preserves the full API response, while CSV provides a flat structure that is easier to use in SQL, Excel, pandas, and Tableau.

How were missing values handled?

> The script uses `.get()` so that missing optional fields become empty values instead of causing the extraction to fail.

How were API errors handled?

> `response.raise_for_status()` stops the process if the server returns an authentication, rate-limit, endpoint, or server error.

────────

25. Current project status

Completed:

• GitHub repository created;
• project folders created;
• folder README files created;
• main README created;
• business questions documented;
• data requirements documented;
• data sources documented;
• Adzuna API account created;
• API credentials stored locally;
• .env excluded from Git;
• repository cloned to Mac;
• Python dependencies installed;
• first data-collection script created;
• first test extraction completed;
• raw JSON and CSV files created.

Next steps:

1. Inspect the extracted data.
2. Check the number of records and fields.
3. Review missing values.
4. Check duplicate vacancies.
5. Decide whether CSV should move to an interim layer.
6. Expand the script to collect multiple pages.
7. Add several search terms.
8. Avoid duplicates across search terms.
9. Create a data-validation report.
10. Build the cleaning pipeline.
11. Save the cleaned dataset to data/processed.
12. Begin exploratory analysis.
