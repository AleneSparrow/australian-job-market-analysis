# EDA Findings — Australian IT Labour Market Project

Working log of exploratory data analysis (EDA). Format: query → result → insight.  
Updated throughout the analysis; final insights are transferred to the project README.

---

## 1. Top Skills (by mentions in job vacancies)

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
|---|---:|
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

**Insight:** AWS, Excel, and Azure are significantly ahead of the other skills. Python and SQL are the most frequently mentioned purely programming-related skills, but they appear much less often than cloud platforms and Excel. Even the top skill, AWS, appears in less than 1% of all vacancies, which clearly indicates that explicit skill extraction captures skills only when they are directly mentioned in the text and does not reflect the market’s full technology stack.

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

**Insight:** AWS clearly leads the Australian market, while GCP falls significantly behind the other two providers.

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

**Insight:** Full-time is the dominant employment type among vacancies where the employment type is specified. At the same time, the total across all categories, approximately 40K, is significantly lower than the total number of vacancies, 105,337, because the field is not populated for most vacancies and there is no explicit marker in the text.

---

## 4. Visa Sponsorship

**Query:**
```sql
SELECT visa_sponsorship, COUNT(*)
FROM jobs_features
GROUP BY visa_sponsorship;
```

**Result:** without sponsorship — 104,909, with sponsorship — 428.

**Insight:** Only 0.4% of vacancies, 428 out of 105,337, explicitly offer visa sponsorship. This is an important and concise finding for the section on labour market accessibility for migrants.

---

## 5. Experience Level (after fixing a bug in the extraction code)

**Initial problem:** The first version of the experience-level extraction code used independent regex patterns such as `senior`, `junior`, and others without mutual exclusion. As a result, 510 vacancies received contradictory labels, with `senior = true AND junior = true` at the same time, for example because of phrases such as “junior to senior developers” in one job posting.

**Fix:** A single `experience_level` column was added with level priority from highest to lowest: staff → principal → lead → manager → senior → mid → junior → entry → graduate. The `lead` and `principal` patterns were also narrowed to avoid capturing unrelated contexts such as “lead generation” and “Principal House Officer”.

**Query (after the fix):**
```sql
SELECT experience_level, COUNT(*)
FROM jobs_features
GROUP BY experience_level
ORDER BY COUNT(*) DESC;
```

**Result:**

| Level | Count |
|---|---:|
| NULL (not identified) | 90,042 |
| senior | 10,736 |
| principal | 1,243 |
| graduate | 1,106 |
| junior | 889 |
| lead | 437 |
| mid | 384 |
| entry | 283 |
| manager | 244 |
| staff | 13 |

**Insight:** 85% of vacancies do not contain an explicit experience-level marker in the title or description. This is typical for a government job portal such as Workforce Australia, where wording is less standardised than on IT-specific sources. Among vacancies with an explicit level, senior appears almost 12 times more often than junior. This likely reflects the characteristics of the source, which contains many healthcare and public-sector vacancies, rather than the overall picture of the IT market.

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

**Result:** 105,337 vacancies in total, 1,628 with a specified salary (**1.55%**).

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
|---|---:|---:|---:|
| workforce | 104,005 | 1,471 | 1.41% |
| adzuna | 996 | 120 | 12.05% |
| jooble | 336 | 37 | 11.01% |

**Insight — important dataset limitation:** Salary analysis is representative primarily of aggregators such as Adzuna and Jooble, which account for less than 1.5% of the entire dataset but contain approximately 90% of all salary data. The main source, Workforce Australia, which represents 98.7% of the dataset, almost never provides salary information. This is typical of official government job portals. Any conclusions about the “average market salary” must include this limitation.

---

## Not Yet Completed — Next Steps

- [ ] Top vacancies by job title (`title`)
- [ ] Top employers by number of vacancies
- [ ] Geographic breakdown by states and cities using `address_short`
- [ ] Relationship between skills and salary using the limited sample of approximately 1,628 vacancies
