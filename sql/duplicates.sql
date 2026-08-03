SELECT
    description_clean,
    COUNT(*) AS duplicates
FROM jobs_unified
GROUP BY description_clean
HAVING COUNT(*) > 1
ORDER BY duplicates DESC;

SELECT *
FROM jobs_unified
WHERE description_clean IN (
    SELECT description_clean
    FROM jobs_unified
    GROUP BY description_clean
    HAVING COUNT(*) > 1
)
ORDER BY description_clean;

DELETE FROM jobs_unified
WHERE ctid IN (
    SELECT ctid
    FROM (
        SELECT
            ctid,
            ROW_NUMBER() OVER (
                PARTITION BY description_clean
                ORDER BY ctid
            ) AS rn
        FROM jobs_unified
    ) t
    WHERE rn > 1
);
