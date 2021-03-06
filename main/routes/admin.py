from flask import render_template, session, request, redirect, url_for, flash
from sqlalchemy import or_
from main import app, db, bcrypt, vonage,  sms
from main.forms.admin import AdminRegistrationForm, AdminLoginForm
from main.models.admin import tblAdmins
from main.models.products import tblProducts, Brand, Category
from main.models.customers import tblOrders, tblCustomers
from main.routes.products import newordercount
import os


    


#admin account
@app.route('/admin/register', methods=['GET', 'POST'])
def register():
    form = AdminRegistrationForm(request.form)
    if request.method == 'POST' and form.validate():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        user = tblAdmins(name = form.name.data,
                    username = form.username.data, 
                    email = form.email.data,
                    password = hash_password)
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome {form.name.data} Thank you for registering','success')
        return redirect(url_for('login'))
    return render_template('admin/register.html', form=form, title='Registration Page')

@app.route('/admin/login', methods=['GET', 'POST'])
def login():
    form = AdminLoginForm(request.form)
    if request.method == "POST" and form.validate():
        user = tblAdmins.query.filter_by(email = form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['email'] = form.email.data
            session['name'] = user.name
            session['role'] = user.role
            session['profile'] = user.profile
            # flash(f'Welcome {user.name}, You are logged successfully')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Wrong password please try again!', 'danger') 
    return render_template('admin/login.html', form=form, title="Login Page")

@app.route('/admin/logout')
def logout():
    session.pop('email', None)
    session.pop('name', None)
    session.pop('role', None)
    session.pop('profile', None)
    return redirect(url_for('login'))


@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    products = tblProducts.query.all()
    return render_template('admin/index.html', title="Admin Portal", products=products, newordercount=newordercount())

@app.route('/admin/brands')
def brand():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html', title="Brand Page", brands=brands, newordercount=newordercount())

@app.route('/admin/categories')
def category():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html', title="Category Page", categories=categories, newordercount=newordercount())


@app.route('/orderlists')
def orderlists():
    if 'email' in session:
        orders = db.session.query(tblOrders, tblCustomers).join(tblCustomers).order_by(tblOrders.id.desc()).all()
        open = db.session.query(tblOrders, tblCustomers).join(tblCustomers).filter(or_(tblOrders.status=='New', tblOrders.status=='In-Progress')).order_by(tblOrders.id.desc()).all()
        completed = db.session.query(tblOrders, tblCustomers).join(tblCustomers).filter(tblOrders.status=='Completed').order_by(tblOrders.id.desc()).all()
        canceled = db.session.query(tblOrders, tblCustomers).join(tblCustomers).filter(tblOrders.status=='Canceled').order_by(tblOrders.id.desc()).all()
        openCount = db.session.query(tblOrders, tblCustomers).join(tblCustomers).filter(or_(tblOrders.status=='New', tblOrders.status=='In-Progress')).order_by(tblOrders.id.desc()).count()
        completedCount = db.session.query(tblOrders, tblCustomers).join(tblCustomers).filter(tblOrders.status=='Completed').order_by(tblOrders.id.desc()).count()
        canceledCount = db.session.query(tblOrders, tblCustomers).join(tblCustomers).filter(tblOrders.status=='Canceled').order_by(tblOrders.id.desc()).count()

    else:
        return redirect(url_for('customerLogin'))
    return render_template('admin/orders.html', orders=orders, open=open, completed=completed, canceled=canceled, openCount=openCount, completedCount=completedCount, canceledCount=canceledCount, newordercount=newordercount(), title = "Order Lists")

@app.route('/orderdetails/<invoice>')
def orderdetails(invoice):
    if 'email' in session:
        grandtotal = 0
        subtotal = 0
        orders = tblOrders.query.filter_by(invoice=invoice).order_by(tblOrders.id.desc()).first()
        customer = tblCustomers.query.filter_by(id=orders.customer_id).first()
        for _key, product in orders.orders.items():
            subtotal += float(product['price']) * int(product['quantity'])  
            discount = float(product['discount']) * int(product['quantity'])
            subtotal -= discount
            grandtotal = float("%.2f" % (1.00 * subtotal))
    else:
        return redirect(url_for('customerLogin'))
    return render_template('admin/orderdetails.html',
    invoice=invoice, customer=customer, subtotal=subtotal, grandtotal=grandtotal, orders=orders, newordercount=newordercount(), title = "Order Details")

@app.route('/acceptorder/<int:id>', methods=['POST'])
def acceptorder(id):
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    order = tblOrders.query.get_or_404(id)
    status = 'In-Progress'
    customer = tblCustomers.query.filter_by(id=order.customer_id).first()
    if request.method == "POST":
        order.status = status
        flash(f'You have accepted the order!','warning')
        db.session.commit()
        responseData = sms.send_message(
            {  
            "from": "Online Miners",
            "to": "+63" + str(customer.number) ,
            "text": f"Hi {customer.name}, Greetings from Online Miners we are now preparing your orders, Reference Number: {order.invoice} Thank you!",
            }
        )
        if responseData["messages"][0]["status"] == "0":
            print(f"Message sent successfully to {customer.number}")
        else:
            print(f"Message failed with error: {responseData['messages'][0]['error-text']}")
        return redirect(url_for('orderlists'))

@app.route('/completeorder/<int:id>', methods=['POST'])
def completeorder(id):
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    order = tblOrders.query.get_or_404(id)
    status = 'Completed'
    if request.method == "POST":
        order.status = status
        flash(f'You have completed the order!','success')
        db.session.commit()
        return redirect(url_for('orderlists'))

@app.route('/cancelorder/<int:id>', methods=['POST'])
def cancelorder(id):
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    order = tblOrders.query.get_or_404(id)
    status = 'Canceled'
    if request.method == "POST":
        order.status = status
        flash(f'You have completed the order!','success')
        db.session.commit()
        return redirect(url_for('orderlists'))