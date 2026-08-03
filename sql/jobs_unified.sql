CREATE TABLE jobs_unified (
    id              SERIAL PRIMARY KEY,
    source          VARCHAR(20),
    title           TEXT,
    company         TEXT,
    tenure_label    VARCHAR(50),
    salary_period   VARCHAR(20),
    salary_min      NUMERIC,
    salary_max      NUMERIC,
    description     TEXT,
    keywords        TEXT[],
    address_short   TEXT,
    coordinates     geography(Point, 4326)
);

INSERT INTO jobs_unified (source, title, company, tenure_label, salary_period, salary_min, salary_max, description, keywords, address_short, coordinates)
SELECT 'adzuna', title_clean, company, tenure_label, salary_period, salary_min1, salary_max1,
       description_clean, keywords, address_short, NULL::geography(Point,4326)
FROM adzuna_jobs_stage

UNION ALL

SELECT 'workforce', title_clean, employername, tenure_label, NULL, NULL, NULL,
       description_clean, keywords, address_short, coordinates
FROM workforce_jobs_stage

UNION ALL

SELECT 'jooble', title_clean, company, NULL, NULL, NULL, NULL,
       description_clean, keywords, NULL, NULL::geography(Point,4326)
FROM jooble_jobs_stage;
