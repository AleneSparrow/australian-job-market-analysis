# Data Sources

## Primary Source: Adzuna Jobs API

The main dataset will be collected through the official Adzuna Jobs API.

The API provides current Australian job advertisement data in JSON format.

### Planned Search Terms

- Data Analyst
- Junior Data Analyst
- Business Analyst
- BI Analyst
- Reporting Analyst
- Insights Analyst
- Analytics Consultant

### Country

Australia (`au`)

### Expected API Fields

- Job identifier
- Job title
- Company
- Location
- Job description
- Posting date
- Minimum salary
- Maximum salary
- Job category
- Contract type
- Contract time
- Redirect URL

### Collection Method

Python will be used to send requests to the API, collect paginated results, validate responses, and save the original data.

Raw API responses will be stored without manual modification.

## Supporting Source: Australian Bureau of Statistics

Australian Bureau of Statistics Job Vacancies data will be used to provide national labour-market context.

The ABS data includes:

- Total Australian job vacancies
- Vacancies by state and territory
- Vacancies by industry
- Public and private sector vacancies
- Historical vacancy trends

This source will not provide individual job advertisements or skill requirements.

## Supporting Source: Jobs and Skills Australia

Jobs and Skills Australia occupation profiles will be used for:

- Occupational definitions
- Employment statistics
- Education profiles
- Industry distribution
- Standard occupation classifications

## Sources Not Used for Primary Collection

### SEEK

SEEK may be referenced as an important Australian job platform, but its website will not be scraped for this project.

### Kaggle

Kaggle datasets may be used only for comparison or prototyping.

They will not be the main source because they may be outdated, poorly documented, or collected using unclear methods.

## Data Collection Date

The collection date and API query parameters will be recorded for every extraction.

## Ethical and Reproducibility Principles

1. Use official APIs and downloadable public datasets where possible.
2. Do not collect applicant or personal information.
3. Respect API limits and terms of use.
4. Keep raw data separate from processed data.
5. Record the source, collection date, search term, and request parameters.
6. Never publish API credentials in the GitHub repository.
