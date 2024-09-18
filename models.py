from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
#from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin 
from werkzeug.security import generate_password_hash, check_password_hash


db = SQLAlchemy()

class Users(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name  = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20))
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'customer' or 'owner'
    password_hash = db.Column(db.String(100), nullable=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


    def __init__(self, name, phone, email, role):
        self.name = name
        self.phone = phone        
        self.email = email
        self.role = role

    def __repr__(self):
        return f'<Users {self.email}, Role: {self.role}>'

class Farms(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  name = db.Column(db.String(100))
  user_id = db.Column(db.Integer, db.ForeignKey('users.id')) 
  phone = db.Column(db.String(20))
  email = db.Column(db.String(50)) 
  address1 = db.Column(db.String(100))
  address2 = db.Column(db.String(100))
  products = db.relationship('Products', backref='farm', lazy='dynamic')

  def __init__(self, name, user_id, phone, email, address1, address2):
      self.name = name
      self.user_id = user_id
      self.phone = phone
      self.email = email
      self.address1 = address1
      self.address1 = address2


class Products(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'))
  prod_category = db.Column(db.String(100))
  prod_name = db.Column(db.String(100))
  package = db.Column(db.String(10))
  unit_price = db.Column(db.Integer) 
  filename = db.Column(db.String(30))
  stock = db.Column(db.Integer)
  event_datetime = db.Column(db.String)
  
  def __init__(self, farm_id, prod_category,prod_name, package, unit_price,filename, stock, event_datetime):
      self.farm_id = farm_id
      self.prod_category = prod_category
      self.prod_name = prod_name
      self.package = package
      self.unit_price = unit_price
      self.filename = filename
      self.stock = stock
      self.event_datetime = event_datetime
 
class Cart_items(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  farm_id = db.Column(db.Integer, db.ForeignKey('farms.id'))
  product_id = db.Column(db.Integer, db.ForeignKey('products.id'))
  quantity = db.Column(db.Integer) 
  package = db.Column(db.String(10))
  unit_price = db.Column(db.Integer)
  filename = db.Column(db.String(30))
  event_datetime = db.Column(db.String(50))
  order_status = db.Column(db.String(5))

  users = db.relationship("Users", backref="cart_items")
  products = db.relationship("Products", backref="cart_items")
  farms = db.relationship("Farms", backref="cart_items")

  def __init__(self, user_id, farm_id, product_id, quantity, package, unit_price, filename, event_datetime, order_status):
      self.user_id = user_id
      self.farm_id = farm_id
      self.product_id = product_id
      self.quantity = quantity
      self.package = package
      self.unit_price = unit_price
      self.file_name = filename
      self.event_datetime = event_datetime
      self.order_status = order_status
      

class Orders(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  order_no = db.Column(db.String(30))
  order_date = db.Column(db.String(50))
  order_farm = db.Column(db.String(10))
  order_user = db.Column(db.String(10))
  order_copy = db.Column(db.String(20))
   
  def __init__(self, order_no, order_date, order_farm, order_user, order_copy):
    self.order_no = order_no
    self.order_date = order_date
    self.order_farm = order_farm
    self.order_user = order_user
    self.order_copy = order_copy

class Stores(db.Model):
  id = db.Column(db.Integer, primary_key = True)
  user_id=db.Column(db.Integer)
  store_name = db.Column(db.String(50))
  activity = db.Column(db.String(50))
  phone1 = db.Column(db.String(10))
  phone2 = db.Column(db.String(10))
  address = db.Column(db.String(50))
  filename = db.Column(db.String(50))
  adv_class=db.Column(db.String(10))

  def __init__(self, user_id, store_name, activity, phone1, phone2, address, filename, adv_class):
    self.user_id = user_id
    self.store_name = store_name
    self.activity = activity
    self.phone1 = phone1
    self.phone2 = phone2
    self.address = address
    self.filename = filename
    self.adv_class = adv_class
    
