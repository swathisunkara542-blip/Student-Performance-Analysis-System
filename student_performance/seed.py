"""Load sample data: python seed.py   (run schema.sql first)."""
import mysql.connector
import numpy as np

from config import Config


def main():
    conn = mysql.connector.connect(host=Config.DB_HOST, port=Config.DB_PORT, user=Config.DB_USER,
                                   password=Config.DB_PASSWORD, database=Config.DB_NAME)
    cur = conn.cursor()
    rng = np.random.default_rng(42)

    subjects = [("Mathematics", 100, 40), ("Physics", 100, 40), ("Chemistry", 100, 40),
                ("English", 100, 35), ("Computer Science", 100, 40)]
    for s in subjects:
        cur.execute("INSERT IGNORE INTO subjects (subject_name, max_marks, pass_marks) VALUES (%s,%s,%s)", s)

    names = ["Asha", "Ravi", "Meena", "Kiran", "Sneha", "Arjun", "Divya", "Karthik", "Lakshmi", "Suresh",
             "Priya", "Naveen", "Anitha", "Vijay", "Harini", "Teja", "Bhavya", "Charan", "Pooja", "Sai"]
    for i, name in enumerate(names, start=1):
        cur.execute("INSERT IGNORE INTO students (roll_no, name, section) VALUES (%s,%s,%s)",
                    (f"R{i:03d}", name, "A" if i <= 10 else "B"))

    cur.execute("SELECT student_id FROM students")
    student_ids = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT subject_id, max_marks FROM subjects")
    subject_rows = cur.fetchall()

    for sid in student_ids:
        ability = rng.normal(62, 15)  # each student has an overall ability level
        for subj_id, max_marks in subject_rows:
            marks = float(np.clip(rng.normal(ability, 10), 0, max_marks).round(1))
            cur.execute("INSERT IGNORE INTO marks (student_id, subject_id, assessment, marks_obtained) "
                        "VALUES (%s,%s,'Final',%s)", (sid, subj_id, marks))
    conn.commit()
    conn.close()
    print("Sample data loaded.")


if __name__ == "__main__":
    main()
