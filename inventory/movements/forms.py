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
        get_label=lambda a: a.name,
        allow_blank=False,
    )

    def validate_from_location(self, field):
        result = True

        if not field.data and not self.to_location.data:
            self.from_location.errors.append('Enter at least one of the locations.')
            result = False

        elif field.data and field.data.get_product_quantity(self.product.data.name)<self.qty.data:
                self.from_location.errors.append('From Location does not have enough stock.')
                result = False

        elif field.data and self.to_location.data:
            if self.from_location.data == self.to_location.data:
                self.from_location.errors.append('From Location cant be same as To Location.')
                result = False

            
        return result