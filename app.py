from flask import Flask, render_template, request, redirect, url_for , session, send_from_directory
from flask import Flask, redirect, session, url_for, request,render_template, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, Farms, Users, Products, Cart_items, Orders, Stores
from datetime import datetime
import sqlite3, os
from functools import wraps

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///Market.db"
app.config['SECRET_KEY'] = "random string"

db.init_app(app)
     
app.config['UPLOAD_FOLDER'] = '/static/image' #test

with app.app_context():
        db.create_all()

app.secret_key = 'f5746747a9b7fa1f5dd11963eaf8b22d45d691315703ff88d443bb0abf075c19'

current_datetime = datetime.now()

formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")

login_manager = LoginManager(app)

login_manager.init_app(app)

#xxxxxxxxxxxxxxxxxxxxxx

@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))

@app.route('/')
#@login_required
def home():
    session.clear()
    login_required
    return render_template('home.html')
    

def login_required(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))  # Redirect to login page if user is not logged in
        return route_function(*args, **kwargs)
    return decorated_function

def login_required(route_function):
    @wraps(route_function)
    def decorated_function(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('login'))  # Redirect to login page if user is not logged in
        return route_function(*args, **kwargs)
    return decorated_function

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name  = request.form.get('name')
        phone = request.form.get('phone')
        email = request.form.get('email')
        role  = request.form['role']
        password = request.form.get('password')

        # Check if the username already exists
        user = Users.query.filter_by(name=name).first()
        if user:
            flash('Username already exists. Please choose a different one.', 'danger')
            return redirect(url_for('signup'))
        else:
            # Create a new user
            new_user = Users(name=name, phone=phone, email=email, role=role)
            new_user.set_password(password)
            db.session.add(new_user)
            db.session.commit()

        flash('You have successfully registered. You can now log in.', 'success')
        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        name = request.form.get('name')
        password = request.form.get('password')
        user = Users.query.filter_by(name=name).first()
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    user = db.session.query(Users)\
        .filter(Users.name==current_user.name)\
        .first()
    
    farm= db.session.query(Farms)\
        .filter(Farms.user_id==user.id)\
        .first()
      
    if user.role=='owner':
        if user.name=='admin':
            return render_template('dashboard_admin.html')
        else:   
            if farm:
                return render_template('dashboard_owners.html', farm=farm )  
            else:
                return render_template('dashboard_new.html')  
    elif user.role=='customer':
            #return render_template('prod_list.html')
            return redirect(url_for('prod_list'))
    else: 
        if user.role=='business':
            return render_template('dashboard_store_owners.html')
            #return redirect(url_for('add_store'))
            
   
    return render_template('login.html')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

#reads all table records
def cart_table_count():
    count= db.session.query(Cart_items).count
    return count
    
#--Add owner/user----------------------------------------------------
# @app.route('/add_user')
# def add_user():
#         if current_user.name =="admin":
#             #return 'user added successfully' 
#             return render_template('add_user.html')
#         else: 
#             return ('You are not authorized')

@app.route('/delete_user/<int:user_id>', methods=['GET', 'POST']) 
def delete_user(user_id):
    user = db.session.query(Users).filter(Users.id==user_id).first()
    if user:
        db.session.delete(user)
        db.session.commit()
        return ('Farm Owner deleted sussfully')  
    else:
        return 'User not found', 404

    #return redirect(url_for('prod_list'))

# #----customers --------
@app.route('/users_list1') #owners list
def users_list1():
     #user = current_user.name
     title='Farm Owners'
     rows = db.session.query(Users).filter(Users.role=='owner').all()
     return render_template('users_list.html', rows=rows, title=title)

@app.route('/users_list2') #customers list
def users_list2():
     #user = current_user.name
     title='Registered Customers'
     rows = db.session.query(Users).filter(Users.role=='customer').all()
     return render_template('users_list.html', rows=rows, title=title)

  
