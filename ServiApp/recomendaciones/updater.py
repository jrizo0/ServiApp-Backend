from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_api, get_recomendaciones


def start_test():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        schedule_api, "cron", hour=15, minute=45, timezone="America/Bogota"
    )
    # scheduler.add_job(schedule_api, 'interval', seconds=5)
    scheduler.start()


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(
        get_recomendaciones, "cron", hour=00, minute=00, timezone="America/Bogota"
    )
    scheduler.start()
