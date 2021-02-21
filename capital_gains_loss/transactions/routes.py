from flask import (render_template, url_for, flash, jsonify,
                   redirect, request, abort, Blueprint, Response)
from flask_login import current_user, login_required
from capital_gains_loss import db
from capital_gains_loss.models import Transaction
from capital_gains_loss.transactions.forms import TransactionForm, TransactionFormUpdate
import datetime
import requests
import io
import csv
from capital_gains_loss.config import Config
from decimal import Decimal

transactions = Blueprint('transactions', __name__)

@transactions.route("/transaction/new", methods=['GET', 'POST'])
@login_required
def new_transaction():
    form = TransactionForm()
    if form.validate_on_submit():
        dt = datetime.datetime.strptime(form.transaction_date.data, '%m/%d/%Y %I:%M %p')
        transaction = Transaction(security_name=form.security_name.data.upper(),
                                  security_details=form.security_details.data,
                                  transaction_date=dt,
                                  transaction_type=form.transaction_type.data,
                                  quantity=form.quantity.data,
                                  price_per_share=form.price_per_share.data,
                                  fees=form.fees.data,
                                  forex_rate=form.forex_rate.data,
                                  amount_recieved=form.amount_recieved.data,
                                  amount_recieved_details=form.amount_recieved_details.data,
                                  author=current_user)
        db.session.add(transaction)
        db.session.commit()
        flash('New transaction has been created!', 'success')
        return redirect(url_for('main.home'))
    return render_template('create_transaction.html', title='New Transaction',
                           form=form, legend='New Transaction')


@transactions.route("/transaction/<int:transaction_id>/update", methods=['GET', 'POST'])
@login_required
def update_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.author != current_user:
        abort(403)
    form = TransactionFormUpdate()
    if form.validate_on_submit():
        transaction.security_name = form.security_name.data.upper()
        transaction.transaction_type = form.transaction_type.data
        transaction.security_details = form.security_details.data
        transaction.quantity = form.quantity.data
        transaction.price_per_share = form.price_per_share.data
        transaction.fees = form.fees.data
        transaction.forex_rate = form.forex_rate.data
        transaction.transaction_date = datetime.datetime.strptime(form.transaction_date.data, '%m/%d/%Y %I:%M %p')
        transaction.amount_recieved = form.amount_recieved.data
        transaction.amount_recieved_details = form.amount_recieved_details.data
        db.session.commit()
        flash('Transaction has been updated!', 'success')
        return redirect(url_for('main.home'))
    elif request.method == 'GET':
        form.security_name.data = transaction.security_name
        form.transaction_type.data = transaction.transaction_type
        form.security_details.data = transaction.security_details
        form.quantity.data = transaction.quantity
        form.price_per_share.data = transaction.price_per_share
        form.fees.data = transaction.fees
        form.forex_rate.data = transaction.forex_rate
        form.transaction_date.data = datetime.datetime.strftime(transaction.transaction_date, '%m/%d/%Y %I:%M %p')
        form.amount_recieved_details.data = transaction.amount_recieved_details
        form.amount_recieved.data = transaction.amount_recieved
    return render_template('create_transaction.html', title='Update Transaction',
                           form=form, legend='Update Transaction')


@transactions.route("/transaction/schedule3report", methods=['GET'])
@login_required
def schedule3_report():
    transactions = Transaction.query.filter(Transaction.gain_loss!=Decimal(0),Transaction.author==current_user).order_by(Transaction.transaction_date.desc()).all()
    return render_template('report.html', transactions=transactions)


@transactions.route("/transaction/<int:transaction_id>/delete", methods=['POST'])
@login_required
def delete_transaction(transaction_id):
    transaction = Transaction.query.get_or_404(transaction_id)
    if transaction.author != current_user:
        abort(403)
    db.session.delete(transaction)
    db.session.commit()
    flash('Your transaction has been deleted!', 'success')
    return redirect(url_for('main.home'))


@transactions.route("/transaction/<symbol_id>/delete", methods=['GET'])
@login_required
def delete_all_transaction(symbol_id):
    transaction = Transaction.query.filter_by(security_name=symbol_id,author=current_user).delete()
    db.session.commit()
    flash('All transactions has been deleted for symbol %s!' %(symbol_id), 'success')
    return redirect(url_for('main.home'))


