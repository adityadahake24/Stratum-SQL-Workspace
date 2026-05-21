from celery.schedules import crontab
from app.workers.celery_app import celery_app

celery_app.conf.beat_schedule = {
    "cleanup-snapshots": {
        "task": "app.workers.tasks.cleanup_tasks.cleanup_expired_snapshots",
        "schedule": crontab(minute="*/15"),
    },
    "cleanup-sessions": {
        "task": "app.workers.tasks.cleanup_tasks.cleanup_stale_sessions",
        "schedule": crontab(hour="*/2", minute=0),
    },
    "cleanup-pools": {
        "task": "app.workers.tasks.cleanup_tasks.cleanup_idle_connection_pools",
        "schedule": crontab(minute="*/5"),
    },
    "cleanup-tokens": {
        "task": "app.workers.tasks.cleanup_tasks.cleanup_expired_tokens",
        "schedule": crontab(minute="*/10"),
    },
}
