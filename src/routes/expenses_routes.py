from flask import Blueprint

expenses_bp = Blueprint('expenses', __name__, url_prefix='/expenses')

@expenses_bp.route('/monthly')
def monthly_expenses():
    # code for monthly expenses page
    return "Monthly expenses page"
