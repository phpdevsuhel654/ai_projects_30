from app import create_app
from app.models import CronJob
from app.utils.extensions import db


SAMPLE_DATA = [
    {
        "name": "Archive Return Order Logs",
        "url": "https://web7.omnirps.com/cron/cron_delete_and_archive_log_table_data/return_order",
        "execution_count": 5,
        "schedule_type": "daily",
        "is_active": True,
        "description": "Archives return_order logs daily.",
    },
    {
        "name": "Delayed Label Check",
        "url": "https://web7.omnirps.com/cron/cron_get_delayed_label",
        "execution_count": 1,
        "schedule_type": "hourly",
        "is_active": True,
        "description": "Checks delayed labels every hour.",
    },
]


def run() -> None:
    app = create_app()
    with app.app_context():
        for item in SAMPLE_DATA:
            exists = CronJob.query.filter_by(name=item["name"], url=item["url"]).first()
            if not exists:
                db.session.add(CronJob(**item))

        db.session.commit()


if __name__ == "__main__":
    run()
