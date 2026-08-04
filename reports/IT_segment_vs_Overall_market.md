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

## 5. Remote / Hybrid / Onsite

**Query:**
```sql
SELECT remote_type, COUNT(*) AS vacancies_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percent
FROM it_jobs
GROUP BY remote_type
ORDER BY vacancies_count DESC;
```

**Result:**

| Type | IT Segment | % | Overall Market % |
|---|---|---|---|
| Not detected (NULL) | 4,397 | 86.8% | 94.2% |
| hybrid | 373 | 7.4% | 2.1% |
| onsite | 169 | 3.3% | 2.4% |
| remote | 124 | 2.4% | 1.4% |

**Insight:** work-location format is stated far more often in IT listings (13.2% vs. 5.8% market-wide), and hybrid clearly leads within IT (7.4%, more than 3x its overall-market share), whereas onsite led on the general market. This is a meaningful and expected divergence — IT roles are simply more amenable to hybrid arrangements than the market's average mix of healthcare, trades, and support-work listings.

---

## 6. Experience Level

**Query:**
```sql
SELECT jf.experience_level, COUNT(*) AS vacancies_count
FROM jobs_features jf
JOIN it_jobs ij ON jf.job_id = ij.job_id
GROUP BY jf.experience_level
ORDER BY vacancies_count DESC;
```

**Result:**

| Level | Count |
|---|---|
| Not detected (NULL) | 3,171 |
| senior | 1,456 |
| principal | 145 |
| lead | 92 |
| junior | 62 |
| mid | 57 |
| graduate | 43 |
| manager | 25 |
| entry | 6 |
| staff | 6 |

**Insight:** the senior-heavy skew seen in the overall market is even more pronounced within IT — senior listings outnumber junior almost **23:1** (1,456 vs. 62), compared to roughly 12:1 market-wide. Junior + entry-level listings combined make up just 1.3% of the IT subset (68 out of 5,063). This is a strong, quotable finding for an international audience considering the Australian IT market: entry points for early-career candidates appear scarce relative to senior demand in this dataset.

---

## 7. Visa Sponsorship

**Query:**
```sql
SELECT jf.visa_sponsorship, COUNT(*) AS vacancies_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2) AS percent
FROM jobs_features jf
JOIN it_jobs ij ON jf.job_id = ij.job_id
GROUP BY jf.visa_sponsorship;
```

**Result:** no sponsorship — 5,055 (99.84%), sponsorship offered — 8 (0.16%).

| Segment | % offering visa sponsorship |
|---|---|
| Overall market | 0.4% |
| IT segment | 0.16% |

**Insight:** counterintuitively, visa sponsorship is mentioned even *less* often within IT (0.16%) than in the overall market (0.4%). This runs against the common assumption that IT roles are more open to sponsoring international candidates. Plausible explanations (not confirmed by this data alone): IT listings sourced from Workforce Australia may skew toward domestically-focused hiring; employers actively sponsoring international IT talent may post primarily through channels not captured in this dataset (e.g. LinkedIn, specialised tech recruiters); and explicit "visa sponsorship" wording in a listing is simply rare regardless of industry. Worth flagging as a genuinely surprising finding rather than smoothing it over.

---



## 8. Top Employers (IT Segment)

**Query:**
```sql
SELECT company, COUNT(*) AS vacancies_count
FROM it_jobs
GROUP BY company
ORDER BY vacancies_count DESC
LIMIT 20;
```

**Result (top 10):**

| Company | IT Vacancies |
|---|---|
| not specified | 4,244 |
| Medical Jobs Australia | 112 |
| SocialbleTech | 52 |
| AI Talent Pty Ltd | 32 |
| AMA Group Solutions | 18 |
| Publicis Media | 13 |
| Phillip Riley Projects | 13 |
| Mane Consulting | 12 |
| Apprise Consulting | 10 |
| Recruitment Innovations | 10 |

| Segment | % "not specified" |
|---|---|
| Overall market | 88% |
| IT segment | 84% |

**Insight:** employer disclosure is slightly better in IT than the overall market (84% vs. 88% "not specified"), though still far from good — a "top employers" read on the remaining 16% should carry the same representativeness caveat as the overall-market version. Notably, the named employers within IT are a mix of recruitment/staffing agencies (Medical Jobs Australia, AI Talent, Recruitment Innovations) and at least one recognisable direct employer further down the list — Deloitte (5 listings) — suggesting a handful of large consultancies do post directly, even if agencies dominate the visible portion.

