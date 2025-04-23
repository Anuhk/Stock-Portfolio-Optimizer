# stockapp/tasks.py
from background_task import background
from django.core.management import call_command


@background(schedule=60)  # Schedule to run after 60 seconds (can adjust timing)
def fetch_stock_data_task():
    call_command('auto_add_stocks')


