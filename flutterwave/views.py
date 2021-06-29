''' Defination of all shop views in `shop` blueprint '''
import json

from flask import (Blueprint, current_app, flash, render_template_string,
                   request, url_for, render_template)
from flask_login import login_required
from Flask_Marketplace.factory import db
from Flask_Marketplace import MarketViews
from . import utilities


# === Declaring the blueprint views ===
flutterwave = Blueprint('flutterwave', __name__, template_folder='templates')


@flutterwave.route('/callback/store_payment', methods=['POST'])
def callback_store_payment():
    flw_data = request.json
    store_name = utilities.confirm_store_reg(
        flw_data['transaction_id'],
        current_app.config['STORE_REG_AMT'],
        current_app.config['FLW_SEC_KEY'])
    if store_name:
        flash("Payment confirmed. Edit your store details to get started.",
              'success')
        return {'redirect': url_for('marketplace.store_admin', store_name=store_name)}
    flash("Unable to confirm payment, contact us", 'danger')
    return {'redirect': url_for('marketplace.dashboard')}


@flutterwave.route('/callback/sales_payment', methods=['POST'])
def callback_sales_payment():
    flw_data = request.json
    if utilities.confirm_sales_payment(
            flw_data['transaction_id'],
            current_app.config['FLW_SEC_KEY']):
        flash("Payment confirmed, thank you", 'success')
    else:
        flash("Unable to confirm payment, contact us", 'danger')
    return {'redirect': url_for('marketplace.market')}


# === Views to overide ===
class FlutterwaveViews(MarketViews):
    @login_required
    def checkout(self):
        if current_app.config['PAY_ON_CHECKOUT']:
            html_string = super().checkout(template_folder='flutterwave')
        else:
            html_string = super().checkout()
        return render_template_string(html_string)

    @login_required
    def store_new(self, **kwargs):
        """Mandate payment for stores
        """
        if current_app.config['PAY_FOR_STORE_REGISTERATION']:
            return render_template('flutterwave/store_new.html')
        else:
            return render_template_string(super().store_new())