@app.route('/add_product')
def add_product():
    items=db.session.query(Farms).all()
    #read farms for the farm selection dropdown
    return render_template('add_productB.html' , farms=items)    

@app.route('/add_productY<int:farm_id>') 
def add_productY(farm_id):
    name = current_user.name
    farm = db.session.query(Farms).filter(Farms.id==farm_id).first()
   
    # rows=db.session.query(Products).filter(Products.)
    # rows = add_product(farm_id)
    return render_template('add_productY.html' , farm = farm )    
    #return 'ok'
#--Add product to products table

@app.route('/submit', methods=['POST'])
def submit():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")

    farm_id        = request.form['farm_id']
    prod_category  = request.form['prod_category']
    prod_name      = request.form['prod_name']
    package        = request.form['package']
    unit_price     = request.form['unit_price']
    stock          = request.form['stock']
    #event_datetime = request.form['event_datatime'] 
    event_datetime = formatted_datetime                
    
    uploaded_files = request.files.getlist('image_path')
    
    #item_folder = os.path.join("static/images", farm_id)
#----------------------
#    if not os.path.exists(item_folder):
 #      os.makedirs(item_folder)
 #      print(f"item folder '{farm}' created successfully.")
 #   else:
 #       print(f"User folder '{farm}'already exists.")
 #   saved_files = [] # emplty list/array to get list of data
    
    for file in uploaded_files:
            filename = file.filename
            if len(filename)>0 :
                #file.save(os.path.join('static/images/' +'/'+ farm_id +'/'+ filename))
                file.save(os.path.join('static/images/'+filename))
    print(filename,'xxxxxxxxxxxxxxxxxxx')

    products=Products(farm_id=farm_id, prod_category=prod_category, prod_name=prod_name, package=package, unit_price=unit_price, filename=filename, stock=stock, event_datetime=event_datetime)
    
    db.session.add(products)
    db.session.commit()
    return "Record saved successfully"
#    return render_template('add_productY.html', rows=rows)

#-----------update products data base table
@app.route('/update_product' , methods=['POST']) 
def update_product():  
    item_id=request.form['id']
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
    
    product=Products.query.filter_by(id=item_id).first()
    try:
        product.farm_id         = request.form['farm_id']
        product.prod_category   = request.form['prod_category']
        product.prod_name       = request.form['prod_name']
        product.package         = request.form['package']
        product.unit_price      = request.form['unit_price']
        #product.filename        = request.form['filename']
        product.stock           = request.form['stock']
        product.event_datetime  = formatted_datetime    
        
        db.session.commit()

        return 'data updated ok'
    except sqlite3.IntegrityError:
       return 'Entry already exists! ... please try again'

#--------function to edit and update products in products table 
@app.route('/edit_product/<int:item_id>') 
def edit_product(item_id):
    product=db.session.query(Products)\
    .filter(Products.id==item_id)\
    .first()
    return render_template('edit_product.html', item=product)
    
@app.route('/delete_product/<int:item_id>') 
#@login_required
def delete_product(item_id):
    product = db.session.query(Products).filter_by(id=item_id).first()
    if product:
        db.session.delete(product)
        db.session.commit()
        return ('Product deleted sussfully')  
    else:
        return 'User not found', 404

@app.route('/previous')
def previous():
    return render_template('previous.html')

#------Test prod-y-------List all products on "products page"-------visitors
@app.route('/prod_list')  
def prod_list():
    farms = db.session.query(Farms).all()
    products=db.session.query(Products).all()
    prods = db.session.query(Products, Farms) \
        .order_by(Products.event_datetime.desc())\
        .join(Farms) \
        .all() 
    return render_template('products.html', prods=prods ,farms=farms, products=products )


  #  return redirect(request.referrer)

    #return 'ok'
    
#------list all products ---------admin user
@app.route('/prod_list1/')  
def prod_list1():
    products = db.session.query(Products, Farms) \
        .join(Farms) \
        .all()
   
    return render_template('prod_list.html', products=products)

