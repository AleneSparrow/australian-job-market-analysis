# EDA Findings — Australian IT Labour Market Project

Рабочий журнал разведочного анализа (EDA). Формат: запрос → результат → вывод.
Обновляется по ходу анализа; финальные инсайты переносятся в README проекта.

---

## 1. Top Skills (по упоминаниям в вакансиях)

**Query:**
```sql
SELECT skill, COUNT(DISTINCT job_id) AS jobs_count
FROM job_skills
GROUP BY skill
ORDER BY jobs_count DESC
LIMIT 20;
```

**Result (top-10):**

| Skill | Jobs |
|---|---|
| aws | 526 |
| excel | 387 |
| azure | 333 |
| python | 127 |
| sql | 116 |
| spark | 109 |
| power_bi | 83 |
| linux | 80 |
| gcp | 77 |
| databricks | 56 |

**Insight:** AWS, Excel и Azure заметно опережают остальные навыки. Python и SQL — самые частые "чисто программистские" навыки, но встречаются на порядок реже облачных платформ и Excel. Даже топовый навык (AWS) фигурирует менее чем в 1% всех вакансий — явный признак того, что explicit skill-extraction ловит навыки только там, где они прямо упомянуты текстом, и не отражает полный технологический стек рынка.

---

## 2. Cloud Platforms

**Query:**
```sql
SELECT 
  SUM(CASE WHEN aws THEN 1 ELSE 0 END) AS aws_count,
  SUM(CASE WHEN azure THEN 1 ELSE 0 END) AS azure_count,
  SUM(CASE WHEN gcp THEN 1 ELSE 0 END) AS gcp_count
FROM jobs_features;
```

**Result:** AWS — 526, Azure — 333, GCP — 77.

**Insight:** AWS явно лидирует на австралийском рынке, GCP заметно отстаёт от двух других провайдеров.

---

## 3. Employment Type

**Query:**
```sql
SELECT 
  SUM(CASE WHEN full_time THEN 1 ELSE 0 END) AS full_time,
  SUM(CASE WHEN part_time THEN 1 ELSE 0 END) AS part_time,
  SUM(CASE WHEN contract THEN 1 ELSE 0 END) AS contract,
  SUM(CASE WHEN casual THEN 1 ELSE 0 END) AS casual
FROM jobs_features;
```

**Result:** full_time — 22,217, part_time — 6,859, contract — 6,113, casual — 4,786.

**Insight:** Full-time — доминирующий тип занятости среди вакансий, где тип вообще указан. При этом сумма всех категорий (~40K) заметно меньше общего числа вакансий (105,337) — у большей части поле не заполнено (нет явного маркера в тексте).

---

## 4. Visa Sponsorship

**Query:**
```sql
SELECT visa_sponsorship, COUNT(*)
FROM jobs_features
GROUP BY visa_sponsorship;
```

**Result:** без спонсорства — 104,909, со спонсорством — 428.

**Insight:** Только 0.4% вакансий (428 из 105,337) явно предлагают спонсорство визы — важный и лаконичный факт для раздела о доступности рынка труда для мигрантов.

---

## 5. Experience Level (после исправления бага в extraction-коде)

**Исходная проблема:** первая версия кода извлечения уровня опыта использовала независимые regex-паттерны (`senior`, `junior` и т.д.) без взаимного исключения. Из-за этого 510 вакансий получили противоречивую разметку — `senior = true AND junior = true` одновременно (например, из-за фраз вроде "junior to senior developers" в одном объявлении).

**Исправление:** добавлена единая колонка `experience_level` с приоритетом уровней (от старшего к младшему: staff → principal → lead → manager → senior → mid → junior → entry → graduate), плюс сужены паттерны `lead` и `principal`, чтобы не ловить посторонний контекст ("lead generation", "Principal House Officer").

**Query (после фикса):**
```sql
SELECT experience_level, COUNT(*)
FROM jobs_features
GROUP BY experience_level
ORDER BY COUNT(*) DESC;
```

**Result:**

| Level | Count |
|---|---|
| NULL (не определено) | 90,042 |
| senior | 10,736 |
| principal | 1,243 |
| graduate | 1,106 |
| junior | 889 |
| lead | 437 |
| mid | 384 |
| entry | 283 |
| manager | 244 |
| staff | 13 |

**Insight:** 85% вакансий не содержат явного маркера уровня опыта в заголовке/описании — типично для государственного портала вакансий (Workforce Australia), где формулировки менее формализованы, чем в IT-специфичных источниках. Среди вакансий с явным уровнем senior встречается почти в 12 раз чаще junior — вероятно, отражение специфики источника (много вакансий здравоохранения и госсектора), а не общей картины IT-рынка.

---

## 6. Data Quality: Salary Coverage

**Query:**
```sql
SELECT 
  COUNT(*) AS total_jobs,
  COUNT(salary_min) AS with_salary,
  ROUND(100.0 * COUNT(salary_min) / COUNT(*), 2) AS pct_with_salary
FROM jobs_unified;
```

**Result:** 105,337 вакансий всего, 1,628 с указанной зарплатой (**1.55%**).

**By source:**
```sql
SELECT 
  source,
  COUNT(*) AS total_jobs,
  COUNT(salary_min) AS with_salary,
  ROUND(100.0 * COUNT(salary_min) / COUNT(*), 2) AS pct_with_salary
FROM jobs_unified
GROUP BY source
ORDER BY total_jobs DESC;
```

| Source | Total jobs | With salary | % |
|---|---|---|---|
| workforce | 104,005 | 1,471 | 1.41% |
| adzuna | 996 | 120 | 12.05% |
| jooble | 336 | 37 | 11.01% |

**Insight (важное ограничение датасета):** анализ зарплат репрезентативен преимущественно для агрегаторов (Adzuna, Jooble), которые составляют менее 1.5% всего датасета, но содержат ~90% всех данных о зарплате. Основной источник (Workforce Australia, 98.7% датасета) почти никогда не указывает зарплату — типично для официальных государственных порталов вакансий. Любые выводы о "средней зарплате по рынку" нужно делать с этой оговоркой.

---

## Ещё не сделано (next steps)

- [ ] Топ вакансий по заголовкам (`title`)
- [ ] Топ работодателей по количеству вакансий
- [ ] Гео-разрез (штаты/города через `address_short`)
- [ ] Связка навыков с зарплатой (на ограниченной выборке ~1,628 вакансий)
