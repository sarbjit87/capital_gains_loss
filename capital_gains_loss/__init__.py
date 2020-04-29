from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from flask_migrate import Migrate
from capital_gains_loss.config import Config

db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = 'users.login'
login_manager.login_message_category = 'info'
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app,db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)

    from capital_gains_loss.users.routes import users
    from capital_gains_loss.transactions.routes import transactions
    from capital_gains_loss.main.routes import main
    from capital_gains_loss.errors.handlers import errors
    app.register_blueprint(users)
    app.register_blueprint(transactions)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
