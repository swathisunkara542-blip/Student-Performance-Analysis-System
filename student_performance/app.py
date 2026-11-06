"""Student Performance Analysis System - Flask REST API."""
import os

import pandas as pd
from flask import Flask, jsonify, request, send_file
from mysql.connector import Error as MySQLError
from mysql.connector.errors import IntegrityError
from werkzeug.exceptions import HTTPException, NotFound

import analysis
import db
from config import Config
from validators import (ValidationError, require, to_number, validate_marks_value,
                        validate_student, validate_subject)

MARKS_SQL = """
    SELECT s.student_id, s.roll_no, s.name, s.section,
           sub.subject_id, sub.subject_name, sub.max_marks, sub.pass_marks,
           m.assessment, m.marks_obtained
    FROM marks m
    JOIN students s   ON s.student_id = m.student_id
    JOIN subjects sub ON sub.subject_id = m.subject_id
"""


def load_marks_df(assessment=None):
    sql, params = MARKS_SQL, ()
    if assessment:
        sql += " WHERE m.assessment = %s"
        params = (assessment,)
    rows = db.query(sql, params)
    if not rows:
        raise NotFound("No marks recorded yet" + (f" for assessment '{assessment}'." if assessment else "."))
    return pd.DataFrame(rows)


def records(df):
    return df.to_dict(orient="records")


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_object(Config)
    if config:
        app.config.update(config)
    os.makedirs(app.config["CHART_DIR"], exist_ok=True)

    # ------------------------------------------------------ error handling
    @app.errorhandler(ValidationError)
    def on_validation(e):
        return jsonify(error=str(e)), 400

    @app.errorhandler(IntegrityError)
    def on_integrity(e):
        msg = "Duplicate entry." if e.errno == 1062 else "Related record does not exist or is still in use."
        return jsonify(error=msg), 409

    @app.errorhandler(MySQLError)
    def on_mysql(e):
        app.logger.exception("Database error")
        return jsonify(error="Database error. Check the server logs and DB settings."), 500

    @app.errorhandler(HTTPException)
    def on_http(e):
        return jsonify(error=e.description), e.code

    @app.errorhandler(Exception)
    def on_unexpected(e):
        app.logger.exception("Unexpected error")
        return jsonify(error="Internal server error."), 500

    @app.get("/")
    def index():
        return jsonify(service="Student Performance Analysis System", status="ok")

    # ------------------------------------------------------------ students
    @app.post("/students")
    def add_student():
        data = validate_student(request.get_json(silent=True))
        new_id, _ = db.execute(
            "INSERT INTO students (roll_no, name, section) VALUES (%s, %s, %s)",
            (data["roll_no"], data["name"], data["section"]))
        return jsonify(student_id=new_id, **data), 201

    @app.get("/students")
    def list_students():
        section = request.args.get("section")
        if section:
            rows = db.query("SELECT * FROM students WHERE section = %s ORDER BY roll_no", (section,))
        else:
            rows = db.query("SELECT * FROM students ORDER BY roll_no")
        return jsonify(rows)

    @app.get("/students/<int:student_id>")
    def get_student(student_id):
        student = db.query_one("SELECT * FROM students WHERE student_id = %s", (student_id,))
        if not student:
            raise NotFound("Student not found.")
        student["marks"] = db.query(
            """SELECT m.mark_id, sub.subject_name, m.assessment, m.marks_obtained, sub.max_marks
               FROM marks m JOIN subjects sub ON sub.subject_id = m.subject_id
               WHERE m.student_id = %s ORDER BY sub.subject_name, m.assessment""", (student_id,))
        return jsonify(student)

    @app.put("/students/<int:student_id>")
    def update_student(student_id):
        data = validate_student(request.get_json(silent=True) or {}, partial=True)
        if not data:
            raise ValidationError("Provide at least one of: roll_no, name, section.")
        sets = ", ".join(f"{col} = %s" for col in data)  # column names come from a fixed whitelist
        _, count = db.execute(f"UPDATE students SET {sets} WHERE student_id = %s",
                              (*data.values(), student_id))
        if not count and not db.query_one("SELECT 1 AS x FROM students WHERE student_id = %s", (student_id,)):
            raise NotFound("Student not found.")
        return jsonify(message="Student updated.")

    @app.delete("/students/<int:student_id>")
    def delete_student(student_id):
        _, count = db.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        if not count:
            raise NotFound("Student not found.")
        return jsonify(message="Student and their marks deleted.")

    # ------------------------------------------------------------ subjects
    @app.post("/subjects")
    def add_subject():
        data = validate_subject(request.get_json(silent=True))
        new_id, _ = db.execute(
            "INSERT INTO subjects (subject_name, max_marks, pass_marks) VALUES (%s, %s, %s)",
            (data["subject_name"], data["max_marks"], data["pass_marks"]))
        return jsonify(subject_id=new_id, **data), 201

    @app.get("/subjects")
    def list_subjects():
        return jsonify(db.query("SELECT * FROM subjects ORDER BY subject_name"))

    # --------------------------------------------------------------- marks
    @app.post("/marks")
    def add_marks():
        data = request.get_json(silent=True)
        require(data, ["student_id", "subject_id", "assessment", "marks_obtained"])
        subject = db.query_one("SELECT max_marks FROM subjects WHERE subject_id = %s", (data["subject_id"],))
        if not subject:
            raise NotFound("Subject not found.")
        if not db.query_one("SELECT 1 AS x FROM students WHERE student_id = %s", (data["student_id"],)):
            raise NotFound("Student not found.")
        marks = validate_marks_value(data["marks_obtained"], subject["max_marks"])
        new_id, _ = db.execute(
            "INSERT INTO marks (student_id, subject_id, assessment, marks_obtained) VALUES (%s, %s, %s, %s)",
            (data["student_id"], data["subject_id"], str(data["assessment"]).strip(), marks))
        return jsonify(mark_id=new_id, marks_obtained=marks), 201

    @app.get("/marks")
    def list_marks():
        sql = ("SELECT m.mark_id, m.student_id, m.subject_id, m.assessment, m.marks_obtained "
               "FROM marks m WHERE 1=1")
        params = []
        for arg in ("student_id", "subject_id", "assessment"):
            if request.args.get(arg):
                sql += f" AND m.{arg} = %s"
                params.append(request.args[arg])
        return jsonify(db.query(sql + " ORDER BY m.mark_id", params))

    @app.put("/marks/<int:mark_id>")
    def update_marks(mark_id):
        data = request.get_json(silent=True)
        require(data, ["marks_obtained"])
        row = db.query_one(
            """SELECT sub.max_marks FROM marks m JOIN subjects sub ON sub.subject_id = m.subject_id
               WHERE m.mark_id = %s""", (mark_id,))
        if not row:
            raise NotFound("Mark record not found.")
        marks = validate_marks_value(data["marks_obtained"], row["max_marks"])
        db.execute("UPDATE marks SET marks_obtained = %s WHERE mark_id = %s", (marks, mark_id))
        return jsonify(message="Marks updated.", marks_obtained=marks)

    @app.delete("/marks/<int:mark_id>")
    def delete_marks(mark_id):
        _, count = db.execute("DELETE FROM marks WHERE mark_id = %s", (mark_id,))
        if not count:
            raise NotFound("Mark record not found.")
        return jsonify(message="Mark record deleted.")

    # ------------------------------------------------------------- reports
    def assessment_arg():
        return request.args.get("assessment")

    @app.get("/reports/students")
    def report_students():
        df = analysis.student_report(load_marks_df(assessment_arg()))
        section = request.args.get("section")
        if section:
            df = df[df["section"] == section]
        return jsonify(records(df))

    @app.get("/reports/subjects")
    def report_subjects():
        return jsonify(records(analysis.subject_summary(load_marks_df(assessment_arg()))))

    @app.get("/reports/sections")
    def report_sections():
        return jsonify(records(analysis.section_summary(load_marks_df(assessment_arg()))))

    @app.get("/reports/pass-fail")
    def report_pass_fail():
        return jsonify(analysis.pass_fail_summary(load_marks_df(assessment_arg())))

    @app.get("/reports/toppers")
    def report_toppers():
        n = int(to_number(request.args.get("n", 3), "n"))
        if n < 1:
            raise ValidationError("'n' must be at least 1.")
        return jsonify(records(analysis.toppers(load_marks_df(assessment_arg()), n)))

    @app.get("/reports/low-performers")
    def report_low():
        threshold = to_number(request.args.get("threshold", app.config["LOW_PERFORMER_THRESHOLD"]), "threshold")
        if not 0 <= threshold <= 100:
            raise ValidationError("'threshold' must be between 0 and 100.")
        df = analysis.low_performers(load_marks_df(assessment_arg()), threshold)
        return jsonify(threshold=threshold, students=records(df))

    # -------------------------------------------------------------- charts
    charts = {
        "subject-averages": analysis.chart_subject_averages,
        "pass-percentage": analysis.chart_pass_percentage,
        "marks-distribution": analysis.chart_marks_distribution,
    }

    @app.get("/charts/<name>")
    def chart(name):
        if name not in charts:
            raise NotFound(f"Unknown chart. Choose one of: {', '.join(charts)}")
        path = os.path.join(app.config["CHART_DIR"], f"{name}.png")
        charts[name](load_marks_df(assessment_arg()), path)
        return send_file(os.path.abspath(path), mimetype="image/png")

    return app


if __name__ == "__main__":
    create_app().run(debug=True)
