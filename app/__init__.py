from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config
from flask_login import current_user

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'  # Redirect to login view if not authenticated

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Import models so they are registered with SQLAlchemy
    from .models import User
    
    # User loader for Flask-Login
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Import and register blueprints
    from .routes import main
    from .auth import auth
    app.register_blueprint(main)
    app.register_blueprint(auth)


    with app.app_context():
        db.create_all()


    return app

