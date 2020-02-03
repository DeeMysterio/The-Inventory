
from wtforms_alchemy import ModelForm
from flask_wtf import Form
from inventory.models import Location


class LocationForm(ModelForm, Form):
    class Meta:
        model = Location
        include = ['name', 'address']