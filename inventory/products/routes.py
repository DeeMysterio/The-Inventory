from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from inventory import db
from inventory.models import Product
from .forms import ProductForm


products = Blueprint('products', __name__)


@products.route("/")
def show_report():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=10)
    return render_template('report.html', products=products, title='Report')

@products.route("/products")
def list_products():
    page = request.args.get('page', 1, type=int)
    products = Product.query.paginate(page=page, per_page=10)
    return render_template('products.html', products=products, title='Products')

@products.route("/product/<int:product_id>")
def product(product_id):
    product = Product.query.get_or_404(product_id)
    return render_template('product.html', title=product.name, product=product, legend='Product Details')

@products.route("/product/new", methods=['GET', 'POST'])
@login_required
def new_product():
    form = ProductForm()
    if form.validate_on_submit():
        product = Product(name=form.name.data)
        product.creator=current_user
        db.session.add(product)
        db.session.commit()
        flash_message = 'The product has been added!'
        flash(flash_message, 'success')
        return redirect(url_for('products.list_products'))
    return render_template('create_product.html', title="New Product", form=form, legend='New Product')

@products.route("/product/<int:product_id>/update", methods=['GET', 'POST'])
@login_required
def update_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.creator != current_user:
        abort(403)
    form = ProductForm()
    if form.validate_on_submit():
        product.name = form.name.data
        db.session.commit()
        flash('The product has been updated!', 'success')
        return redirect(url_for('products.product', product_id=product.product_id))
    elif request.method == 'GET':
        form.name.data = product.name
    return render_template('create_product.html', title="Update Product", form=form, legend='Update Product')

@products.route("/product/<int:product_id>/delete", methods=['POST'])
@login_required
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    if product.creator != current_user:
        abort(403)
    db.session.delete(product)
    db.session.commit()
    flash('The product has been deleted', 'success')
    return redirect(url_for('products.list_products'))

