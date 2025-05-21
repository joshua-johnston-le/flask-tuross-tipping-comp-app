import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from app.models import Fixture, FixtureFree, db, User, UserTipStats, Tip
from app import create_app, db
from datetime import datetime, date, timedelta
import pytz

def get_user_rank(user_id):
    # Fetch leaderboard data: user_id and total successful tips
    leaderboard_data = (
        db.session.query(
            User.id.label("user_id"),
            db.func.sum(UserTipStats.successful_tips).label("total_success")
        )
        .join(User, User.id == UserTipStats.user_id)
        .group_by(User.id)
        .order_by(db.desc("total_success"))
        .all()
    )

    # Iterate through sorted leaderboard to find rank
    for idx, row in enumerate(leaderboard_data, start=1):
        if row.user_id == user_id:
            return idx  # Rank starts at 1

    return None

def has_user_submitted_tips(user_id):
    pass

def get_all_rounds():
    rounds = db.session.query(FixtureFree.round).distinct().order_by(FixtureFree.round).all()
    return [r[0] for r in rounds]


def is_past_thursday_5pm_aus():
    # Set timezone to Australia/Sydney
    aus_tz = pytz.timezone('Australia/Sydney')
    now = datetime.now(aus_tz)

    # Get this week's Thursday
    # weekday(): Monday=0, ..., Sunday=6 → Thursday = 3
    days_since_thursday = (now.weekday() - 3) % 7
    this_thursday = now - timedelta(days=days_since_thursday)
    thursday_5pm = this_thursday.replace(hour=17, minute=0, second=0, microsecond=0)

    # Return True if it's now Thursday 5pm or later
    return now >= thursday_5pm
