"""Pandas / NumPy / Matplotlib logic. No database or Flask code here, so it is easy to test.

Rules (documented so calculations are reproducible):
* A student's score in a subject = mean of their marks across assessments (or the single
  assessment if one is selected).
* Total = sum of subject scores; Percentage = total / sum(max_marks) * 100.
* A student PASSES only if every subject score >= that subject's pass_marks.
* Grade by percentage: A+ >=90, A >=80, B >=70, C >=60, D >=50, E >=40, else F.
  A student who fails any subject receives grade F.
"""
import matplotlib

matplotlib.use("Agg")  # render to files, no display needed
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

GRADE_BANDS = [(90, "A+"), (80, "A"), (70, "B"), (60, "C"), (50, "D"), (40, "E")]


def grade_for(percentage):
    for cutoff, grade in GRADE_BANDS:
        if percentage >= cutoff:
            return grade
    return "F"


def subject_scores(df):
    """One row per student per subject."""
    keys = ["student_id", "roll_no", "name", "section",
            "subject_id", "subject_name", "max_marks", "pass_marks"]
    scores = df.groupby(keys, as_index=False)["marks_obtained"].mean()
    scores = scores.rename(columns={"marks_obtained": "score"})
    scores["passed"] = scores["score"] >= scores["pass_marks"]
    return scores


def student_report(df):
    scores = subject_scores(df)
    report = scores.groupby(["student_id", "roll_no", "name", "section"], as_index=False).agg(
        total=("score", "sum"),
        max_total=("max_marks", "sum"),
        subjects_taken=("subject_id", "count"),
        failed_subjects=("passed", lambda s: int((~s).sum())),
    )
    report["average"] = report["total"] / report["subjects_taken"]
    report["percentage"] = report["total"] / report["max_total"] * 100
    report["status"] = np.where(report["failed_subjects"] == 0, "Pass", "Fail")
    report["grade"] = [
        "F" if st == "Fail" else grade_for(p)
        for st, p in zip(report["status"], report["percentage"])
    ]
    report = report.sort_values("percentage", ascending=False).reset_index(drop=True)
    report["rank"] = report["percentage"].rank(method="min", ascending=False).astype(int)
    return report.round(2)


def subject_summary(df):
    scores = subject_scores(df)
    rows = []
    for (sid, name, max_marks), g in scores.groupby(["subject_id", "subject_name", "max_marks"]):
        vals = g["score"].to_numpy()
        rows.append({
            "subject_id": int(sid), "subject_name": name, "max_marks": float(max_marks),
            "students": int(len(vals)),
            "mean": float(np.mean(vals)), "median": float(np.median(vals)),
            "min": float(np.min(vals)), "max": float(np.max(vals)),
            "std_dev": float(np.std(vals)),
            "pass_percentage": float(g["passed"].mean() * 100),
        })
    return pd.DataFrame(rows).round(2)


def section_summary(df):
    report = student_report(df)
    out = report.groupby("section", as_index=False).agg(
        students=("student_id", "count"),
        mean_percentage=("percentage", "mean"),
        median_percentage=("percentage", "median"),
        highest=("percentage", "max"),
        lowest=("percentage", "min"),
        passed=("status", lambda s: int((s == "Pass").sum())),
    )
    out["pass_percentage"] = out["passed"] / out["students"] * 100
    return out.round(2)


def pass_fail_summary(df):
    report = student_report(df)
    total = len(report)
    passed = int((report["status"] == "Pass").sum())
    return {
        "total_students": total, "passed": passed, "failed": total - passed,
        "pass_percentage": round(passed / total * 100, 2) if total else 0.0,
        "grade_distribution": report["grade"].value_counts().to_dict(),
    }


def toppers(df, n=3):
    return student_report(df).head(n)


def low_performers(df, threshold):
    """Students whose percentage is below the threshold or who failed any subject."""
    report = student_report(df)
    return report[(report["percentage"] < threshold) | (report["status"] == "Fail")]


# ---------------------------------------------------------------- charts
def _finish(fig, path):
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    return path


def chart_subject_averages(df, path):
    summ = subject_summary(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(summ))
    ax.bar(x, summ["mean"], color="#4C78A8", label="Average marks")
    ax.plot(x, summ["max_marks"], "r--o", label="Maximum marks")
    ax.set_xticks(x)
    ax.set_xticklabels(summ["subject_name"], rotation=20, ha="right")
    ax.set_title("Subject-wise Average Marks")
    ax.set_xlabel("Subject")
    ax.set_ylabel("Marks")
    ax.legend()
    return _finish(fig, path)


def chart_pass_percentage(df, path):
    summ = subject_summary(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.bar(summ["subject_name"], summ["pass_percentage"], color="#54A24B", label="Pass percentage")
    ax.axhline(100, color="grey", linestyle=":", label="100%")
    ax.set_ylim(0, 110)
    ax.set_title("Subject-wise Pass Percentage")
    ax.set_xlabel("Subject")
    ax.set_ylabel("Students passed (%)")
    plt.setp(ax.get_xticklabels(), rotation=20, ha="right")
    ax.legend()
    return _finish(fig, path)


def chart_marks_distribution(df, path):
    report = student_report(df)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.hist(report["percentage"], bins=range(0, 110, 10), color="#F58518",
            edgecolor="black", label="Students")
    mean = report["percentage"].mean()
    ax.axvline(mean, color="red", linestyle="--", label=f"Mean = {mean:.1f}%")
    ax.set_title("Distribution of Overall Percentage")
    ax.set_xlabel("Overall percentage (%)")
    ax.set_ylabel("Number of students")
    ax.legend()
    return _finish(fig, path)
