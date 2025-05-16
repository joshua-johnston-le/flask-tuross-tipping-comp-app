from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app, session
from flask_login import login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from app import db
from app.models import User  # Assuming your User model is here
import os

profile_bp = Blueprint('profile', __name__)

TMP_AVATAR_LIST = [
    'borat.png',
    'chicken.jpg'
]

@profile_bp.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    avatar_folder = os.path.join(current_app.static_folder, 'avatars')
    avatars = sorted([f for f in os.listdir(avatar_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])
    return render_template("profile.html", avatars=TMP_AVATAR_LIST, current_avatar=session.get('avatar', 'chicken.jpg'))

@profile_bp.route('/update_password', methods=['POST'])
@login_required
def update_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        # Check if current password matches
        if not current_user.check_password(current_password):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('profile.profile'))

        # Validate new password and confirm password match
        if new_password != confirm_password:
            flash('New passwords do not match', 'danger')
            return redirect(url_for('profile.profile'))

        # Update password
        current_user.set_password(new_password)
        db.session.commit()
        flash('Password updated successfully', 'success')
        return redirect(url_for('profile.profile'))

    return render_template('profile.html')


@profile_bp.route('/update_avatar', methods=['POST'])
@login_required
def update_avatar():
    avatar_folder = os.path.join(current_app.static_folder, 'avatars')
    avatars = sorted([f for f in os.listdir(avatar_folder) if f.endswith(('.png', '.jpg', '.jpeg'))])
    
    selected_avatar = request.form.get('selected_avatar')
    if selected_avatar and selected_avatar in avatars:
        current_user.avatar = secure_filename(selected_avatar)
        db.session.commit()
        flash('Avatar updated!', 'success')
        return redirect(url_for('profile.profile'))  # Adjust to your profile route
    else:
        flash('Invalid avatar selected.', 'danger')

    return render_template('profile.html', avatars=TMP_AVATAR_LIST)
