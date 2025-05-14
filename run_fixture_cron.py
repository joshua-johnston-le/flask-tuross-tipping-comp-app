# run_fixtures_cron.py

from app import create_app, db
from app.services.fixtures import upsert_free_fixtures, update_user_tip_stats
from datetime import datetime
import pytz

au_datetime = datetime.now(pytz.timezone("Australia/Sydney"))

def run():
    app = create_app()
    with app.app_context():
        print(f"Initialising Cron Job at: {au_datetime}")
        print("Running cron job: upserting NRL fixtures...")
        upsert_free_fixtures()
        print("Done.")
        print("Running cron job: updating tip results...")
        update_user_tip_stats()
        print("Done.")

if __name__ == "__main__":
    run()
