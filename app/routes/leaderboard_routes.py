from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Tip, FixtureFree, User, UserTipStats
from app.utils.team_logos import TEAM_LOGOS
from datetime import date, timedelta
from sqlalchemy import func, asc
from sqlalchemy.orm import aliased
from sqlalchemy import over

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route("/leaderboard", methods=["GET","POST"])
@login_required
def leaderboard():
    # Aggregate total successful tips per user
    leaderboard_data = (
        db.session.query(
            User.username,
            db.func.sum(UserTipStats.successful_tips).label("total_success"),
            db.func.sum(UserTipStats.pending_tips).label("total_pending")
        )
        .join(User, User.id == UserTipStats.user_id)
        .group_by(User.id)
        .order_by(db.desc("total_success"))  # Sort by success descending
        .all()
    )
    
    #building a subquery so i can use the windows function to calc running total
    subquery = (
        db.session.query(
            UserTipStats.round_number.label("round_number"),
            func.sum(UserTipStats.successful_tips).label("total_success"),
            func.sum(UserTipStats.pending_tips).label("total_pending")
        )
        .filter(UserTipStats.user_id == current_user.id)
        .group_by(UserTipStats.round_number)
        .subquery()
    )

    
    alias = aliased(subquery)

    
    round_data = (
        db.session.query(
            alias.c.round_number,
            alias.c.total_success,
            alias.c.total_pending,
            over(
                func.sum(alias.c.total_success),
                order_by=alias.c.round_number
            ).label("running_total_success")
        )
        .order_by(alias.c.round_number)
        .all()
    )
    

    return render_template("leaderboard.html", leaderboard_data=leaderboard_data, round_data=round_data)

