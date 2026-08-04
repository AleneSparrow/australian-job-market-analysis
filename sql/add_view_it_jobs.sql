CREATE VIEW it_jobs AS
SELECT ju.*
FROM jobs_unified ju
WHERE ju.job_id IN (SELECT DISTINCT job_id FROM job_skills)
   OR ju.title ILIKE ANY (ARRAY[
     '%software engineer%', '%data engineer%', '%devops engineer%',
     '%cloud engineer%', '%network engineer%', '%systems engineer%',
     '%qa engineer%', '%test engineer%', '%security engineer%',
     '%ml engineer%', '%machine learning engineer%', '%platform engineer%',
     '%site reliability engineer%', '%backend engineer%', '%frontend engineer%',
     '%full stack engineer%', '%developer%', '%data scientist%',
     '%data analyst%', '%software%', '%programmer%', '%solution architect%',
     '%database admin%', '%dba%', '%cyber%', '%web developer%'
   ]);
