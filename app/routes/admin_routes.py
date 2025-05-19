from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models import User, Tip, FixtureFree
from datetime import date
from app import db
from app.services.fixtures import find_current_round

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/admin", methods=["GET", "POST"])
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for("main.index"))

    current_round = find_current_round()

    if not current_round:
        return render_template("admin.html", round_data=None)

    users = User.query.all()
    current_fixtures = FixtureFree.query.filter_by(round=current_round).all()
    current_match_ids = [f.match_id for f in current_fixtures]

    tips_by_user = {}
    for user in users:
        tips = Tip.query.filter(Tip.user_id == user.id, Tip.match.in_(current_match_ids)).all()
        tips_by_user[user.id] = tips

    # Handle Change Username form submission
    username_update_success = False
    username_update_error = None

    if request.method == "POST" and "user_id" in request.form and "new_username" in request.form:
        user_id = request.form["user_id"]
        new_username = request.form["new_username"].strip()

        existing_user = User.query.filter_by(username=new_username).first()
        if existing_user:
            username_update_error = "Username already taken."
        else:
            user = User.query.get(user_id)
            if user:
                user.username = new_username
                db.session.commit()
                username_update_success = True
            else:
                username_update_error = "User not found."

    return render_template(
        "admin.html",
        users=users,
        tips_by_user=tips_by_user,
        round=current_round,
        username_update_success=username_update_success,
        username_update_error=username_update_error,
    )
