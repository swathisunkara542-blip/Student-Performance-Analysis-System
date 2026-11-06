import os
import sys

import pandas as pd
import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
import analysis
from validators import ValidationError, validate_marks_value, validate_subject


def make_df():
    rows = []
    for sid, roll, name, math, sci in [(1, "R1", "A", 80, 60), (2, "R2", "B", 90, 30)]:
        for subj_id, subj, mark in [(1, "Math", math), (2, "Science", sci)]:
            rows.append(dict(student_id=sid, roll_no=roll, name=name, section="A",
                             subject_id=subj_id, subject_name=subj, max_marks=100,
                             pass_marks=40, assessment="Final", marks_obtained=mark))
    return pd.DataFrame(rows)


def test_grade_bands():
    assert analysis.grade_for(95) == "A+"
    assert analysis.grade_for(70) == "B"
    assert analysis.grade_for(39.99) == "F"


def test_student_report_values():
    rep = analysis.student_report(make_df()).set_index("roll_no")
    assert rep.loc["R1", "total"] == 140
    assert rep.loc["R1", "percentage"] == 70
    assert rep.loc["R1", "grade"] == "B" and rep.loc["R1", "status"] == "Pass"
    assert rep.loc["R2", "percentage"] == 60
    assert rep.loc["R2", "status"] == "Fail" and rep.loc["R2", "grade"] == "F"


def test_subject_summary():
    s = analysis.subject_summary(make_df()).set_index("subject_name")
    assert s.loc["Math", "mean"] == 85 and s.loc["Math", "pass_percentage"] == 100
    assert s.loc["Science", "mean"] == 45 and s.loc["Science", "pass_percentage"] == 50


def test_toppers_and_low_performers():
    assert analysis.toppers(make_df(), 1).iloc[0]["roll_no"] == "R1"
    low = analysis.low_performers(make_df(), 65)
    assert list(low["roll_no"]) == ["R2"]


def test_pass_fail_summary():
    s = analysis.pass_fail_summary(make_df())
    assert s["passed"] == 1 and s["failed"] == 1 and s["pass_percentage"] == 50


def test_invalid_marks_rejected():
    with pytest.raises(ValidationError):
        validate_marks_value(101, 100)
    with pytest.raises(ValidationError):
        validate_marks_value(-1, 100)
    with pytest.raises(ValidationError):
        validate_marks_value("abc", 100)
    assert validate_marks_value("75.5", 100) == 75.5


def test_subject_validation():
    with pytest.raises(ValidationError):
        validate_subject({"subject_name": "X", "max_marks": 50, "pass_marks": 60})


def test_charts_created(tmp_path):
    for fn in (analysis.chart_subject_averages, analysis.chart_pass_percentage,
               analysis.chart_marks_distribution):
        p = fn(make_df(), str(tmp_path / f"{fn.__name__}.png"))
        assert os.path.getsize(p) > 0