#------List farm products for owner -----------------
@app.route('/prod_list2/<int:farm_id><name>')  #farm products
def prod_list2(farm_id, name):
    name1=current_user.name
    products = db.session.query(Products, Farms) \
        .join(Farms) \
        .filter(Products.farm_id == farm_id) \
        .all()
    return render_template('prod_list.html', name=name, products=products)

#-------------Products list for selected farm ------------
@app.route('/prod_list_by_farm', methods=['GET', 'POST'])   
def prod_list_by_farm():
    Fx=request.form['options']
    prods=db.session.query(Products, Farms)\
        .join(Farms) \
        .filter(Products.farm_id==Fx) \
        .all()
    return render_template('prod_list_a.html', prods=prods)


#-------------Products list for selected farm ------------
@app.route('/prod_list_by_products', methods=['GET', 'POST'])   
def prod_list_by_products():
    Fx=request.form['options']
    prods=db.session.query(Products, Farms)\
        .join(Farms) \
        .filter(Products.prod_category==Fx) \
        .all()
    return render_template('prod_list_a.html', prods=prods)


#--------Products list matches selected category-----------
# @app.route('/prod_list_by_products', methods=['GET', 'POST'])   
# def prod_list_by_products():
#     Fx=request.form['options']
#     print("options")
#     prods=db.session.query(Products, Farms)\
#         .join(Farms) \
#         .filter(Products.prod_category=='options') \
#         .all()  
#     return render_template('prod_list_a.html', prods=prods)

@app.route('/search_by_product')  ## selection dropdown 
def search_by_product():
    products = db.session.query(Products).all()
    for product in products:
            print(f"Products: {product.prod_category} ")
    return render_template('search-input-products.html', products=products)

@app.route('/search_by_farm')  # selection dropdown 
def search_by_farm():
    farms = db.session.query(Farms).all()
    for farm in farms:
            print(f"Farms: {farm.name} ")
    return render_template('search-input-farm.html', farms=farms)

@app.route('/view_image/<int:item_id>') #Not used
def view_image(item_id):

    # conn    = sqlite3.connect('Market.db')
    # cursor  = conn.cursor()
    # cursor.execute("SELECT * FROM products WHERE id=?", (item_id,))
    # #cursor.execute("UPDATE entries SET name=?, email=? WHERE id=?", (user_id,))
    # record= cursor.fetchone()
    # photo=record[7] 
    # prod_name=record[3]
    # conn.commit()
    # conn.close()
    record = db.session.query(Products).filter(Products.id==item_id).first()
    photo = record.filename
    prod_name = record.prod_name

    return render_template('view_image.html', prod_name=prod_name, photo=photo )

@app.route('/add_store')
def add_store():
    user = current_user.name
    store=db.session.query(Stores).filter(Stores.user_id==Users.id)
    user =db.session.query(Users)\
         .filter(Users.name==user)\
         .filter(Users.role=='business')\
         .first()   

    return render_template('add_store.html', store=store, user=user)    


@app.route('/show_store_adv')
def show_store_adv():
    user = current_user.name
    store = db.session.query(Stores)\
        .filter(Stores.user_id==Users.id)\
        .all()
        
    return render_template('page-1.html', store=store, user=user)    
 

@app.route('/store_list_by_activity' , methods=['GET', 'POST'])
def store_list_by_activity():
    #user = current_user.name
    activity = request.form['activity']
    store = db.session.query(Stores)\
        .filter(Stores.activity==activity)\
        .all()

    # if store.adv_class == "A":
    #     return render_template('page-1.html', store=store, user=user)    
    # elif store.adv_class == "B":
    #     return render_template('page-2.html', store=store, user=user)   
    # else:
    #     return render_template('page-3.html', store=store, user=user)    
 
    return render_template('page-3.html', store=store)    


