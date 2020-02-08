from wtforms_alchemy.fields import QuerySelectField
from wtforms_alchemy import ModelForm
from flask_wtf import Form
from inventory.models import Product, Location, Movement


class MovementForm(ModelForm, Form):
    class Meta:
        model = Movement
    from_location = QuerySelectField(
        query_factory=lambda: Location.query.all(),
        get_pk=lambda a: a.location_id,
        get_label=lambda a: a.name,
        allow_blank=True,
    )
    to_location = QuerySelectField(
        query_factory=lambda: Location.query.all(),
        get_pk=lambda a: a.location_id,
        get_label=lambda a: a.name,
        allow_blank=True,
    )
    product = QuerySelectField(
        query_factory=lambda: Product.query.all(),
        get_pk=lambda a: a.product_id,
        get_label=lambda a: "{0} ({1})".format(a.name, str(a.warehouse)),
        allow_blank=False,
    )

    def validate_product(self, field):
        if self.from_location.data and field.data:
            if not field.data.warehouse:
                self.product.errors.append('The product does not belong to any warehouse yet.')

    def validate_from_location(self, field):
        result = True

        if not field.data and not self.to_location.data:
            self.from_location.errors.append('Enter at least one of the locations.')
            result = False

        if field.data:
            if self.product.data.warehouse != field.data:
                self.from_location.errors.append('The product does not belong to this location.')
            elif field.data.get_product_quantity(self.product.data.name)<self.qty.data:
                self.from_location.errors.append('Location does not have enough stock. Available quantity: {0}'.format(field.data.get_product_quantity(self.product.data.name)))
            result = False

        if field.data and self.to_location.data:
            if self.from_location.data == self.to_location.data:
                self.from_location.errors.append('From Location can\'t be same as To Location.')
                result = False

        return result

    def validate_qty(self, field):
        result = True
        if not self.from_location.data and self.to_location.data:
            products = Product.query.all()
            products = [product for product in products if self.product.data.name==product.name and not product.warehouse]
            if not products:
                self.qty.errors.append('No products available! Please create some and then try adding or try moving From some Location.')
                return False
            
            elif len(products) < field.data:
                self.qty.errors.append('Only {0} item(s) available! Please create more of them.'.format(len(products)))
                return False
        return result