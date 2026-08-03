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

-- Adzuna: зарплата уже числовая, просто переносим как есть
INSERT INTO jobs_unified (source, title, company, tenure_label, salary_period, salary_min, salary_max, description, keywords, address_short, coordinates)
SELECT 'adzuna', title_clean, company, tenure_label, salary_period, salary_min1, salary_max1,
       description_clean, keywords, address_short, NULL::geography(Point,4326)
FROM adzuna_jobs_stage;

-- Workforce: парсим salary_label в числа
INSERT INTO jobs_unified (source, title, company, tenure_label, salary_period, salary_min, salary_max, description, keywords, address_short, coordinates)
SELECT
    'workforce',
    title_clean,
    employername,
    tenure_label,
    CASE
        WHEN salary_label ILIKE '%hour%' THEN 'hourly'
        WHEN salary_label ILIKE '%year%' OR salary_label ILIKE '%annum%' THEN 'yearly'
        WHEN salary_label ILIKE '%day%' THEN 'daily'
        ELSE NULL
    END,
    NULLIF(regexp_replace(split_part(salary_label, '-', 1), '[^0-9.]', '', 'g'), '')::numeric,
    NULLIF(regexp_replace(split_part(salary_label, '-', 2), '[^0-9.]', '', 'g'), '')::numeric,
    description_clean,
    keywords,
    address_short,
    coordinates
FROM workforce_jobs_stage;

-- Jooble: тот же принцип
INSERT INTO jobs_unified (source, title, company, tenure_label, salary_period, salary_min, salary_max, description, keywords, address_short, coordinates)
SELECT
    'jooble',
    title_clean,
    company,
    NULL,
    CASE
        WHEN salary_label ILIKE '%hour%' THEN 'hourly'
        WHEN salary_label ILIKE '%year%' OR salary_label ILIKE '%annum%' THEN 'yearly'
        WHEN salary_label ILIKE '%day%' THEN 'daily'
        ELSE NULL
    END,
    NULLIF(regexp_replace(split_part(salary_label, '-', 1), '[^0-9.]', '', 'g'), '')::numeric,
    NULLIF(regexp_replace(split_part(salary_label, '-', 2), '[^0-9.]', '', 'g'), '')::numeric,
    description_clean,
    keywords,
    NULL,
    NULL::geography(Point,4326)
FROM jooble_jobs_stage;


INSERT INTO jobs_unified (source, title, company, tenure_label, salary_period, salary_min, salary_max, description, keywords, address_short, coordinates)
SELECT
    'workforce',
    title_clean,
    employername,
    tenure_label,

    -- период
    CASE
        WHEN salary_label ILIKE '%hourly%' THEN 'hourly'
        WHEN salary_label ~ '^\$' OR salary_label ~ '^[<>]' THEN 'yearly'
        ELSE NULL
    END,

    -- salary_min
    CASE
        WHEN salary_label ~ '^\$[0-9,]+\s*-\s*\$[0-9,]+$' THEN
            NULLIF(regexp_replace(split_part(salary_label, '-', 1), '[^0-9]', '', 'g'), '')::numeric
        WHEN salary_label ~ '^>\$[0-9,]+$' THEN
            NULLIF(regexp_replace(salary_label, '[^0-9]', '', 'g'), '')::numeric
        ELSE NULL
    END,

    -- salary_max
    CASE
        WHEN salary_label ~ '^\$[0-9,]+\s*-\s*\$[0-9,]+$' THEN
            NULLIF(regexp_replace(split_part(salary_label, '-', 2), '[^0-9]', '', 'g'), '')::numeric
        WHEN salary_label ~ '^<\$[0-9,]+$' THEN
            NULLIF(regexp_replace(salary_label, '[^0-9]', '', 'g'), '')::numeric
        ELSE NULL
    END,

    description_clean,
    keywords,
    address_short,
    coordinates
FROM workforce_jobs_stage;


CREATE OR REPLACE FUNCTION parse_salary_amount(token TEXT)
RETURNS NUMERIC AS $$
    SELECT NULLIF(regexp_replace(token, '[^0-9.]', '', 'g'), '')::numeric
           * CASE WHEN token ILIKE '%k%' THEN 1000 ELSE 1 END
$$ LANGUAGE sql IMMUTABLE;

INSERT INTO jobs_unified (source, title, company, tenure_label, salary_period, salary_min, salary_max, description, keywords, address_short, coordinates)
SELECT
    'jooble',
    title_clean,
    company,
    NULL,
    CASE
        WHEN salary_label ILIKE '%per hour%'  THEN 'hourly'
        WHEN salary_label ILIKE '%per month%' THEN 'monthly'
        WHEN salary_label ~ '\$'              THEN 'yearly'
        ELSE NULL
    END,
    parse_salary_amount(split_part(regexp_replace(salary_label, '\s*per\s*(hour|month)', '', 'i'), '-', 1)),
    CASE
        WHEN salary_label ~ '-' THEN
            parse_salary_amount(split_part(regexp_replace(salary_label, '\s*per\s*(hour|month)', '', 'i'), '-', 2))
        ELSE
            parse_salary_amount(split_part(regexp_replace(salary_label, '\s*per\s*(hour|month)', '', 'i'), '-', 1))
    END,
    description_clean,
    keywords,
    NULL,
    NULL::geography(Point,4326)
FROM jooble_jobs_stage;