@app.route('/save_store', methods=['POST'])
def save_store():
    store_name =request.form['store_name']
    user_id =request.form['user_id']
    phone1  =request.form['phone1']
    phone2  =request.form['phone2']
    address =request.form['address']
    activity =request.form['activity']
    adv_class=request.form['adv_class']
        
    uploaded_files = request.files.getlist('image_path')
   
    for file in uploaded_files:
         filename = file.filename
         if len(filename)>0 :
             file.save(os.path.join('static/images/'+filename))
         else :   print('error')
    if request.method == 'POST':
        newStore = Stores( user_id, store_name, activity, phone1, phone2, address, filename, adv_class)
        db.session.add(newStore)
        db.session.commit()
        return 'Store saved successfully'
    

@app.route('/add_farm')
def add_farm():
    user = current_user.name
    user=db.session.query(Users)\
         .filter(Users.name==user)\
         .filter(Users.role=='owner')\
         .first()   
   
    return render_template('add_farm.html', owner=user)    
    #else: return ('not authorized')

@app.route('/edit_farm/<int:farm_id>') 
def edit_farm(farm_id):
    user=db.session.query(Farms).filter(Farms.id==farm_id).first()
    return render_template('edit_farm.html', user=user)

@app.route('/delete_farm/<int:farm_id>') 
@login_required
def delete_farm(farm_id):
    farm=db.session.query(Farms).filter(Farms.id==farm_id).first()
    if farm:
        db.session.delete(farm)
        db.session.commit()
        return ('Delete record successfully')
    else:
        return 'User not found', 404
    
    
@app.route('/farm_list_admin') #original fun
def farm_list_admin():
    #farms = db.session.query(table1, table2).join(table2).all()
    farms = db.session.query(Farms, Users) \
        .join(Users) \
        .filter(Users.role=='owner')\
        .all()
    
    #for farm, owner in farms:
    #    print(f"Farms: {farm.name}, Owners: {owner.name}")
    
    #return render_template('farm_list.html', rows = Farms.query.all())
    return render_template('farm_list.html', farms = farms)
   
    
  #-------------------Edit/add Farm Record------------------------   
@app.route('/add_new_farm', methods=['POST'])
def add_new_farm():
    try:
        name        =request.form['name']
        owner_id    =request.form['owner_id']
        phone       =request.form['phone']
        email       =request.form['email']
        address1    =request.form['address1']
        address2    =request.form['address2']
        newFarm= Farms( name, owner_id, phone, email, address1, address2)
        COUNT=db.session.query(Farms)\
            .filter(Farms.name=='%'+name+'%')\
            .count()
        db.session.add(newFarm)
        db.session.commit()

        if COUNT >0 :
            return ('farm name exists! please select another name ') 
        else:
            db.session.add(newFarm)
            db.session.commit()
        return 'Farm saved successfully'
    except sqlite3.IntegrityError:
        return ('Error !')
       
    #return 'Entry already exists in the database ... please try again!'
      #  return redirect(url_for('add_farm'), error='not unique value')

@app.route('/update_farm', methods=['POST'])
#@login_required
def update_farm():
        id=request.form['id']
        farm=db.session.query(Farms).filter(Farms.id==id)
        farm.id      =request.form['id']
        farm.name    =request.form['name']
        farm.owner   =request.form['owner']
        farm.phone   =request.form['phone']
        farm.email   =request.form['email']
        farm.address1 =request.form['address1']
        farm.address2 =request.form['address2']
    
        db.session.commit()
        return ('Farm record modified ok')


