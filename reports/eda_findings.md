# EDA Findings — Australian IT Labour Market Project

Working log of the exploratory data analysis (EDA). Format: query → result → insight.
Updated as the analysis progresses; final insights are folded into the project README.

---

## 1. Top Skills (by job mentions)

**Query:**
```sql
SELECT skill, COUNT(DISTINCT job_id) AS jobs_count
FROM job_skills
GROUP BY skill
ORDER BY jobs_count DESC
LIMIT 20;
```

**Result (top 10):**

| Skill | Jobs |
|---|---|
| aws | 526 |
| excel | 387 |
| azure | 333 |
| python | 127 |
| sql | 116 |
| spark | 109 |
| power_bi | 83 |
| linux | 80 |
| gcp | 77 |
| databricks | 56 |

**Insight:** AWS, Excel and Azure clearly lead over the rest. Python and SQL are the most common "core programming" skills, but appear far less often than cloud platforms and Excel. Even the top skill (AWS) shows up in under 1% of all listings — a sign that explicit skill extraction only catches skills that are directly mentioned in the text, not the full technology stack of the market.

---

## 2. Cloud Platforms

**Query:**
```sql
SELECT 
  SUM(CASE WHEN aws THEN 1 ELSE 0 END) AS aws_count,
  SUM(CASE WHEN azure THEN 1 ELSE 0 END) AS azure_count,
  SUM(CASE WHEN gcp THEN 1 ELSE 0 END) AS gcp_count
FROM jobs_features;
```

**Result:** AWS — 526, Azure — 333, GCP — 77.

**Insight:** AWS is the clear leader in the Australian market, with GCP notably behind both other providers.

---

## 3. Employment Type

**Query:**
```sql
SELECT 
  SUM(CASE WHEN full_time THEN 1 ELSE 0 END) AS full_time,
  SUM(CASE WHEN part_time THEN 1 ELSE 0 END) AS part_time,
  SUM(CASE WHEN contract THEN 1 ELSE 0 END) AS contract,
  SUM(CASE WHEN casual THEN 1 ELSE 0 END) AS casual
FROM jobs_features;
```

**Result:** full_time — 22,217, part_time — 6,859, contract — 6,113, casual — 4,786.

**Insight:** Full-time is the dominant employment type among listings where it's specified. However, the sum of all categories (~40K) is well below the total number of jobs (105,337) — for most listings this field is simply not populated (no explicit marker in the text).

---

## 4. Visa Sponsorship

**Query:**
```sql
SELECT visa_sponsorship, COUNT(*)
FROM jobs_features
GROUP BY visa_sponsorship;
```

**Result:** no sponsorship — 104,909, sponsorship offered — 428.

**Insight:** Only 0.4% of listings (428 out of 105,337) explicitly offer visa sponsorship — a short but telling data point for a section on labour market accessibility for migrants.

---

## 5. Experience Level (after fixing a bug in the extraction code)

**Original problem:** the first version of the experience-level extraction code used independent regex patterns (`senior`, `junior`, etc.) with no mutual exclusion. As a result, 510 listings ended up with contradictory labels — `senior = true AND junior = true` at the same time (e.g. from phrases like "junior to senior developers" appearing in a single posting).

**Fix:** added a single `experience_level` column with a priority order (highest to lowest: staff → principal → lead → manager → senior → mid → junior → entry → graduate), and narrowed the `lead` and `principal` patterns to avoid catching unrelated context ("lead generation", "Principal House Officer").

**Query (after fix):**
```sql
SELECT experience_level, COUNT(*)
FROM jobs_features
GROUP BY experience_level
ORDER BY COUNT(*) DESC;
```

**Result:**

| Level | Count |
|---|---|
| NULL (not detected) | 90,042 |
| senior | 10,736 |
| principal | 1,243 |
| graduate | 1,106 |
| junior | 889 |
| lead | 437 |
| mid | 384 |
| entry | 283 |
| manager | 244 |
| staff | 13 |

**Insight:** 85% of listings contain no explicit experience-level marker in the title/description — typical for a government job portal (Workforce Australia), where wording is less standardised than in IT-specific sources. Among listings with an explicit level, senior appears almost 12x more often than junior — likely reflecting the composition of the source (heavy in healthcare and public-sector roles) rather than the broader IT market.

---

## 6. Data Quality: Salary Coverage

**Query:**
```sql
SELECT 
  COUNT(*) AS total_jobs,
  COUNT(salary_min) AS with_salary,
  ROUND(100.0 * COUNT(salary_min) / COUNT(*), 2) AS pct_with_salary
FROM jobs_unified;
```

**Result:** 105,337 jobs total, 1,628 with a listed salary (**1.55%**).

**By source:**
```sql
SELECT 
  source,
  COUNT(*) AS total_jobs,
  COUNT(salary_min) AS with_salary,
  ROUND(100.0 * COUNT(salary_min) / COUNT(*), 2) AS pct_with_salary
FROM jobs_unified
GROUP BY source
ORDER BY total_jobs DESC;
```

| Source | Total jobs | With salary | % |
|---|---|---|---|
| workforce | 104,005 | 1,471 | 1.41% |
| adzuna | 996 | 120 | 12.05% |
| jooble | 336 | 37 | 11.01% |

