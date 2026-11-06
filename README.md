Student Performance Analysis System

A beginner-friendly Flask + MySQL project for maintaining student profiles, subjects and marks, then analysing academic performance using Pandas, NumPy and Matplotlib.

1. Requirements

- Python 3.10 or newer
- Visual Studio Code
- MySQL Server
- MySQL Workbench (or another MySQL client)

2. Open Project in VS Code

1. Extract the ZIP file.
2. Open Visual Studio Code.
3. Select File → Open Folder.
4. Select "student_performance_analysis_system".
5. Open Terminal → New Terminal.

3. Create Virtual Environment and Install Packages

Windows:

py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

If PowerShell blocks activation, run:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate

4. Create MySQL Database

1. Start MySQL Server.
2. Open MySQL Workbench.
3. Connect to your local MySQL server.
4. Open "schema.sql".
5. Click the Execute button (lightning bolt).

This creates the database, three tables and five sample subjects.

5. Configure Database Connection

1. Copy ".env.example".
2. Rename the copied file to ".env".
3. Open ".env".
4. Set "DB_USER" and "DB_PASSWORD" to your local MySQL username and password.
5. Keep "DB_NAME=student_performance_db".

Never upload ".env" or share your database password.

6. Add Sample Data

Run the following command in the VS Code terminal:

python seed.py

This inserts synthetic sample students and marks. It is safe to run again.

7. Run the Application

Execute:

python app.py

Open the local address printed in the terminal, usually:

"http://127.0.0.1:5000"

8. Main Pages

Page| Description
"/"| Dashboard
"/students"| Add, view, update and delete students
"/subjects"| View and add subjects
"/marks"| Enter and delete marks
"/reports"| Student and subject analysis reports
"/api/health"| Database health check
"/api/students"| GET and POST student API
"/api/summary"| Dashboard summary JSON

9. Analysis Rules Used

- Assessment percentage = (Marks Obtained / Maximum Marks) × 100.
- A mark record passes when marks obtained are greater than or equal to that subject's pass marks.
- Student average percentage = Mean of the student's recorded assessment percentages.
- Dashboard class average = Mean of student average percentages.

Grade Calculation

Grade| Percentage
A+| 90 and above
A| 80–89
B| 70–79
C| 60–69
D| 40–59
F| Below 40

- "Needs support" is a project reporting flag for average percentage below 40. It is not a permanent label about a student.
- Subject charts normalize average marks as a percentage of each subject's maximum marks for fair comparison.

10. Charts and Data Visualization

Dashboard and report charts are interactive Chart.js visualizations built from current MySQL assessment records.

Dashboard Charts

- Average percentage by subject.
- Pass/fail totals.
- Average percentage by student.

Reports Charts

- Subject average and pass-rate comparison.
- Student average comparison.
- Grade distribution.

Chart.js is loaded from its CDN, so the browser needs an internet connection to render interactive charts.

11. Troubleshooting

Problem| Solution
Access denied| Check DB_USER and DB_PASSWORD in ".env".
Unknown database| Execute "schema.sql" in MySQL Workbench.
Can't connect| Make sure MySQL Server is running and DB_HOST/DB_PORT are correct.
No module named ...| Activate ".venv" and run "pip install -r requirements.txt".

12. Limitations

- This is an educational mini project using synthetic sample data.
- It has no login or role management system.
- It is not an official institutional grading platform.
- The current student summary averages recorded assessment percentages; it does not assume unrecorded assessments are zero.
