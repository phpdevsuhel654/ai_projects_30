import re


ALLOWED_SCHEDULE_TYPES = {"hourly", "daily", "custom"}


def validate_schedule(schedule_type: str, schedule_expression: str | None) -> str | None:
    if schedule_type not in ALLOWED_SCHEDULE_TYPES:
        return "schedule_type must be one of: hourly, daily, custom"

    if schedule_type == "custom":
        if not schedule_expression:
            return "schedule_expression is required when schedule_type=custom"

        parts = re.split(r"\s+", schedule_expression.strip())
        if len(parts) != 5:
            return "schedule_expression must contain 5 cron parts"

    return None