@transactions.route('/forex', methods=['GET'])
@login_required
def find_forex_rate():
    try:
        trans_date = request.args.get('trans_date',0,type=str)
        trans_date = datetime.datetime.strptime(trans_date, '%m/%d/%Y %I:%M %p').date()
        qdate = datetime.datetime.strftime(trans_date, "%Y-%m-%d")
        r = requests.get("https://www.bankofcanada.ca/valet/observations/FXUSDCAD/json?start_date=%s&end_date=%s" %(qdate,qdate))
        res = r.json()
        forex = res['observations'][0]['FXUSDCAD']['v']
        return jsonify(result=forex)
    except Exception as e:
        print(e)
        return str(e)

@transactions.route('/commission', methods=['GET'])
@login_required
def find_commission():
    try:
        quantity = Decimal(request.args.get('quantity',0))
        forex_rate = Decimal(request.args.get('forex_rate',0))
        fees = Decimal(request.args.get('fees',0,type=str))
        amount_recieved = Decimal(request.args.get('amount_recieved',0))
        price_per_share = Decimal(request.args.get('price_per_share',0))

        if forex_rate != Decimal(0):
            amount = (quantity * price_per_share * forex_rate) - (fees * forex_rate)
        else:
            amount = (quantity * price_per_share) - fees

        difference =  amount - amount_recieved

        if forex_rate != Decimal(0):
            fees = fees + difference/forex_rate
        else:
            fees = fees + difference

        print("DEBUG IN COMMISSION : Amount : %f , difference : %f, FEES: %f" %(amount,difference, fees))

        fees = round(fees,2)

        return jsonify(result=str(fees))
    except Exception as e:
        print(e)
        return str(e)

@transactions.route('/downloadcsv/')
@login_required
def download_csv():
    transactions = Transaction.query.filter_by(author=current_user).order_by(Transaction.transaction_date.desc())
    output = io.StringIO()
    writer = csv.writer(output)
    list_items = ['id', 'security_name', 'security_details', 'transaction_date', 'transaction_type',\
                  'quantity', 'price_per_share', 'fees', 'forex_rate', 'acb', 'gain_loss', 'amount_recieved',\
                  'amount_recieved_details', 'amount_in_cad', 'acb_change']
    line = ''
    for x in list_items:
        line = line + x + ','

    line = line.rstrip(',')
    writer.writerow([line])

    for transaction in transactions:
        line = ''
        for x in list_items:
            line = line + '"' + str(getattr(transaction,x)) + '"' + ','
        line = line.rstrip(',')
        writer.writerow([line])

    filedt = datetime.datetime.utcnow().strftime('%m_%d_%Y')
    output.seek(0)

    return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=export_%s.csv" %(filedt)})

def allowed_file(filename):
    if not "." in filename:
        return False
    ext = filename.rsplit(".", 1)[1]
    if ext.upper() in ['CSV']:
        return True
    else:
        return False



@transactions.route('/uploadcsv', methods = ['GET', 'POST'])
@login_required
def upload_csv():
    if request.method == "POST":
        if request.files:
            csvfile1 = request.files["csvfile"]

            if csvfile1.filename == "":
                flash('No file provided!', 'danger')
                return redirect(request.url)

            if not allowed_file(csvfile1.filename):
                flash('Only csv files are allowed', 'danger')
                return redirect(request.url)

            stream = io.StringIO(csvfile1.stream.read().decode("UTF8"), newline=None)
            csv_input = csv.reader(stream)

            result = []
            headers = [header.strip() for header in next(csv_input)]
            headers = headers[0].split(",")

            for line in csv_input:
                values = [value.strip() for value in line]
                values = values[0].split(",")
                r = {}
                for idx, val in enumerate(headers):
                    #print("IDX: %d, VAL: %s" %(idx,val))
                    r[val] = values[idx].strip('"')
                result.append(r)

            for r in result:
                dt = datetime.datetime.strptime(r['transaction_date'], '%Y-%m-%d %H:%M:%S')
                transaction = Transaction(security_name=r['security_name'].upper(),
                                          security_details=r['security_details'],
                                          transaction_date=dt,
                                          transaction_type=r['transaction_type'],
                                          quantity=r['quantity'],
                                          price_per_share=r['price_per_share'],
                                          fees=r['fees'],
                                          forex_rate=r['forex_rate'],
                                          amount_recieved=r.get('amount_recieved'),
                                          amount_recieved_details=r.get('amount_recieved_details'),
                                          author=current_user)
                db.session.add(transaction)
                db.session.commit()
            flash('CSV file uploaded successfully!', 'success')

            return redirect(url_for('main.home'))
    return render_template("upload.html")
