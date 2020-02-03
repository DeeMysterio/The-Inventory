from datetime import datetime
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app
from inventory import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    products = db.relationship('Product', backref='creator', lazy=True)
    locations = db.relationship('Location', backref='creator', lazy=True)
    movements = db.relationship('Movement', backref='creator', lazy=True)


    def get_reset_token(self, expires_sec=1800):
        s = Serializer(current_app.config['SECRET_KEY'], expires_sec)
        return s.dumps({'user_id': self.id}).decode('utf-8')

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return self.username


class Product(db.Model):
    product_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    movements = db.relationship("Movement", backref='product')
    location_id = db.Column(db.Integer, db.ForeignKey('location.location_id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        product_name = self.name
        if self.warehouse:
            warehouse = self.warehouse
            qty = warehouse.get_product_quantity(product_name)
            return "{0}:{1}{2}".format(product_name, warehouse, qty)
        return product_name


class Location(db.Model):
    location_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    address = db.Column(db.Text, nullable=False)
    products = db.relationship("Product", backref='warehouse')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return "{0}({1})".format(self.name, self.get_total_stock())

    def get_product_quantity(self, product_name):   
        qty = 0
        for product in self.products:
            if product_name in product.name:
                qty+=1
        return qty

    def get_total_stock(self):
        return len(self.products)
    

class Movement(db.Model):
    movement_id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    from_location_id = db.Column(db.Integer, db.ForeignKey("location.location_id"))
    to_location_id = db.Column(db.Integer, db.ForeignKey("location.location_id"))
    from_location = db.relationship(Location, lazy='joined', foreign_keys=[from_location_id], backref='from_location')
    to_location = db.relationship(Location, lazy='joined', foreign_keys=[to_location_id], backref='to_location')
    product_id = db.Column(db.Integer, db.ForeignKey('product.product_id'))
    qty = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)


    def __repr__(self):
        return str(self.movement_id)

