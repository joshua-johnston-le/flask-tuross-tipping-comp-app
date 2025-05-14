from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Tip, FixtureFree, User, UserTipStats
from app.utils.team_logos import TEAM_LOGOS
from datetime import date, timedelta

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route("/leaderboard", methods=["GET","POST"])
@login_required
def leaderboard():
    # Aggregate total successful tips per user
    leaderboard_data = (
        db.session.query(
            User.username,
            db.func.sum(UserTipStats.successful_tips).label("total_success"),
            db.func.sum(UserTipStats.failed_tips).label("total_failure"),
            db.func.sum(UserTipStats.pending_tips).label("total_pending")
        )
        .join(User, User.id == UserTipStats.user_id)
        .group_by(User.id)
        .order_by(db.desc("total_success"))  # Sort by success descending
        .all()
    )
    round_data = (
        db.session.query(
            UserTipStats.round_number,
            db.func.sum(UserTipStats.successful_tips).label("total_success"),
            db.func.sum(UserTipStats.failed_tips).label("total_failure"),
            db.func.sum(UserTipStats.pending_tips).label("total_pending")
        )
        .filter_by(user_id=current_user.id)
        .group_by(UserTipStats.round_number)
        .order_by(db.desc("total_success"))  # Sort by success descending
        .all()
    )
    

    return render_template("leaderboard.html", leaderboard_data=leaderboard_data, round_data=round_data)

