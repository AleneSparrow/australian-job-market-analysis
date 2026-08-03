UPDATE adzuna_jobs_stage
SET
    salary_average = CASE
        WHEN tenure_label = 'contract' THEN 'contract'
        WHEN salary_min BETWEEN 0   AND 79     AND salary_max BETWEEN 0   AND 79     THEN 'per/hour'
        WHEN salary_min BETWEEN 80  AND 499    AND salary_max BETWEEN 80  AND 499    THEN 'per/year'
        WHEN salary_min BETWEEN 500 AND 400000 AND salary_max BETWEEN 500 AND 400000 THEN 'per/year'
        ELSE NULL
    END,
    salary_min1 = CASE
        WHEN tenure_label = 'contract' THEN salary_min
        WHEN salary_min BETWEEN 0   AND 79     AND salary_max BETWEEN 0   AND 79     THEN salary_min
        WHEN salary_min BETWEEN 80  AND 499    AND salary_max BETWEEN 80  AND 499    THEN salary_min * 1000
        WHEN salary_min BETWEEN 500 AND 400000 AND salary_max BETWEEN 500 AND 400000 THEN salary_min
        ELSE NULL
    END,
    salary_max1 = CASE
        WHEN tenure_label = 'contract' THEN salary_max
        WHEN salary_min BETWEEN 0   AND 79     AND salary_max BETWEEN 0   AND 79     THEN salary_max
        WHEN salary_min BETWEEN 80  AND 499    AND salary_max BETWEEN 80  AND 499    THEN salary_max * 1000
        WHEN salary_min BETWEEN 500 AND 400000 AND salary_max BETWEEN 500 AND 400000 THEN salary_max
        ELSE NULL
    END
WHERE salary_min IS NOT NULL 
  AND salary_max IS NOT NULL;