#xxxxxxxxxxxxxx CART xxxxxxxxxxxx
@app.route('/cart_items_db', methods=['GET', 'POST']) #---ok
def cart_items_db():
    page = request.args.get('/page', 1, type=int)
    per_page = 1
    start_index = (page - 1) * per_page
    current_page = page
    user = current_user.name

    row = db.session.query(Cart_items, Products, Farms, Users) \
        .join(Products, Cart_items.product_id==Products.id) \
        .join(Farms, Cart_items.farm_id==Farms.id) \
        .join(Users, Cart_items.user_id==Users.id) \
        .first()
    
    total_records = db.session.query(Cart_items)\
          .filter(Cart_items.buyer_id==Users.id)\
          .count()

    buyer=db.session.query(Users)\
          .filter(Users.name==current_user.name)\
          .first()

    # total_records = db.session.query(Cart_items)\
    #       .filter(Cart_items.buyer_id==Buyers.id)\
    #       .count()

    # row=db.session.query(Cart_items)\
    #      .first()

    # return render_template('cart_items2_db.html', row=row
    #                        )
    return render_template('cart_items2_db.html', total_records=total_records, row=row, current_page=current_page, user=user)


#--list for all cart items - admin
@app.route('/cart_items_list') #---ok
def cart_items_list():
    rows = db.session.query(Cart_items, Products, Farms, Users) \
        .join(Products, Cart_items.product_id==Products.id) \
        .join(Farms, Cart_items.farm_id==Farms.id) \
        .join(Users, Cart_items.user_id==Users.id) \
        .all()
    
    return render_template('cart_items_list.html', rows=rows)
    #return('ok')

#--list for cart items - buyer
@app.route('/cart_items_list1') #-- ok
def cart_items_list1():
    username=current_user.name

    user=db.session.query(Users)\
         .filter(Users.name==username)\
         .first() 

    farms = db.session.query(Farms).all()
    
    items = db.session.query(Cart_items, Farms, Products) \
        .join(Farms, Cart_items.farm_id==Farms.id ) \
        .join(Products, Cart_items.product_id==Products.id) \
        .filter(Cart_items.user_id==user.id)\
        .all()
   
    return render_template('cart_items_list1.html',  items=items, farms=farms, user=user)
                           
           
#---cart items for farm owners ---    
@app.route('/cart_items_list2/<farm_id>') #-- ok
def cart_items_list2(farm_id):

    buyers = db.session.query(Users)\
        .filter(Users.role=='customer').all()

    farms = db.session.query(Farms)\
         .filter(Farms.id==farm_id)\
         .first()
    
    print(farm_id,'xxxx')
    items = db.session.query(Cart_items, Products, Users) \
            .join( Products) \
            .join( Users) \
            .filter(Cart_items.farm_id==Farms.id)\
            .all()

    return render_template('cart_items_list2.html', items=items, buyers=buyers , farms=farms)

@app.route('/add_to_cart/<int:item_id>', methods=['GET', 'POST'])
def add_to_cart(item_id):
    products = db.session.query(Products) \
          .join(Farms, Products.farm_id==Farms.id)\
          .filter(Products.id==item_id)\
          .first()
    farms=db.session.query(Farms)\
        .filter(Farms.id==products.farm_id)\
        .first()
    buyers=db.session.query(Users).filter(Users.name == current_user.name).first()
    return render_template('add_to_cart.html', products=products, buyers=buyers, farms=farms)

#--------add new items to cart table ?
@app.route('/add_to_cartY' , methods=['GET', 'POST']) #OK
def add_to_cartY():
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
    try:
        buyer_id      = request.form['buyer_id']
        farm_id       = request.form['farm_id']
        product_id    = request.form['id']
        quantity      = request.form['quantity']
        package       = request.form['package']
        unit_price    = request.form['unit_price']
        filename      = request.form['filename']
        event_datetime =formatted_datetime
        order_status  = 'Pending'
        cart_item = Cart_items(buyer_id, farm_id, product_id, quantity,  package, unit_price, filename, event_datetime, order_status)
        db.session.add(cart_item)
        db.session.commit()
        return ('item saved successfully ')
    except sqlite3.IntegrityError:
           return 'Entry error in the database ... please try again!'

