from flask import render_template, session, request, redirect, url_for, flash
from main import app, db, bcrypt
from main.forms.admin import AdminRegistrationForm, AdminLoginForm
from main.models.admin import tblAdmins
from main.models.products import tblProducts, Brand, Category
from main.models.customers import tblOrders, tblCustomers
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
            session['profile'] = user.profile
            # flash(f'Welcome {user.name}, You are logged successfully')
            return redirect(request.args.get('next') or url_for('admin'))
        else:
            flash('Wrong password please try again!', 'danger') 
    return render_template('admin/login.html', form=form, title="Login Page")

@app.route('/admin/logout')
def logout():
    session.pop('email', None)
    return redirect(url_for('login'))


@app.route('/admin')
def admin():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    products = tblProducts.query.all()
    return render_template('admin/index.html', title="Admin Portal", products=products)

@app.route('/brands')
def brand():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    brands = Brand.query.order_by(Brand.id.desc()).all()
    return render_template('admin/brand.html', title="Brand Page", brands=brands)

@app.route('/category')
def category():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    categories = Category.query.order_by(Category.id.desc()).all()
    return render_template('admin/brand.html', title="Category Page", categories=categories)

@app.route('/orderlists')
def orderlists():
    if 'email' in session:
        orders = tblOrders.query.order_by(tblOrders.id.desc()).all()
        # customer = tblCustomers.query.filter_by(id=orders.customer_id).order_by(tblCustomers.id.desc()).first()
        # for _key, product in orders.orders.items():
    else:
        return redirect(url_for('customerLogin'))
    return render_template('admin/orders.html', orders=orders, title = "Order Lists")

@app.route('/orderdetails/<invoice>')
def orderdetails(invoice):
    if 'email' in session:
        grandtotal = 0
        subtotal = 0
        orders = tblOrders.query.order_by(tblOrders.id.desc()).first()
        customer = tblCustomers.query.filter_by(id=orders.customer_id).first()
        for _key, product in orders.orders.items():
            subtotal += float(product['price']) * int(product['quantity'])  
            discount = float(product['discount']) * int(product['quantity'])
            subtotal -= discount
            grandtotal = float("%.2f" % (1.00 * subtotal))
    else:
        return redirect(url_for('customerLogin'))
    return render_template('admin/orderdetails.html', invoice=invoice, customer=customer, subtotal=subtotal, grandtotal=grandtotal, orders=orders, title = "Order Details")

