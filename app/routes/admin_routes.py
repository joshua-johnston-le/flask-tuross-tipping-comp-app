from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from app.models import User, Tip, Fixture
from datetime import date
from app import db
from app.services.fixtures import 

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for("main.index"))

    # Get current round (assuming you have a way to determine it)
    current_round = find_current_round()
    if not current_round:
        return render_template("admin.html", round_data=None)

    # Get all users
    users = User.query.all()

    # Get all tips for current round
    current_fixtures = Fixture.query.filter_by(round=current_round).all()
    current_match_ids = [f.match_id for f in current_fixtures]

    tips_by_user = {}
    for user in users:
        tips = Tip.query.filter(Tip.user_id == user.id, Tip.match.in_(current_match_ids)).all()
        tips_by_user[user.id] = tips

    return render_template("admin.html", users=users, tips_by_user=tips_by_user, round=current_round)