---

## 9. Top Job Titles (IT Segment)

**Query:**
```sql
SELECT title, COUNT(*) AS vacancies_count
FROM it_jobs
GROUP BY title
ORDER BY vacancies_count DESC
LIMIT 20;
```

**Result:** identical to the list already surfaced while building the `it_jobs` title filter (see the filter-development query results) — Software Engineer (108), Senior Software Engineer (78), Data Engineer (70), Data Analyst (67), Systems Engineer (55), Solution Architect (48), Network Engineer (48), Senior Data Engineer (41), DevOps Engineer (34), Senior Network Engineer (34)...

**Insight:** no new finding here — this table is included for completeness in the comparison document, since the equivalent overall-market top-titles table (EDA Findings section 7) is dominated by non-IT roles (Disability Support Worker, Registered Nurse, Chef). Side by side, the two tables are themselves the clearest demonstration of why the `it_jobs` subset was necessary: the general "Top Job Titles" query on the full dataset does not represent the IT market at all.

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
| Work format stated | 5.8% of listings | 13.2% of listings | IT discloses format 2.3x more often |
| Leading format (where stated) | onsite | hybrid | IT skews hybrid |
| Senior : Junior ratio | ~12 : 1 | ~23 : 1 | IT even more senior-skewed |
| Junior + entry share | — | 1.3% of IT subset | very limited entry points in IT |
| Visa sponsorship offered | 0.4% | 0.16% | IT less likely, counterintuitively |
| Employer "not specified" | 88% | 84% | IT marginally more transparent |

---

## Open question / next step

Salary-by-skill analysis on the IT subset (e.g. average salary where `python = true` vs
not) is possible but should be flagged with the small-sample caveat (only ~135 IT listings
have salary data) — see EDA Findings section 6 for the full salary-coverage discussion.

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

## 5. Remote / Hybrid / Onsite

**Query:**
```sql
SELECT remote_type, COUNT(*) AS vacancies_count,
       ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 1) AS percent
FROM it_jobs
GROUP BY remote_type
ORDER BY vacancies_count DESC;
```

**Result:**

| Type | IT Segment | % | Overall Market % |
|---|---|---|---|
| Not detected (NULL) | 4,397 | 86.8% | 94.2% |
| hybrid | 373 | 7.4% | 2.1% |
| onsite | 169 | 3.3% | 2.4% |
| remote | 124 | 2.4% | 1.4% |

**Insight:** work-location format is stated far more often in IT listings (13.2% vs. 5.8% market-wide), and hybrid clearly leads within IT (7.4%, more than 3x its overall-market share), whereas onsite led on the general market. This is a meaningful and expected divergence — IT roles are simply more amenable to hybrid arrangements than the market's average mix of healthcare, trades, and support-work listings.

---

## 6. Experience Level

**Query:**
```sql
SELECT jf.experience_level, COUNT(*) AS vacancies_count
FROM jobs_features jf
JOIN it_jobs ij ON jf.job_id = ij.job_id
GROUP BY jf.experience_level
ORDER BY vacancies_count DESC;
```

**Result:**

| Level | Count |
|---|---|
| Not detected (NULL) | 3,171 |
| senior | 1,456 |
| principal | 145 |
| lead | 92 |
| junior | 62 |
| mid | 57 |
| graduate | 43 |
| manager | 25 |
| entry | 6 |
| staff | 6 |

**Insight:** the senior-heavy skew seen in the overall market is even more pronounced within IT — senior listings outnumber junior almost **23:1** (1,456 vs. 62), compared to roughly 12:1 market-wide. Junior + entry-level listings combined make up just 1.3% of the IT subset (68 out of 5,063). This is a strong, quotable finding for an international audience considering the Australian IT market: entry points for early-career candidates appear scarce relative to senior demand in this dataset.

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
| Work format stated | 5.8% of listings | 13.2% of listings | IT discloses format 2.3x more often |
| Leading format (where stated) | onsite | hybrid | IT skews hybrid |
| Senior : Junior ratio | ~12 : 1 | ~23 : 1 | IT even more senior-skewed |
| Junior + entry share | — | 1.3% of IT subset | very limited entry points in IT

---

## Open question / next step

Salary-by-skill analysis on the IT subset (e.g. average salary where `python = true` vs
not) is possible but should be flagged with the small-sample caveat (only ~135 IT listings
have salary data) — see EDA Findings section 6 for the full salary-coverage discussion.
