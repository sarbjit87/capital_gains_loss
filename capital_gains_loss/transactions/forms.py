from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, DecimalField, DateTimeField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Optional, ValidationError
from wtforms.widgets import html_params, HTMLString
import datetime

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
    forex_rate = DecimalField('Forex Rate, if in foreign currency (will be used for both shares and fees)',places=4, validators=[Optional()])
    submit = SubmitField('Add Transaction')

    def validate_transaction_date(self, field):
        try:
            dt = datetime.datetime.strptime(field.data, '%m/%d/%Y %I:%M %p')
            print(dt)
        except Exception as e:
            print(e)
            raise ValidationError('Invalid Date format!')
