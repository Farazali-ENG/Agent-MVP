from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore
import logging
import warnings

# Set up logging
logger = logging.getLogger(__name__)

# Global scheduler instance to ensure only one scheduler runs
scheduler = None


def start_scheduler():
    """
    Initializes and starts the BackgroundScheduler. Ensures it runs only once.
    """
    global scheduler

    if scheduler and scheduler.running:
        # Skip initialization if the scheduler is already running
        return

    try:
        scheduler = BackgroundScheduler()
        scheduler.add_jobstore(DjangoJobStore(), "default")

        # Schedule the daily email report
        _schedule_daily_email_report()

        # Start the scheduler
        scheduler.start()
    except Exception as e:
        logger.error(f"Error starting the scheduler: {e}")


def _schedule_daily_email_report():
    """
    Internal function to schedule the daily email report job.
    """
    try:
        from .daily_email_cron import daily_email_report  # Import here to avoid circular imports
        scheduler.add_job(
            daily_email_report,
            'cron',
            hour=20,  # 8 PM
            minute=0,
            id='daily_email_report',
            max_instances=1,
            replace_existing=True
        )
    except Exception as e:
        logger.error(f"Error scheduling daily email report job: {e}")

