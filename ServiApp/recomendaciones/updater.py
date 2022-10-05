from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .jobs import schedule_api

def start():
	scheduler = BackgroundScheduler()
	scheduler.add_job(schedule_api, 'cron', hour=13, minute=48, timezone='America/Bogota')
	scheduler.start()
