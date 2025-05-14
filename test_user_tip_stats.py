# test_user_tip_stats.py

from app import create_app, db
from app.models import User, Tip, FixtureFree, UserTipStats
from datetime import date, time

def setup_test_data():
    # Create Flask app context
    app = create_app()
    with app.app_context():
        print("Setting up test data...")

        # Ensure test user exists
        user = User.query.filter_by(username="test_user").first()

        # Add round 9 fixtures
        fixtures = FixtureFree.query.filter_by(round=9).all()

        # Add tips for test user
        tip1 = Tip(user_id=user.id, match=65, selected_team="Sharks", username=user.username)     
        tip2 = Tip(user_id=user.id, match=66, selected_team="Roosters", username=user.username)    
        tip3 = Tip(user_id=user.id, match=67, selected_team="Rabbitohs", username=user.username)
        tip4 = Tip(user_id=user.id, match=68, selected_team="Warriors", username=user.username) 
        tip5 = Tip(user_id=user.id, match=69, selected_team="Wests Tigers", username=user.username)     
        tip6 = Tip(user_id=user.id, match=70, selected_team="Bulldogs", username=user.username)    
        tip7 = Tip(user_id=user.id, match=71, selected_team="Broncos", username=user.username)
        tip8 = Tip(user_id=user.id, match=72, selected_team="Raiders", username=user.username)    
        db.session.add_all([tip1, tip2, tip3, tip4, tip5, tip6, tip7, tip8])
        db.session.commit()

        # Run update function
        from app.services.fixtures import update_user_tip_stats  # Make sure this function exists
        update_user_tip_stats()

        # Output result
        stat = UserTipStats.query.filter_by(user_id=user.id, round_number=9).first()
        print(f"Results for user '{user.username}' in round 9:")
        print(f"✅ Successes: {stat.successful_tips}")
        print(f"❌ Failures:  {stat.failed_tips}")
        print(f"⏳ Pending:   {stat.pending_tips}")

if __name__ == "__main__":
    setup_test_data()
