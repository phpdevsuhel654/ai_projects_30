from app.models import CronJob
from app.utils.extensions import db


class CronRepository:
    @staticmethod
    def create(job: CronJob) -> CronJob:
        db.session.add(job)
        db.session.commit()
        return job

    @staticmethod
    def list_all() -> list[CronJob]:
        return CronJob.query.order_by(CronJob.id.desc()).all()

    @staticmethod
    def list_active() -> list[CronJob]:
        return CronJob.query.filter_by(is_active=True).order_by(CronJob.id.desc()).all()

    @staticmethod
    def get_by_id(cron_id: int) -> CronJob | None:
        return db.session.get(CronJob, cron_id)

    @staticmethod
    def delete(job: CronJob) -> None:
        db.session.delete(job)
        db.session.commit()
