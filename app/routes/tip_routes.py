from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models import db, Tip, FixtureFree
from app.utils.team_logos import TEAM_LOGOS
from datetime import date, timedelta

tip_bp = Blueprint('tip', __name__)

@tip_bp.route('/submit_tip', methods=['GET', 'POST'])
@login_required
def submit_tip():
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    fixtures = FixtureFree.query.filter(
        FixtureFree.date >= monday,
        FixtureFree.date <= sunday
    ).all()
    
    match_ids = [f.id for f in fixtures]  # ✅ FIXED: use f.id not f.match_id
    
    existing_tips = Tip.query.filter(Tip.user_id == current_user.id, Tip.match.in_(match_ids)).all()
    has_submitted = len(existing_tips) == len(match_ids)
    
    if request.method == 'POST':
        if has_submitted:
            flash('You have already submitted your tips.', 'warning')
            return redirect(url_for('main.home'))

        for fixture in fixtures:
            match_id = fixture.id
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