@app.route('/edit_cart/<int:item_id>')
#@login_required
def edit_cart(item_id):

    buyer = current_user.name
    
    # formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
    # event_datetime=formatted_datetime
          
    items=db.session.query(Cart_items)\
        .filter(Cart_items.id==item_id)\
        .first()

    products=db.session.query(Products)\
        .filter(Products.id==Cart_items.product_id )\
        .first()
    
    buyers=db.session.query(Users)\
        .filter(Users.id==items.buyer_id)\
        .first()      
    
    farms=db.session.query(Farms)\
        .filter(Farms.id==Cart_items.farm_id)\
        .first()
    
    owners=db.session.query(Users)\
        .filter(Users.id==farms.owner_id)\
        .first()
    
    return render_template('edit_cart.html', owners=owners, items=items, products=products, buyers=buyers, farms=farms)


#---update existing items in table
@app.route('/update_cart' , methods=['GET', 'POST']) 
def update_cart():  
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M")
    # event_datetime=formatted_datetime
    
    id=request.form['id']
    items=db.session.query(Cart_items).filter(Cart_items.id==id).first()
    
    items.buyer_id        = request.form['buyer_id']
    items.farm_id         = request.form['farm_id']
    items.product_id      = request.form['product_id']
    items.quantity        = request.form['quantity']
    items.package         = request.form['package']
    items.unit_price      = request.form['unit_price']
    items.filename        = request.form['filename']

    items.event_datetime  = formatted_datetime    
    items.order_status    = request.form['order_status']
    db.session.commit()
    return ('Cart items updated successfully ')


@app.route('/delete_item_from_cart/<int:item_id>') 
def delete_item_from_cart(item_id):
    item = db.session.query(Cart_items).filter_by(id=item_id).first()
    if item:
        db.session.delete(item)
        db.session.commit()
        return ('item deleted sussfully')  # Redirect to a list of users
    else:
        return 'User not found', 404
    
#xxxxxxxxxxxxxxxxxxxxxxxx
@app.route('/order_status') 
def order_status():
   return('order status')


@app.route('/create_purchase_order1', methods =['GET', 'POST']) 
def create_purchase_order1():
    pass
    farm = request.form['item-dropdown'] #selected farm
    buyer= request.form['user']
    
    print('Farm:', farm)
    print('Buyer:', buyer)
    
    rows = db.session.query(Orders).count()
    current_date = datetime.now().strftime('%Y%m%d')
    current_time = datetime.now().strftime('%H%M')
    order_no ='PO'+'-'+ current_time +'-'+ str(rows+1)
    order_date = current_date

    buyers = db.session.query(Users)\
        .filter(Users.name==buyer)\
        .first() 
        
    farms = db.session.query(Farms)\
        .filter(Farms.name==farm)\
        .first() 
     
    products = db.session.query(Products)\
         .all() 
     
    items = db.session.query(Cart_items, Products) \
        .join(Products, Cart_items.product_id==Products.id) \
        .filter(Cart_items.farm_id==farms.id)\
        .filter(Cart_items.user_id==buyers.id)\
        .all()

    return render_template('purchase_order.html', items=items,  farms=farms, buyers=buyers, products=products, order_no=order_no, order_date=order_date)


@app.route('/create_purchase_order2', methods =['GET', 'POST']) 
def create_purchase_order2():
    pass
    buyer = request.form['item-dropdown'] #selected farm
    farm  = request.form['farm']

    rows = db.session.query(Orders).count()
    current_date = datetime.now().strftime('%Y%m%d')
    current_time = datetime.now().strftime('%H%M')
    order_no ='PO'+'-'+ current_time +'-'+ str(rows+1)
    order_date = current_date

    buyers = db.session.query(Users)\
         .filter(Users.name==buyer)\
         .first() 
  
    farms = db.session.query(Farms)\
         .filter(Farms.name == farm)\
         .first() 
    
    products = db.session.query(Products)\
         .all() 
    
    items = db.session.query(Cart_items, Products) \
        .join(Products)\
        .filter(Cart_items.user_id==buyers.id)\
        .all()
    
    return render_template('purchase_order.html', items=items, farms=farms, buyers=buyers, products=products, order_no=order_no, order_date=order_date)
    

