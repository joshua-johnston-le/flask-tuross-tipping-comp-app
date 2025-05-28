from app import create_app, db
from app.models import User, Tip, FixtureFree
from app.services.fixtures import find_current_round
from app.utils.helper_functions import has_user_submitted_tips

def run():
    app = create_app()
    with app.app_context():
        users = User.query.all()
        current_round = find_current_round()
        fixtures = FixtureFree.query.filter_by(round=current_round).all

        for user in users:
            if not has_user_submitted_tips(user.id):
                for fixture in fixtures:
                    new_tip = Tip(user_id=user.id, username=user.username, match=fixture.match_id, selected_team=fixture.away_team)
                db.session.add(new_tip)
                print(f"❌ {user.username} HAS NOT submitted their tips and were given away teams ")
            else:
                print(f"✅ {user.username} HAS submitted their tips for round: {current_round}")
        db.session.commit()
        
if __name__ = "__main__":
    print('Running submission checks...')
    #run()
    print('Done ✔✔✔')