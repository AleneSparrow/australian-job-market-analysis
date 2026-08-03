ALTER TABLE workforce_jobs_stage
    ADD COLUMN IF NOT EXISTS address_short TEXT;

UPDATE workforce_jobs_stage
SET address_short = 
    CASE
        WHEN suburb IS NOT NULL 
             AND suburb <> 'Not specified' 
             AND state IS NOT NULL 
             AND state <> 'Not specified'
            THEN INITCAP(suburb) || ', ' || state

        WHEN location_label IS NOT NULL 
             AND location_label <> 'Not specified'
            THEN TRIM(split_part(location_label, '-', 1)) || ' - ' || TRIM(split_part(location_label, '-', 2))

        ELSE 'Not specified'
    END;