@app.route('/save_order', methods =['GET', 'POST'] ) #------Saves order form to DB file->
def save_order():
    order_no  =request.form['order_no']
    order_date=request.form['order_date']
    order_farm=request.form['order_farm']
    order_buyer=request.form['order_buyer']
    return render_template('save_order.html', order_no=order_no,    
                           order_date=order_date, order_farm=order_farm, order_buyer=order_buyer )

@app.route('/save_order1', methods =['GET', 'POST'] )
def save_order1():
    order_no  =request.form['order_no']
    order_date=request.form['order_date']
    order_farm=request.form['order_farm']
    order_buyer=request.form['order_buyer']

    uploaded_files = request.files.getlist('image_path')
    for file in uploaded_files:
        filename = file.filename
        if len(filename)>0 :
            file.save(os.path.join('static/images/'+filename))
    #order_copy= filename
    if request.method == 'POST':
        order_no = request.form['order_no']
        order_date = request.form['order_date']
        order_farm = request.form['order_farm']
        order_buyer = request.form['order_buyer']
        order = Orders(order_no, order_date, order_farm, order_buyer, filename)
        db.session.add(order)
        db.session.commit()

    flash('Record was successfully added')
    #return render_template('save_order.html')  
    return redirect(url_for('home'))

@app.route('/view_order/<int:order_id>')
def view_order(order_id):
    row = db.session.query(Orders)\
        .filter(Orders.id == order_id)\
        .first() 
    return render_template('view_order.html', row=row)

@app.route('/view_orders_list')
def view_orders_list():
    buyer=current_user.name
    order=db.session.query(Orders).filter(Orders.order_buyer==buyer).all()
    return render_template('orders_list.html', s=order)


@app.route('/view_orders_list_F/<int:farm_id>')
def view_orders_list_F(farm_id):
    #buyer=current_user.name
    farm=db.session.query(Farms).filter(Farms.id==farm_id).first()
    #order=db.session.query(Orders).filter(Orders.order_buyer==buyer).all()
    order=db.session.query(Orders).filter(Orders.order_farm==farm.name).all()
    
    return render_template('orders_list.html', s=order)

@app.route('/delete_order/<int:order_id>', methods=['GET', 'POST']) 
def delete_order(order_id):
    order=db.session.query(Orders).filter(Orders.id==order_id).first()
    db.session.delete(order)
    db.session.commit()
    return 'order deleted'

#----------------Galary -------
@app.route('/image_area')
def image_area():
    return render_template('image_area.html')
  
@app.route('/view_gallery_images')
def view_gallery_images():
    image_folder = 'static/images' 
    image_files = os.listdir(image_folder)
    return render_template('view_gallery.html', image_files=image_files)

@app.route('/images/<path:filename>')
def get_image(filename):
    image_folder ='static/images-prod/'  
    return send_from_directory(image_folder, filename)


@app.route('/map-page')
def map():
    return render_template('map-page.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/page1')
def page1():
    return render_template ('page1.html')

@app.route('/page2')
def page2():
    return render_template ('page2.html')

@app.route('/page3')
def page3():
    return render_template ('page3.html')

@app.route('/page4')
def page4():
    return render_template ('page4.html')

@app.route('/page5')
def page5():
    return render_template ('page5.html')

@app.route('/complain1')
def complain1():
    return render_template ('complain1.html')



if __name__ == '__main__':
       app.run(debug=True)

#  if name == "__main__":
#       app.run(debug=true)

# if __name__ == "__main__":
#     app.run(host="127.0.0.1", port=5000, debug=True)