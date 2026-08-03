ALTER TABLE adzuna_jobs_stage
    ADD COLUMN IF NOT EXISTS title_clean TEXT;
UPDATE adzuna_jobs_stage
SET title_clean = TRIM(
    regexp_replace(
        regexp_replace(
            regexp_replace(
                title,
                '\s*\([^)]*\)', '', 'g'                          -- убрать всё в скобках, напр. (R, Python)
            ),
            '\s*[-–|/].*$', '', 'g'                               -- убрать всё после дефиса/тире/слэша/палки
        ),
        '\y(wanted|urgent|urgently hiring|hiring now|full[- ]time|part[- ]time|permanent|contract|casual|immediate start|apply now|new|exciting opportunity)\y',
        '', 'gi'
    )
);

-- финальная зачистка пробелов и пунктуации по краям
UPDATE adzuna_jobs_stage
SET title_clean = TRIM(both ' ,.-' from regexp_replace(title_clean, '\s+', ' ', 'g'));

SELECT word, COUNT(*) AS freq
FROM adzuna_jobs_stage,
     LATERAL regexp_split_to_table(
         regexp_replace(title, '[^a-zA-Z0-9\s]', ' ', 'g'),  -- убрать пунктуацию, оставить буквы/цифры
         '\s+'
     ) AS word
WHERE word <> ''
GROUP BY word
ORDER BY freq DESC
LIMIT 100;

UPDATE adzuna_jobs_stage
SET title_clean = 
    CASE
        -- Случай 1: роль в начале ("Head of...", "Chief...", "VP of...")
        WHEN title ~* '^\y(Head|Chief|VP|President|Director)\y\s+of\s+.+'
            THEN TRIM(regexp_replace(title, '\s*[-–|].*$', ''))  -- обрезаем только по дефису/палке, начало не трогаем
        
        -- Случай 2: роль в конце (обычный порядок слов)
        WHEN title ~* '\y(Analyst|Manager|Engineer|Consultant|Developer|Scientist|Director|Officer|Specialist|Coordinator|Executive|Administrator|Architect|Assistant|Advisor|Planner|Lead|Associate|Surveyor|Owner|Recruiter|Representative|Supervisor|Technician|Auditor|Strategist|Programmer|Trader|Practitioner|Superintendent|Controller|Clerk|Master|Geologist|Designer|Modeller|President|Partner|Tester|Reporter)s?\y'
            THEN TRIM(
                substring(
                    title FROM '^.*\y(?:Analyst|Manager|Engineer|Consultant|Developer|Scientist|Director|Officer|Specialist|Coordinator|Executive|Administrator|Architect|Assistant|Advisor|Planner|Lead|Associate|Surveyor|Owner|Recruiter|Representative|Supervisor|Technician|Auditor|Strategist|Programmer|Trader|Practitioner|Superintendent|Controller|Clerk|Master|Geologist|Designer|Modeller|President|Partner|Tester|Reporter)s?\y'
                )
            )
        
        ELSE title_clean  -- не трогаем то, что не подошло ни под одно правило
    END;


SELECT DISTINCT title
FROM adzuna_jobs_stage
WHERE title_clean IS NULL
LIMIT 50;
