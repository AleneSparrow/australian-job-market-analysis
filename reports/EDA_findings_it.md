# IT Segment vs. Overall Market — Australian Job Market Project

Supplementary report. Compares the IT-specific subset (`it_jobs` view, 5,063 listings)
against the full dataset (105,337 listings) to see where the IT segment differs from
the broader Australian labour market.

**How the IT subset was built:** a listing is included in `it_jobs` if it either (a) has
at least one entry in `job_skills` (an explicit technical skill was detected in the text),
or (b) its title matches a narrowed set of IT-specific role patterns (e.g. "software
engineer", "data analyst", "devops engineer", "cyber security engineer"). Broad terms like
bare "engineer" or "architect" were intentionally excluded from the title match, since an
early version of the filter pulled in non-IT roles such as Mechanical Engineer, Civil
Engineer, and Structural Engineer (see EDA Findings, section 7, for that investigation).

```sql
CREATE VIEW it_jobs AS
SELECT ju.*
FROM jobs_unified ju
WHERE ju.job_id IN (SELECT DISTINCT job_id FROM job_skills)
   OR ju.title ILIKE ANY (ARRAY[
     '%software engineer%', '%data engineer%', '%devops engineer%',
     '%cloud engineer%', '%network engineer%', '%systems engineer%',
     '%qa engineer%', '%test engineer%', '%security engineer%',
     '%ml engineer%', '%machine learning engineer%', '%platform engineer%',
     '%site reliability engineer%', '%backend engineer%', '%frontend engineer%',
     '%full stack engineer%', '%developer%', '%data scientist%',
     '%data analyst%', '%software%', '%programmer%', '%solution architect%',
     '%database admin%', '%dba%', '%cyber%', '%web developer%'
   ]);
```

**Size:** 5,063 IT listings out of 105,337 total (4.8% of the dataset).

---

## 1. Skills

Identical to the overall-market top skills (AWS 526, Excel 387, Azure 333, Python 127,
SQL 116...), since the `job_skills` table is one of the two inclusion criteria for the
`it_jobs` view — every listing with a detected skill is IT by definition. No new insight
here beyond what's already in EDA Findings section 1; included for completeness only.

---

## 2. Salary Coverage

**Query:**
```sql
SELECT 
  COUNT(*) AS total_it_jobs,
  COUNT(salary_min) AS with_salary,
  ROUND(100.0 * COUNT(salary_min) / COUNT(*), 2) AS pct_with_salary
FROM it_jobs;
```

**Result:** 5,063 total, 135 with salary (**2.67%**).

| Segment | % with salary |
|---|---|
| Overall market | 1.55% |
| IT segment | 2.67% |

**Insight:** IT listings disclose salary almost twice as often as the market average. The absolute sample is still small (135 listings), so any salary-by-skill breakdown on this subset should be treated as directional, not definitive — but the direction itself (IT employers being somewhat more salary-transparent) is a reasonable takeaway.

---

## 3. Geographic Distribution

**Query:**
```sql
SELECT address_short, COUNT(*) AS vacancies_count
FROM it_jobs
GROUP BY address_short
ORDER BY vacancies_count DESC
LIMIT 15;
```

**Result (top 6):**

| City/Region | IT Vacancies |
|---|---|
| Sydney, NSW | 1,368 |
| Melbourne, VIC | 893 |
| Canberra, ACT | 717 |
| Perth, WA | 421 |
| Brisbane City, QLD | 375 |
| Adelaide, SA | 264 |

**Comparison to overall market ranking:**

| Rank | Overall Market | IT Segment |
|---|---|---|
| 1 | Sydney | Sydney |
| 2 | Perth | Melbourne |
| 3 | Melbourne | **Canberra** |
| 4 | Brisbane | Perth |
| 5 | Adelaide | Brisbane |

**Insight:** Canberra jumps from 6th place in the overall market to 3rd in the IT segment — plausibly driven by government IT contracts and consulting work concentrated in the capital. Perth, which leads the overall market (likely due to mining-sector demand), drops to 4th in IT — mining-heavy Western Australia doesn't translate into a proportional IT hiring share. Sydney and Melbourne remain the two biggest IT hubs either way.

---

## 4. Employment Type

**Query:**
```sql
SELECT 
  SUM(CASE WHEN jf.full_time THEN 1 ELSE 0 END) AS full_time,
  SUM(CASE WHEN jf.part_time THEN 1 ELSE 0 END) AS part_time,
  SUM(CASE WHEN jf.contract THEN 1 ELSE 0 END) AS contract
FROM jobs_features jf
JOIN it_jobs ij ON jf.job_id = ij.job_id;
```

**Result:** full_time — 601, part_time — 45, contract — (not yet captured in this run).

**Insight:** Full-time dominates even more heavily in IT than in the overall market — the full_time-to-part_time ratio is roughly 13:1 in IT, versus about 3:1 market-wide. IT listings are markedly more likely to be full-time, standard employment rather than part-time or casual work.

---

## Summary Table

| Metric | Overall Market | IT Segment | Difference |
|---|---|---|---|
| Total listings | 105,337 | 5,063 (4.8%) | — |
| % with salary listed | 1.55% | 2.67% | IT ~1.7x more transparent |
| Top city | Sydney | Sydney | same |
| 2nd city | Perth | Melbourne | shifted |
| Notable riser | — | Canberra (6th → 3rd) | govt/consulting effect |
| Notable faller | — | Perth (1st → 4th) | mining vs. IT mismatch |
| Full-time share | dominant, but closer to other types | dominant, ~13:1 vs part-time | IT more standardised employment |

---

## Open question / next step

Salary-by-skill analysis on the IT subset (e.g. average salary where `python = true` vs
not) is possible but should be flagged with the small-sample caveat (only ~135 IT listings
have salary data) — see EDA Findings section 6 for the full salary-coverage discussion.
