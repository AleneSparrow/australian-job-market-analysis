ALTER TABLE jooble_jobs_stage
    ADD COLUMN IF NOT EXISTS description_clean TEXT;

UPDATE jooble_jobs_stage
SET description_clean = TRIM(
    regexp_replace(
        regexp_replace(
            regexp_replace(
                regexp_replace(description, '<[^>]+>', ' ', 'g'),   -- убрать HTML-теги (<b>, </b> и т.п.)
                '&nbsp;', ' ', 'g'                                   -- убрать &nbsp;
            ),
            '¶', ' ', 'g'                                           -- убрать символ параграфа
        ),
        '\s+', ' ', 'g'                                              -- схлопнуть повторяющиеся пробелы
    )
);
ALTER TABLE jooble_jobs_stage
    ADD COLUMN IF NOT EXISTS description_words TEXT;

UPDATE jooble_jobs_stage
SET description_words = TRIM(
    regexp_replace(
        regexp_replace(
            lower(description_clean),
            '[^a-z\s]', ' ', 'g'    -- оставить только буквы и пробелы, убрать цифры/пунктуацию
        ),
        '\s+', ' ', 'g'
    )
);

SELECT word, COUNT(*) AS freq
FROM jooble_jobs_stage,
     LATERAL regexp_split_to_table(description_words, '\s+') AS word
WHERE length(word) > 2   -- отсекаем однобуквенные/двухбуквенные мусорные токены
GROUP BY word
ORDER BY freq DESC
LIMIT 100;

ALTER TABLE jooble_jobs_stage
    ADD COLUMN IF NOT EXISTS description_tsv tsvector;

UPDATE jooble_jobs_stage
SET description_tsv = to_tsvector('english', description_clean);

SELECT word, ndoc, nentry
FROM ts_stat('SELECT description_tsv FROM jooble_jobs_stage')
ORDER BY nentry DESC
LIMIT 100;

ALTER TABLE jooble_jobs_stage
    ADD COLUMN IF NOT EXISTS keywords TEXT[];

WITH frequent_words AS (
    SELECT word
    FROM ts_stat('SELECT description_tsv FROM jooble_jobs_stage')
    WHERE nentry > 20
)
UPDATE jooble_jobs_stage j
SET keywords = (
    SELECT array_agg(DISTINCT lexeme)
    FROM unnest(j.description_tsv) AS lexeme
    WHERE lexeme IN (SELECT word FROM frequent_words)
);