**Insight (key dataset limitation):** salary analysis is mostly representative of the aggregators (Adzuna, Jooble), which make up under 1.5% of the whole dataset but contain ~90% of all salary data. The primary source (Workforce Australia, 98.7% of the dataset) almost never lists a salary — typical for an official government job portal. Any conclusions about "average market salary" need this caveat attached.

---

## 7. Top Job Titles

**Query:**
```sql
SELECT title, COUNT(*) AS vacancies_count
FROM jobs_unified
GROUP BY title
ORDER BY vacancies_count DESC
LIMIT 20;
```

**Result (top 10):**

| Title | Vacancies |
|---|---|
| Project Manager | 492 |
| Business Development Manager | 489 |
| Telstra Retail: Customer Service | 401 |
| Disability Support Worker | 378 |
| Support Worker | 327 |
| Business Analyst | 276 |
| Registered Nurse | 257 |
| Educator | 255 |
| Chef | 252 |
| Site Manager | 247 |

**Insight (important limitation):** the top titles contain almost no narrowly IT-specific roles — Disability Support Worker, Registered Nurse, Chef, and Educator dominate instead. This confirms the finding from the Data Quality section: the dataset in practice reflects the **general Australian labour market**, not a narrow IT segment, since the dominant source (Workforce Australia) is a government portal covering all industries. For the project to live up to its "IT Labour Market" framing, it's worth either explicitly carving out an IT-specific subset (by title/skills) or honestly reframing the scope in the README.

---

## 8. Top Employers

**Query:**
```sql
SELECT company, COUNT(*) AS vacancies_count
FROM jobs_unified
GROUP BY company
ORDER BY vacancies_count DESC
LIMIT 20;
```

**Result (top 10):**

| Company | Vacancies |
|---|---|
| not specified | 92,741 |
| Medical Jobs Australia | 3,968 |
| HealthcareLink | 1,128 |
| SocialbleTech | 885 |
| Recruitment Innovations P... | 299 |
| APPRISE CONSULTING | 193 |
| Medlo — Medical Recruitment | 162 |
| Global Skilled Employment | 144 |
| NETYOURJOB AUSTRALIA | 108 |
| Secret Customer Australia | 106 |

**Insight (critical data limitation):** 88% of listings (92,741 out of 105,337) have `company = "not specified"` — no employer listed. Of the remaining 12%, the top rows are mostly recruitment agencies (Medical Jobs Australia, HealthcareLink, Recruitment Innovations) rather than direct employers. **A "top employers" analysis on this data is not representative** and should not be presented as reflecting the real market of hiring companies — this needs to be flagged as a limitation rather than dropped from the report.

---

## 9. Geographic Distribution

**Query:**
```sql
SELECT address_short, COUNT(*) AS vacancies_count
FROM jobs_unified
GROUP BY address_short
ORDER BY vacancies_count DESC
LIMIT 20;
```

**Result (top 10):**

| City/Region | Vacancies |
|---|---|
| Sydney, NSW | 14,794 |
| Perth, WA | 11,834 |
| Melbourne, VIC | 11,603 |
| Brisbane City, QLD | 7,352 |
| Adelaide, SA | 7,047 |
| Canberra, ACT | 4,366 |
| Gold Coast Mc, QLD | 2,438 |
| Darwin, NT | 1,457 |
| Newcastle, NSW | 1,441 |
| Ballina, NSW | 1,429 |

**Insight:** Sydney, Perth, and Melbourne are the three clear leaders by number of listings, matching the expected distribution across Australia's largest cities. Field completeness is high — only 694 listings (0.7%) have no address (NULL). This is currently the cleanest and most reliable metric in the dataset — safe to use for a geographic dashboard without further caveats.

---

## 10. Remote / Hybrid / Onsite

**Background:** the `remote_type` column was found to be 100% NULL for the entire dataset (105,337 rows) — the field was never populated during the original feature-engineering pass. A text search confirmed the underlying signal exists (940 mentions of "remote", 2,079 of "hybrid", 586 of "work from home"/"wfh" in `description_clean`), so the field was backfilled with a keyword-based classifier (priority: hybrid → remote/wfh → onsite → null) rather than left empty.

**Query (after backfill):**
```sql
SELECT remote_type, COUNT(*) AS vacancies_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percent
FROM jobs_unified
GROUP BY remote_type
ORDER BY vacancies_count DESC;
```

**Result:**

| Type | Count | % |
|---|---|---|
| NULL (not detected) | 99,216 | 94.2% |
| onsite | 2,522 | 2.4% |
| hybrid | 2,175 | 2.1% |
| remote | 1,424 | 1.4% |

**Insight:** even after backfilling, 94.2% of listings give no explicit signal about work location format — consistent with the dataset's overall pattern of sparse structured detail outside title/basic fields. Among the ~5.8% that do specify, onsite slightly edges out hybrid and remote, plausibly reflecting the dataset's tilt toward roles (healthcare, trades, support work) that inherently require physical presence. The three categories are otherwise fairly evenly split, so no single format dominates among listings where it's stated.

---

## Not done yet (next steps)

- [ ] Skills-to-salary relationship (on the limited ~135-job sample with salary data, within `it_jobs`)
- [ ] Remote/hybrid/onsite breakdown for the `it_jobs` subset specifically
