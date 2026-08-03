UPDATE jobs_unified j
SET coordinates = c.coordinates
FROM (
    SELECT DISTINCT ON (address_short)
           address_short,
           coordinates
    FROM jobs_unified
    WHERE coordinates IS NOT NULL
      AND address_short IS NOT NULL
    ORDER BY address_short
) c
WHERE j.coordinates IS NULL
  AND j.address_short = c.address_short;
