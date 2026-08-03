import pandas as pd
from sqlalchemy import create_engine

DB_USER="postgres"
DB_PASSWORD="7851"
DB_HOST="localhost"
DB_PORT="5432"
DB_NAME="australian_job_market"

engine=create_engine(f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}")

df = pd.read_sql("SELECT * FROM jobs_unified", engine)

text = (
    df["title"].fillna("") + " " +
    df["description_clean"].fillna("")
).str.lower()

SKILLS={
"python":r"\bpython\b","sql":r"\bsql\b","excel":r"\bexcel\b","tableau":r"\btableau\b",
"power_bi":r"\bpower\s?bi\b","aws":r"\baws\b|amazon web services","azure":r"\bazure\b",
"gcp":r"\bgcp\b|google cloud","docker":r"\bdocker\b","kubernetes":r"\bkubernetes\b|\bk8s\b",
"git":r"\bgit\b","linux":r"\blinux\b","terraform":r"\bterraform\b","snowflake":r"\bsnowflake\b",
"databricks":r"\bdatabricks\b","spark":r"\bspark\b","pandas":r"\bpandas\b","numpy":r"\bnumpy\b",
"tensorflow":r"\btensorflow\b","pytorch":r"\bpytorch\b"}

EXPERIENCE_LEVELS={
"graduate":r"\bgraduate\b|\bgraduate program\b","entry":r"\bentry[- ]?level\b",
"junior":r"\bjunior\b|\bjr\b","mid":r"\bmid[- ]?level\b|\bintermediate\b",
"senior":r"\bsenior\b|\bsr\b","lead":r"\blead\b|\bteam lead\b|\btechnical lead\b",
"principal":r"\bprincipal\b","staff":r"\bstaff engineer\b",
"manager":r"\bmanager\b|\bengineering manager\b"}

df["remote_type"]="unknown"
df.loc[text.str.contains(r"hybrid|hybrid working|hybrid office",regex=True,na=False),"remote_type"]="hybrid"
df.loc[(df["remote_type"]=="unknown") & text.str.contains(r"remote|work from home|work-from-home|working from home|fully remote|remote role|work entirely remotely|\bwfh\b",regex=True,na=False),"remote_type"]="remote"
df.loc[(df["remote_type"]=="unknown") & text.str.contains(r"onsite|on-site|office based|office-based|in office|in-office",regex=True,na=False),"remote_type"]="onsite"

for s,p in SKILLS.items():
    df[s]=text.str.contains(p,regex=True,na=False)

for l,p in EXPERIENCE_LEVELS.items():
    df[l]=text.str.contains(p,regex=True,na=False)

feature_columns=["job_id","remote_type"]+list(SKILLS.keys())+list(EXPERIENCE_LEVELS.keys())
jobs_features=df[feature_columns].copy()

job_skills=[]
for s,p in SKILLS.items():
    for job_id in df.loc[text.str.contains(p,regex=True,na=False),"job_id"]:
        job_skills.append({"job_id":job_id,"skill":s})

pd.DataFrame(job_skills).to_sql("job_skills",engine,if_exists="replace",index=False)
jobs_features.to_sql("jobs_features",engine,if_exists="replace",index=False)

print("Done")