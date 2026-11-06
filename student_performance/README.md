# Student Performance Analysis System (Flask + MySQL + Pandas + NumPy + Matplotlib)

## Setup
1. Install Python 3.10+ and MySQL 8.0.16+ (needed for CHECK constraints).
2. `pip install -r requirements.txt`
3. Create the tables: `mysql -u root -p < schema.sql`
4. Copy `.env.example` to `.env` and put in your MySQL password. Never commit `.env`.
5. (Optional) load sample data: `python seed.py`
6. Run the API: `python app.py` (http://127.0.0.1:5000)
7. Run tests (no database needed): `pytest`

## Calculation rules
- Subject score = mean of that student's marks over assessments (filter with `?assessment=Final`).
- Total = sum of subject scores; Percentage = total / sum of max marks x 100.
- Pass only if every subject score >= its pass marks.
- Grade: A+ >= 90, A >= 80, B >= 70, C >= 60, D >= 50, E >= 40, otherwise F. Failing any subject gives F.
- Marks outside 0..max_marks are rejected (HTTP 400).

## Endpoints
| Method | URL | Purpose |
|---|---|---|
| POST/GET | /students | add / list (`?section=A`) |
| GET/PUT/DELETE | /students/<id> | view (with marks) / update / delete |
| POST/GET | /subjects | add / list |
| POST/GET | /marks | add / list (`?student_id=&subject_id=&assessment=`) |
| PUT/DELETE | /marks/<id> | update / delete marks |
| GET | /reports/students | total, average, percentage, grade, status, rank |
| GET | /reports/subjects | mean, median, min, max, std dev, pass % per subject |
| GET | /reports/sections | section-wise summary |
| GET | /reports/pass-fail | pass/fail counts and grade distribution |
| GET | /reports/toppers?n=3 | top students |
| GET | /reports/low-performers?threshold=40 | below threshold or failed a subject |
| GET | /charts/subject-averages, /charts/pass-percentage, /charts/marks-distribution | PNG charts (also saved in `charts/`) |

## Example requests
```
curl -X POST localhost:5000/students -H "Content-Type: application/json" -d '{"roll_no":"R101","name":"Asha","section":"A"}'
curl -X POST localhost:5000/subjects -H "Content-Type: application/json" -d '{"subject_name":"Maths","max_marks":100,"pass_marks":40}'
curl -X POST localhost:5000/marks -H "Content-Type: application/json" -d '{"student_id":1,"subject_id":1,"assessment":"Final","marks_obtained":78}'
curl localhost:5000/reports/toppers?n=5
curl localhost:5000/charts/subject-averages --output subject_averages.png
```
Invalid example: `marks_obtained: 150` for a 100-mark subject returns `400 {"error": "'marks_obtained' must be between 0 and 100."}`.

## Project layout
`app.py` routes and error handling | `analysis.py` Pandas/NumPy/Matplotlib | `db.py` parameterized SQL helper |
`validators.py` input checks | `config.py` env-based settings | `schema.sql` tables | `seed.py` sample data | `tests/`
