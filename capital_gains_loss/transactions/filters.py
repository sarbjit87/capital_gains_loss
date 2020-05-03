from flask import Blueprint
from decimal import Decimal

filters = Blueprint('filters', __name__)

@filters.app_template_filter()
def pretty_date(dttm):
    return dttm.strftime('%Y-%m-%d')

@filters.app_template_filter()
def convert_to_cad(amount,forex):
    if forex != Decimal(0):
        return round((amount * forex), 2)
    else:
        return amount

@filters.app_template_filter()
def gain_loss_check(gl,trntype):
    if (trntype == "buy") and (gl == Decimal(0)):
        return "N/A"
    else:
        return gl
