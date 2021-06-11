from flask_wtf import FlaskForm
from wtforms import (IntegerField, SelectField, StringField,
                     SubmitField)
from wtforms.validators import required

from .utilities import bank_options
from Flask_Marketplace.forms.shop_forms import AccountForm


class FlwAccountForm(AccountForm):
    """Extend the Account creation form
    Make the bank field to display a dropdown list of supported banks
    """
    bank = SelectField('Select a bank', [required()],
                       choices=bank_options,
                       render_kw={'title': 'Search',
                                  'data-live-search': 'true'}
                       )
