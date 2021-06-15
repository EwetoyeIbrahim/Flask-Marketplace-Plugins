import json
import os

from flask_security import current_user
from requests import get, post

from Flask_Marketplace.factory import db
from Flask_Marketplace.models.shop_models import AccountDetail, Dispatcher, Order, OrderLine, Store
from Flask_Marketplace.utilities import register_store
# Getting the bank details handy,
# Banks don't get created every year
# Instead of querying Flutterwaves bank codes api for a data
# that may never be updated within a year or two, maybe even more,
# a JSON file generated from a python script which will be added to
# the repository later.
# The script will be used to collect the updated bank details,
# when require, maximum of once in a year.
# ---------------------
# Pre-generate the bank options as a var in format list of tuples
# Format => ('name/country_code/bank_code', 'name(country_code)')
# The above format will be used to assign value during the creation
# of sub-accounts.
with open(os.path.join(os.path.dirname(__file__), 'bank_data.json'),
          encoding='utf8') as f:
    bank_data = json.load(f)
bank_options = []
for k, v in bank_data.items():
    for line in v:
        bank_options.append((f"{line['code']}/{k}",
                             f"{line['name']}({k})"))


def confirm_payment(trans_id, currency, value, flw_sec_key):
    print('Started confirm_payment')
    '''
    Note: Flutterwave only checks if the given payment exists.
    It does not tell me if it has been formerly used previously
    used on this platform.
    Thus, calling functions have to check its usability.
    '''
    flw_resp = get(
        'https://api.flutterwave.com/v3/transactions/' + str(
            trans_id) + '/verify',
        headers={"Content-Type": "application/json",
                 'Authorization': 'Bearer ' + flw_sec_key}
    ).json()
    if flw_resp['data']['status'] == 'successful':
        # confirm currency and amount
        if flw_resp['data']['currency'] == currency:
            if flw_resp['data']['amount'] >= float(value):
                print('True confirm_payment')
                return flw_resp['data']['tx_ref']
    print('False confirm_payment')
    return False


def confirm_store_reg(trans_id, store_reg_amt, flw_sec_key):
    value, currency = store_reg_amt.split(' ')
    tx_ref = confirm_payment(trans_id, currency, value, flw_sec_key)
    if tx_ref:
        # Check if the txref is still usable
        # Recall, txref = store/user_id/number_of_stores.
        # Confirm that the current user matches the reference id
        _, user_id, store_num = tx_ref.split('/')
        if int(user_id) == current_user.id:
            # confirm is number of stores is valid
            if int(store_num) == len(current_user.stores):
                # Now, it's too good not to be true
                # Proceed with dummy store creation
                # We want to randomly fix a store to a dispatcher
                register_store()
                # Note: trans_id has been used to create a store
                return trans_id
    return False


def confirm_sales_payment(trans_id, flw_sec_key):
    # get the order data for comparism and verification
    cart = Order.cart().filter_by(user_id=current_user.id).first()
    cart_tot = db.session.query(
        db.func.sum(OrderLine.qty * OrderLine.price)).filter(
        OrderLine.order_id == cart.id).group_by(OrderLine.order_id).first()
    tx_ref = confirm_payment(trans_id, cart.iso_code, cart_tot[0],
                             flw_sec_key)
    if tx_ref:
        # Recall, txref = order/user_id/order_id.
        # Here user_id is no longer needed as order_id is sufficient
        if int(tx_ref.split('/')[2]) == cart.id:
            # Now, it's too good not to be true
            # We can now certify the order
            cart.status = 'paid'
            cart.amount = str(cart_tot[0])
            db.session.commit()
            return True
    return False


def flw_subaccount(partner, mode, split_ratio, account_form,
                   flw_sec_key):
    bank_code, country = account_form.bank.data.split('/')
    url = "https://api.flutterwave.com/v3/subaccounts"
    headers = {
        'Authorization': flw_sec_key,
        'Content-Type': 'application/json'
    }
    payload = {
        'account_bank': bank_code,
        'account_number': account_form.account_num.data,
        'business_name': partner.name,
        'country': country,
        'split_value': str(1-float(split_ratio)),
        'split_type': 'percentage',
        'business_mobile': partner.phone,
        'business_email': partner.email
    }

    result = post(url, headers=headers, data=json.dumps(payload),).json()
    # Record the created subaccount
    if result['data']:
        if not partner.account:
            account = AccountDetail(
                account_name=result['data']['bank_name'],
                account_num=result['data']['account_number'],
                bank=result['data']['account_bank'],
                sub_id=result['data']['id'],
                sub_number=result['data']['subaccount_id'],)
            partner.account = account
            db.session.commit()
        else:
            # The store owner is trying to change the attached account
            partner.account.account_name=result['data']['bank_name']
            partner.account.account_num=result['data']['account_number']
            partner.account.bank=result['data']['account_bank']
            partner.account.sub_id=result['data']['id']
            partner.account.sub_number=result['data']['subaccount_id']
        db.session.commit()
        return('Your account has been successfully verified', 'success')
    elif ('kindly pass a valid account' in result['message']):
        return('Your account number and/or bank is invalid', 'danger')
    elif ('number and bank already exists' in result['message']):
        account=AccountDetail.query.filter_by(
            account_num = account_form.account_num.data).first()
        if account:
            partner.account_id=account.id
            return('A similar account was found and assigned', 'info')
    return('Crical error: contact us', 'danger')
