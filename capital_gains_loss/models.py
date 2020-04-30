from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from capital_gains_loss import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    transactions = db.relationship('Transaction', backref='author', lazy=True)

    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"


class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    security_name = db.Column(db.String(20), nullable=False)
    security_details = db.Column(db.String(100), nullable=True)
    transaction_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    transaction_type = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price_per_share = db.Column(db.Numeric(10,2), nullable=False)
    fees = db.Column(db.Numeric(10,2), nullable=True, default=0.0)
    forex_rate = db.Column(db.Numeric(precision=4), nullable=True, default=0.0)
    acb = db.Column(db.Numeric(10,2), nullable=True, default=0.0)
    acb_change = db.Column(db.Numeric(10,2), nullable=True, default=0.0)
    amount_in_cad = db.Column(db.Numeric(10,2), nullable=True, default=0.0)
    amount_recieved = db.Column(db.Numeric(10,2), nullable=True, default=0.0)
    amount_recieved_details = db.Column(db.String(100), nullable=True)
    gain_loss = db.Column(db.Numeric(10,2), nullable=True, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"Transaction('{self.security_name}', '{self.transaction_date}', '{self.transaction_type}')"
