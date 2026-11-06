🎓 Student Performance Analysis System

📌 Project Overview

The Student Performance Analysis System is a web-based application developed using Python, Flask, MySQL, Pandas, NumPy and Matplotlib.

This system helps educational institutions manage student records, analyze academic performance, calculate grades, identify low-performing students and generate graphical reports.

🎯 Objectives

- Maintain student academic records.
- Analyze subject-wise marks.
- Calculate total marks and percentages.
- Identify low-performing students.
- Generate performance charts.
- Support better academic decision-making.

✨ Features

- Student record management
- Subject management
- Marks entry and management
- Academic performance analysis
- Grade calculation
- Pass and fail identification
- Low performer detection
- Data visualization
- Database integration
- Input validation

🛠️ Technologies Used

Technology| Purpose
Python| Backend programming
Flask| Web framework
MySQL| Database
Pandas| Data analysis
NumPy| Numerical calculations
Matplotlib| Data visualization
Pytest| Testing

📂 Project Structure

Student-Performance-Analysis-System/
│
└── student_performance/
    ├── app.py
    ├── analysis.py
    ├── config.py
    ├── db.py
    ├── validators.py
    ├── seed.py
    ├── schema.sql
    ├── requirements.txt
    ├── .env.example
    ├── .gitignore
    ├── README.md
    │
    └── tests/
        └── test_analysis.py

⚙️ Installation and Setup

Step 1: Clone Repository

git clone https://github.com/swathisunkara542-blip/Student-Performance-Analysis-System.git

Step 2: Navigate to Project Folder

cd Student-Performance-Analysis-System/student_performance

Step 3: Install Dependencies

pip install -r requirements.txt

Step 4: Configure Database

- Install MySQL 8.0.16 or later.
- Create the database.
- Configure database credentials in the ".env" file.
- Use ".env.example" as a reference.

Step 5: Create Database Tables

mysql -u root -p < schema.sql

Step 6: Load Sample Data

python seed.py

Step 7: Run Application

python app.py

Application URL:

"http://127.0.0.1:5000"

📊 Calculation Rules

- Subject score is calculated using assessment marks.
- Total marks are calculated from subject scores.
- Percentage is calculated based on maximum marks.
- Students must meet subject pass marks to pass.
- Grades are assigned according to percentage.
- Marks outside the allowed range are rejected.

🔗 API Endpoints

Method| Endpoint| Purpose
GET/POST| "/students"| Add and list students
GET/PUT/DELETE| "/students/<id>"| Manage student records
GET/POST| "/subjects"| Add and list subjects
GET/POST| "/marks"| Add and list marks

🧪 Testing

Run the following command:

pytest

🔐 Security

- Database credentials are managed through environment variables.
- Sensitive files are excluded using ".gitignore".
- ".env.example" provides sample configuration.

🚀 Future Enhancements

- Interactive performance dashboard
- Student performance prediction
- Attendance analysis
- Automated report generation
- Advanced data visualization

👩‍💻 Author

Swathi

GitHub: https://github.com/swathisunkara542-blip

📝 Conclusion

The Student Performance Analysis System provides an efficient way to manage student records, evaluate academic results and visualize performance. It helps identify students who need additional academic support and promotes data-driven educational decisions.

---

⭐ If you like this project, please give it a star on GitHub!
