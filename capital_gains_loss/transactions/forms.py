from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, DateTimeField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from wtforms.widgets import html_params, HTMLString
import datetime
from capital_gains_loss.models import Transaction
from flask_login import current_user

class DateTimePickerWidget(object):
    """
    Date Time picker from Eonasdan GitHub
    """

    data_template = (
            """
            <div class="input-group date" id="datetimepicker1" data-target-input="nearest">
                <input %(text)s class="form-control datetimepicker-input" data-target="#datetimepicker1"/>
                <div class="input-group-append" data-target="#datetimepicker1" data-toggle="datetimepicker">
                    <div class="input-group-text"><i class="fa fa-calendar"></i></div>
                </div>
            </div>
            """
    )

    def __call__(self, field, **kwargs):
        kwargs.setdefault("id", field.id)
        kwargs.setdefault("name", field.name)
        if not field.data:
            field.data = ""
        template = self.data_template

        return HTMLString(
            template % {"text": html_params(type="text", value=field.data, **kwargs)}
        )


class TransactionForm(FlaskForm):
    security_name = StringField('Security Name', validators=[DataRequired(), Length(max=20)])
    security_details = StringField('Security Details (Optional)', validators=[])
    transaction_date = StringField('Transaction Date',validators=[], widget=DateTimePickerWidget())
    transaction_type = SelectField(u'Transaction Type', choices = [('buy', 'Buy'), ('sell', 'Sell')], validators=[])
    quantity = IntegerField('Number of Shares', validators=[DataRequired()])
    price_per_share = DecimalField('Price per Share', validators=[DataRequired()])
    fees = DecimalField('Commission/Brokerage Fees', validators=[Optional()])
    amount_recieved = DecimalField('Amount Recieved (Optional)', validators=[Optional()])
    amount_recieved_details = StringField('Amount Recieved Details (Optional)', validators=[])
    forex_rate = DecimalField('Forex Rate, if in foreign currency (will be used for both shares and fees)',places=4, validators=[Optional()])
    submit = SubmitField('Add Transaction')

    def validate_transaction_date(self, field):
        try:
            dt = datetime.datetime.strptime(field.data, '%m/%d/%Y %I:%M %p')
            print(dt)
        except Exception as e:
            print(e)
            raise ValidationError('Invalid Date format!')

    def validate(self):
        if not super(TransactionForm, self).validate():
            return False

        last_transaction = Transaction.query.filter_by(security_name=self.security_name.data.upper(),author=current_user).order_by(Transaction.transaction_date.desc()).first()
        print(last_transaction)
        print(last_transaction.total_shares)
        if self.transaction_type.data.lower() == "sell":
            if self.quantity.data > last_transaction.total_shares:
                msg = 'No Stock available to sell!'
                self.transaction_type.errors.append(msg)
            return False
        return True


class TransactionFormUpdate(FlaskForm):
    security_name = StringField('Security Name', validators=[DataRequired(), Length(max=20)])
    security_details = StringField('Security Details (Optional)', validators=[])
    transaction_date = StringField('Transaction Date',validators=[], widget=DateTimePickerWidget())
    transaction_type = SelectField(u'Transaction Type', choices = [('buy', 'Buy'), ('sell', 'Sell')], validators=[])
    quantity = IntegerField('Number of Shares', validators=[DataRequired()])
    price_per_share = DecimalField('Price per Share', validators=[DataRequired()])
    fees = DecimalField('Commission/Brokerage Fees', validators=[Optional()])
    amount_recieved = DecimalField('Amount Recieved (Optional)', validators=[Optional()])
    amount_recieved_details = StringField('Amount Recieved Details (Optional)', validators=[])
    forex_rate = DecimalField('Forex Rate, if in foreign currency (will be used for both shares and fees)',places=4, validators=[Optional()])
    submit = SubmitField('Update Transaction')

    def validate_transaction_date(self, field):
        try:
            dt = datetime.datetime.strptime(field.data, '%m/%d/%Y %I:%M %p')
            print(dt)
        except Exception as e:
            print(e)
            raise ValidationError('Invalid Date format!')

    def validate(self):
        if not super(TransactionFormUpdate, self).validate():
            return False

        total_shares = 0
        transactions = Transaction.query.filter_by(security_name=self.security_name.data.upper(),author=current_user).order_by(Transaction.transaction_date.asc())
        for transaction in transactions:
            if transaction.transaction_type.lower() == "buy":
                total_shares = total_shares + transaction.quantity
            elif transaction.transaction_type.lower() == "sell":
                total_shares = total_shares - transaction.quantity

        if self.transaction_type.data.lower() == "sell":
            #print("Debug ", self.quantity.data, total_shares)
            if self.quantity.data >= total_shares:
                msg = 'Cannot edit to sell transaction. This will lead to selling stocks which are not available (no corresponding buy transaction)!'
                self.transaction_type.errors.append(msg)
            return False
        return True
