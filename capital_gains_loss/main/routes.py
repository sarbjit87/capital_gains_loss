from flask import render_template, request, Blueprint
from flask_login import current_user, login_required
from capital_gains_loss.models import Transaction
from capital_gains_loss import db
from decimal import Decimal

main = Blueprint('main', __name__)

def calculate_acb(symbol):
    transactions = Transaction.query.filter_by(security_name=symbol,author=current_user).order_by(Transaction.transaction_date.asc())
    previous_record = None
    total_shares = 0
    for transaction in transactions:
        if previous_record is None:
            previous_acb = 0
        else:
            previous_acb = previous_record.acb

        #print("Debug: Processing Transaction : ", transaction)
        #print("Debug: Previous ACB : ", previous_acb)
        #print("Debug: Total Shares : ", total_shares)
        #print("Debug: Transaction quantity : ", transaction.quantity)
        #print("Debug: Transaction ID : ", transaction.id)
        if transaction.transaction_type.lower() == "buy":
            #BUY Transaction
            if transaction.forex_rate != Decimal(0):
                amount_in_cad = (transaction.quantity * transaction.price_per_share * transaction.forex_rate)
                transaction.acb = previous_acb + amount_in_cad + (transaction.fees * transaction.forex_rate)
            else:
                amount_in_cad = (transaction.quantity * transaction.price_per_share)
                transaction.acb = previous_acb + amount_in_cad + transaction.fees

            transaction.amount_in_cad = amount_in_cad
            transaction.acb_change = transaction.acb - previous_acb
            total_shares = total_shares + transaction.quantity
            transaction.total_shares = total_shares
        else:
            #SELL Transaction
            acb_sell = ((previous_acb /total_shares) * transaction.quantity)
            transaction.acb = previous_acb * Decimal(((total_shares - transaction.quantity) / total_shares))

            if transaction.forex_rate != Decimal(0):
                amount_in_cad = (transaction.quantity * transaction.price_per_share * transaction.forex_rate)
                transaction.gain_loss = amount_in_cad - (transaction.fees * transaction.forex_rate) - acb_sell
                #transaction.gain_loss = ((transaction.quantity * transaction.price_per_share * transaction.forex_rate) - (transaction.fees * transaction.forex_rate)) - ((transaction.acb/total_shares) * transaction.quantity)
            else:
                amount_in_cad = (transaction.quantity * transaction.price_per_share)
                transaction.gain_loss = amount_in_cad - (transaction.fees) - acb_sell
                #transaction.gain_loss = (transaction.quantity * transaction.price_per_share) - transaction.fees - transaction.acb

            transaction.amount_in_cad = amount_in_cad
            transaction.acb_change = transaction.acb - previous_acb
            total_shares = total_shares - transaction.quantity
            transaction.total_shares = total_shares

        db.session.commit()
        previous_record = transaction


@main.route("/")
@main.route("/home")
@login_required
def home():
    symbols = Transaction.query.filter_by(author=current_user).with_entities(Transaction.security_name).distinct().all()
    symbols = [value for value, in symbols]
    symbols.sort()
    symbol = ""

    if len(symbols) > 0:
        page = request.args.get('page', 1, type=int)
        symbol = request.args.get('symbol', symbols[0])
        transactions = Transaction.query.filter_by(security_name=symbol,author=current_user).order_by(Transaction.transaction_date.desc()).paginate(page=page, per_page=10)
    else:
        transactions = Transaction.query.filter_by(author=current_user).all()

    calculate_acb(symbol)

    return render_template('home.html', transactions=transactions,symbols=symbols, symbol=symbol)

@main.route("/about")
def about():
    return render_template('about.html', title='About')
