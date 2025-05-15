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
