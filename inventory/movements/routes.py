from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from inventory.models import Movement, Product
from inventory import db
from .forms import MovementForm

movements = Blueprint('movements', __name__)


@movements.route("/movements")
def list_movements():
    page = request.args.get('page', 1, type=int)
    movements = Movement.query.order_by(Movement.timestamp.desc()).paginate(page=page, per_page=10)
    return render_template('movements.html', movements=movements, title='Movements')

@movements.route("/movement/<int:movement_id>")
def movement(movement_id):
    movement = Movement.query.get_or_404(movement_id)
    return render_template('movement.html', title=movement, movement=movement, legend='Movement Details')

@movements.route("/movement/new", methods=['GET', 'POST'])
@login_required
def new_movement():
    form = MovementForm()
    if form.validate_on_submit():
        from_location = form.from_location.data if hasattr(form, 'from_location') else None
        to_location = form.to_location.data if hasattr(form, 'to_location') else None
        product = form.product.data
        qty = form.qty.data

        if from_location and to_location:
            products = db.session.query(Product).filter(Product.warehouse==from_location).all()
            products_transferred = 0
            for item in products:
                if item.name == product.name and products_transferred<qty:
                    products_transferred+=1
                    item.warehouse = to_location
                    db.session.add(item)
            db.session.commit()
            flash_msg = 'The products have been successfully shifted'

        elif from_location or to_location:
            if from_location and from_location.get_product_quantity(product.name)>= qty:
                products = db.session.query(Product).filter(Product.warehouse==from_location).all()
                for product in products:
                    product.warehouse = None
                db.session.commit()
                flash_msg = 'The products have been successfully removed!'
            elif to_location:
                products_to_add = []
                products = db.session.query(Product).filter(Product.name==product.name)
                products_transferred = 0
                for product in products:
                    if not product.warehouse and products_transferred<qty:
                        products_transferred+=1
                        product.warehouse = to_location
                        products_to_add.append(product)
                db.session.add_all(products_to_add)
                db.session.commit()
                flash_msg = '{0} {1}(s) have been added in the warehouse {2}!'.format(len(products_to_add), product.name, to_location)
        product_id = product.product_id
        movement = Movement(product_id=product_id, qty=qty, 
                        from_location=from_location,
                        to_location=to_location, creator=current_user)
        db.session.add(movement)
        db.session.commit()
        flash(flash_msg, 'success')
        return redirect(url_for('movements.list_movements'))
    return render_template('create_movement.html', title="New Movement", form=form, legend='Add a new Movement')


@movements.route("/movement/<int:movement_id>/update", methods=['GET', 'POST'])
@login_required
def update_movement(movement_id):
    movement = Movement.query.get_or_404(movement_id)
    if movement.creator != current_user:
        abort(403)
    form = MovementForm()
    if form.validate_on_submit():
        movement.from_location = form.from_location.data
        movement.to_location = form.to_location.data
        movement.qty = form.qty.data
        movement.product = form.product.data
        db.session.commit()
        flash('The movement has been updated!', 'success')
        return redirect(url_for('movements.movement', movement_id=movement.movement_id))
    elif request.method == 'GET':
        form.from_location.data = movement.from_location
        form.to_location.data = movement.to_location
        form.product.data = movement.product
        form.qty.data = movement.qty
    return render_template('create_movement.html', title="Update Movement", form=form, legend='Update Movement')

@movements.route("/movement/<int:movement_id>/delete", methods=['POST'])
@login_required
def delete_movement(movement_id):
    movement = Movement.query.get_or_404(movement_id)
    if movement.creator != current_user:
        abort(403)
    db.session.delete(movement)
    db.session.commit()
    flash('The movement has been deleted', 'success')
    return redirect(url_for('movements.list_movements'))