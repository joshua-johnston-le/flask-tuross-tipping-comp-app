from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Tip, FixtureFree, User
from app.utils.team_logos import TEAM_LOGOS
from datetime import date, timedelta
from app.utils.helper_functions import get_all_rounds, is_past_thursday_5pm_aus
from app.services.fixtures import find_current_round

tip_bp = Blueprint('tip', __name__)

@tip_bp.route('/submit_tip', methods=['GET', 'POST'])
@login_required
def submit_tip():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    fixtures = FixtureFree.query.filter(FixtureFree.round==find_current_round()).all()
    
    match_ids = [f.match_id for f in fixtures]  # ✅ FIXED: use f.id not f.match_id
    
    existing_tips = Tip.query.filter(Tip.user_id == current_user.id, Tip.match.in_(match_ids)).all()
    has_submitted = len(existing_tips) == len(match_ids)
    
    if request.method == 'POST':
        if has_submitted:
            flash('You have already submitted your tips.', 'warning')
            return redirect(url_for('main.home'))

        for fixture in fixtures:
            match_id = fixture.match_id
            selected_team = request.form.get(f'team-input-{match_id}')  # ✅ Correct name

            if not selected_team:
                flash('You must select a team for all matches.', 'danger')
                return redirect(url_for('tip.submit_tip'))

            new_tip = Tip(user_id=current_user.id, username=current_user.username, match=match_id, selected_team=selected_team)
            db.session.add(new_tip)

        db.session.commit()
        flash('Tips submitted successfully!', 'success')
        return redirect(url_for('main.home'))

    submitted_tips = []
    if has_submitted:
        match_lookup = {f.id: f for f in fixtures}
        for tip in existing_tips:
            fixture = match_lookup.get(tip.match)
            print("here!!!")
            print(match_lookup.get(73))
            submitted_tips.append({
                'selected_team': tip.selected_team,
                #'date': "TBD" fixture.date if fixture else None
            })

    return render_template(
        'submit_tip.html',
        fixtures=fixtures,
        has_submitted=has_submitted,
        submitted_tips=submitted_tips,
        team_logos=TEAM_LOGOS
    )

@tip_bp.route("/view-tips")
@login_required
def view_tips():
    selected_round = request.args.get("round", type=int)
    all_rounds = get_all_rounds()

    if not selected_round:
        selected_round = find_current_round()

    fixtures = FixtureFree.query.filter_by(round=selected_round).order_by(FixtureFree.match_id.asc()).all()
    match_ids = [f.match_id for f in fixtures]

    users = User.query.filter(~User.username.in_(['testing_db2'])).all()
    tips_by_user = {
        user.id: Tip.query.filter(Tip.user_id == user.id, Tip.match.in_(match_ids)).all()
        for user in users if user.username not in ['testing_db2']
    }
    results_map = {match : FixtureFree.get_winning_team(match) for match in match_ids}
    
    return render_template(
        "view_tips.html",
        users=users,
        tips_by_user=tips_by_user,
        selected_round=selected_round,
        all_rounds=all_rounds,
        fixtures=fixtures,
        results_map=results_map,
        after_5_thursday=is_past_thursday_5pm_aus(), #dictate if user can see others tips
        current_round=find_current_round()
    )