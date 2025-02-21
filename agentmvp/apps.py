import os
from django.apps import AppConfig


class AgentMVPConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'agentmvp'

    def ready(self):
        # Start the scheduler only in the main process
        if os.environ.get("RUN_MAIN") == "true":
            from .scheduler import start_scheduler
            start_scheduler()
