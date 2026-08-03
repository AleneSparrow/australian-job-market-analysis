DO $$
DECLARE
    col RECORD;
BEGIN
    FOR col IN 
        SELECT column_name
        FROM information_schema.columns
        WHERE table_name = 'workforce_jobs_stage'
          AND data_type IN ('text', 'character varying')
    LOOP
        EXECUTE format(
            'UPDATE workforce_jobs_stage 
             SET %I = COALESCE(NULLIF(TRIM(%I), ''''), ''Not specified'')',
            col.column_name, col.column_name
        );
    END LOOP;
END $$;
