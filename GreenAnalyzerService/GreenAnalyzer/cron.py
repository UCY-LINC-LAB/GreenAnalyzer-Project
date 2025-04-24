# # GreenAnalyzer/cron.py

# from datetime import datetime

# def print_hw():
#     with open("services/cron_output.log", "a") as f:
#         f.write(f"[{datetime.now()}] Hello world!\n")


from django.conf import settings
import os
from datetime import datetime

def print_hw():
    # log_path = os.path.join(settings.BASE_DIR, "cron_output.log")
    log_path = 'GreenAnalyzer/cron_output.log'
    with open(log_path, "a") as f:
        f.write(f"[{datetime.now()}] Hello world!\n")

if __name__ == "__main__":
    print_hw()
