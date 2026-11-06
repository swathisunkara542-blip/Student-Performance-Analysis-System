"""Input validation. Raises ValidationError, which the Flask app turns into HTTP 400."""


class ValidationError(Exception):
    pass


def require(data, fields):
    if not isinstance(data, dict):
        raise ValidationError("Request body must be a JSON object.")
    missing = [f for f in fields if data.get(f) in (None, "")]
    if missing:
        raise ValidationError(f"Missing required field(s): {', '.join(missing)}")


def to_number(value, field):
    try:
        if isinstance(value, bool):
            raise ValueError
        return float(value)
    except (TypeError, ValueError):
        raise ValidationError(f"'{field}' must be a number.")


def clean_text(value, field, max_len):
    text = str(value).strip()
    if not text:
        raise ValidationError(f"'{field}' cannot be empty.")
    if len(text) > max_len:
        raise ValidationError(f"'{field}' must be at most {max_len} characters.")
    return text


def validate_student(data, partial=False):
    if not partial:
        require(data, ["roll_no", "name", "section"])
    out = {}
    for field, limit in (("roll_no", 20), ("name", 100), ("section", 10)):
        if field in data:
            out[field] = clean_text(data[field], field, limit)
    return out


def validate_subject(data):
    require(data, ["subject_name", "max_marks", "pass_marks"])
    name = clean_text(data["subject_name"], "subject_name", 100)
    max_marks = to_number(data["max_marks"], "max_marks")
    pass_marks = to_number(data["pass_marks"], "pass_marks")
    if max_marks <= 0:
        raise ValidationError("'max_marks' must be greater than 0.")
    if not 0 <= pass_marks <= max_marks:
        raise ValidationError("'pass_marks' must be between 0 and max_marks.")
    return {"subject_name": name, "max_marks": max_marks, "pass_marks": pass_marks}


def validate_marks_value(value, max_marks):
    """Reject marks outside 0..max_marks."""
    marks = to_number(value, "marks_obtained")
    if not 0 <= marks <= max_marks:
        raise ValidationError(f"'marks_obtained' must be between 0 and {max_marks:g}.")
    return marks
