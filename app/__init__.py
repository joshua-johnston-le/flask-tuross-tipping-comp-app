from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv
from flask_apscheduler import APScheduler
from flask_migrate import Migrate

db = SQLAlchemy()
login_manager = LoginManager()
scheduler = APScheduler()
migrate = Migrate()

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'

    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    # Import models so they’re registered
    from . import models
    from .models import User
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from .routes.auth_routes import auth_bp
    from .routes.tip_routes import tip_bp
    from .routes.main_routes import main_bp
    from .routes.leaderboard_routes import leaderboard_bp
    from .routes.chat_routes import chat_bp
    from .routes.profile_routes import profile_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(tip_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(profile_bp)
    
    with app.app_context():
        db.create_all()

    return app
