from wtforms_alchemy import ModelForm
from flask_wtf import Form
from inventory.models import Product


class ProductForm(ModelForm, Form):
    class Meta:
        model = Product
        include = ['name']