ALTER TABLE workforce_jobs_stage
    ADD COLUMN IF NOT EXISTS coordinates GEOGRAPHY(POINT, 4326);

UPDATE workforce_jobs_stage
SET coordinates = 
    CASE 
        WHEN lat IS NOT NULL AND long IS NOT NULL 
        THEN ST_SetSRID(ST_MakePoint(long, lat), 4326)::GEOGRAPHY
        ELSE NULL
    END;
