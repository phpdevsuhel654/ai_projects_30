from app.models import CronJob
from app.repositories.cron_repository import CronRepository
from app.scheduler.job_scheduler import job_scheduler
from app.utils.extensions import db


class CronService:
    @staticmethod
    def create(data: dict) -> CronJob:
        cron_job = CronJob(
            name=data["name"],
            url=data["url"],
            execution_count=data.get("execution_count", 1),
            schedule_type=data.get("schedule_type", "daily"),
            schedule_expression=data.get("schedule_expression"),
            is_active=data.get("is_active", True),
            description=data.get("description"),
        )
        created = CronRepository.create(cron_job)
        job_scheduler.schedule_job(created.id)
        return created

    @staticmethod
    def list_all() -> list[CronJob]:
        return CronRepository.list_all()

    @staticmethod
    def get(cron_id: int) -> CronJob | None:
        return CronRepository.get_by_id(cron_id)

    @staticmethod
    def update(cron_id: int, data: dict) -> CronJob | None:
        cron_job = CronRepository.get_by_id(cron_id)
        if not cron_job:
            return None

        if "name" in data:
            cron_job.name = data["name"]
        if "url" in data:
            cron_job.url = data["url"]
        if "execution_count" in data:
            cron_job.execution_count = data["execution_count"]
        if "schedule_type" in data:
            cron_job.schedule_type = data["schedule_type"]
        if "schedule_expression" in data:
            cron_job.schedule_expression = data["schedule_expression"]
        if "is_active" in data:
            cron_job.is_active = data["is_active"]
        if "description" in data:
            cron_job.description = data["description"]

        db.session.commit()
        job_scheduler.schedule_job(cron_job.id)
        return cron_job

    @staticmethod
    def delete(cron_id: int) -> bool:
        cron_job = CronRepository.get_by_id(cron_id)
        if not cron_job:
            return False

        job_id = cron_job.id
        CronRepository.delete(cron_job)
        job_scheduler.remove_job(job_id)
        return True
