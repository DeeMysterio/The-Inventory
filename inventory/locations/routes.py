from flask import Blueprint
from flask import render_template, url_for, flash, redirect, request, abort
from flask_login import current_user, login_required
from inventory import db
from inventory.models import Location
from .forms import LocationForm

locations = Blueprint('locations', __name__)

@locations.route("/locations")
def list_locations():
    page = request.args.get('page', 1, type=int)
    locations = Location.query.paginate(page=page, per_page=10)
    return render_template('locations.html', locations=locations, title='Locations')


@locations.route("/location/<int:location_id>")
def location(location_id):
    location = Location.query.get_or_404(location_id)
    return render_template('location.html', title=location.name, location=location, legend='Location Details')

@locations.route("/location/new", methods=['GET', 'POST'])
@login_required
def new_location():
    form = LocationForm()
    if form.validate_on_submit():
        location = Location(name=form.name.data, address=form.address.data, creator=current_user)
        db.session.add(location)
        db.session.commit()
        flash_message = 'The Location has been added!'
        flash(flash_message, 'success')
        return redirect(url_for('locations.list_locations'))
    return render_template('create_location.html', title="New Location", form=form, legend='Add a new Location')

@locations.route("/location/<int:location_id>/update", methods=['GET', 'POST'])
@login_required
def update_location(location_id):
    location = Location.query.get_or_404(location_id)
    if location.creator != current_user:
        abort(403)
    form = LocationForm()
    if form.validate_on_submit():
        location.name = form.name.data
        location.address = form.address.data
        db.session.commit()
        flash('The location has been updated!', 'success')
        return redirect(url_for('locations.location', location_id=location.location_id))
    elif request.method == 'GET':
        form.name.data = location.name
        form.address.data = location.address
    return render_template('create_location.html', title="Update Location", form=form, legend='Update Location')

@locations.route("/location/<int:location_id>/delete", methods=['POST'])
@login_required
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)
    if location.creator != current_user:
        abort(403)
    db.session.delete(location)
    db.session.commit()
    flash('The location has been deleted', 'success')
    return redirect(url_for('locations.list_locations'))