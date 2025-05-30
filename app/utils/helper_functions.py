import os
import requests
from dotenv import load_dotenv
from datetime import datetime
from app.models import Fixture, FixtureFree, db, User, UserTipStats, Tip
from app import create_app, db
from datetime import datetime, date, timedelta
import pytz
from app.services.fixtures import find_current_round

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
    match_ids = [f.match_id for f in FixtureFree.query.filter_by(round=find_current_round()).all()]
    tips = Tip.query.filter(Tip.user_id==user_id, Tip.match.in_(match_ids)).all()
    
    if len(match_ids)==len(set(t.match for t in tips)):
        return True
    else:
        return False

def get_all_rounds():
    rounds = db.session.query(FixtureFree.round).distinct().order_by(FixtureFree.round).all()
    return [r[0] for r in rounds]


def is_past_thursday_5pm_aus():
    now = datetime.now(pytz.timezone('Australia/Sydney'))
    
    # Calculate the start of the week (Monday at 12:01 AM)
    monday = now - timedelta(days=now.weekday())  # Get the previous Monday
    monday = monday.replace(hour=0, minute=1, second=0, microsecond=0)

    # Calculate the end of the week (Sunday at 11:59 PM)
    sunday = monday + timedelta(days=6)  # Get the next Sunday
    sunday = sunday.replace(hour=23, minute=59, second=59, microsecond=999999)

    days_until_thursday = (3 - now.weekday()) % 7
    thursday = now - timedelta(days=now.weekday() - 3) if now.weekday() >= 3 else now - timedelta(days=now.weekday() + 4)
    thursday_5pm = thursday.replace(hour=17, minute=0, second=0, microsecond=0)


    if monday <= now <= thursday_5pm:
        return False
    elif thursday_5pm <= now <= sunday:
        return True 
    else:
        return False
