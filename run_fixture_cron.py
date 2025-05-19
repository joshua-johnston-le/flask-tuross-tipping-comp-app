# run_fixtures_cron.py

from app import create_app, db
from app.services.fixtures import upsert_free_fixtures, update_user_tip_stats, find_current_round, get_free_nrl_fixtures
from datetime import datetime
import pytz
from app.models import FixtureFree, User, UserTipStats
import json

au_datetime = datetime.now(pytz.timezone("Australia/Sydney"))

def run():
    app = create_app()
    with app.app_context():
        curr_round = find_current_round()
        print(f"Initialising Cron Job at: {au_datetime}, for NRL ROUND: {curr_round}")
        print("Running cron job: upserting NRL fixtures...")
        upsert_free_fixtures()
        print("Fixtures updated, ✅.")
        print("Latest scores updated")
        fixtures = FixtureFree.query.filter_by(round=find_current_round()).all()
        for fixture in fixtures:
            print(f"{fixture.home_team} vs {fixture.away_team}: {fixture.home_score} - {fixture.away_score}")
        print("Updating tip results...")
        update_user_tip_stats()
        print("Scores updated, ✅.")
        print(f"Results for current round: {curr_round}")
        results = UserTipStats.query.filter_by(round_number=find_current_round()).all()
        for result in results:
            print(f"{result.user.username} got: {result.successful_tips}")
        print("Schema check! ✅")
        fixtures = get_free_nrl_fixtures()
        print(json.dumps(fixtures[0], indent=2))

if __name__ == "__main__":
    run()
