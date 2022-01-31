from flask import render_template, session, request, redirect, url_for, flash, current_app, make_response
from flask_login import login_required, current_user, logout_user, login_user
from main import db, app, photos, search, bcrypt, login_manager
from main.forms.customers import CustomerRegisterForm, CustomerLoginForm
from main.models.customers import tblCustomers, tblOrders
from main.routes.products import brands, categories
import secrets, os, json, pdfkit


#customer account
@app.route('/register', methods=['POST', 'GET'])
def customer_register():
    form = CustomerRegisterForm(request.form)
    if form.validate_on_submit():
        hash_password = bcrypt.generate_password_hash(form.password.data)
        register = tblCustomers(name=form.name.data, username=form.username.data, email=form.email.data, password=hash_password, address=form.address.data, number=form.number.data)
        db.session.add(register)
        flash(f'Welcome {form.name.data}', 'success')
        db.session.commit()
        return redirect(url_for('customerLogin'))
    return render_template('customers/register.html', form=form, title = "Register")

@app.route('/login', methods=['POST','GET'])
def customerLogin():
    form = CustomerLoginForm()
    if form.validate_on_submit():
        user = tblCustomers.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash(f'You are successfully logged in {form.email.data}', 'success')
            next = request.args.get('next')
            return redirect(next or url_for('home'))
        flash(f'Incorrect email or password', 'danger')
        return redirect(url_for('customerLogin'))
    return render_template('customers/login.html', form=form, title = "Login")

@app.route('/logout')
def customerLogout():
    logout_user()
    return redirect(url_for('customerLogin'))


# customer order
@app.route('/getOrder')
@login_required
def get_order():
    if current_user.is_authenticated:
        customer_id = current_user.id
        invoice = secrets.token_hex(5)
        try:
            order = tblOrders(invoice=invoice, customer_id=customer_id, orders=session['Shoppingcart'])
            db.session.add(order)
            db.session.commit()
            flash(f'Your order has been sent','success')
            session.pop('Shoppingcart')
            return redirect(url_for('orders', invoice=invoice))
        except Exception as e:
            print(e)
            flash(f'Something went wrong', 'danger')
            return redirect(url_for('GetCart'))

@app.route('/orders/<invoice>')
@login_required
def orders(invoice):
    if current_user.is_authenticated:
        grandtotal = 0
        subtotal = 0
        customer_id = current_user.id
        customer = tblCustomers.query.filter_by(id=customer_id).first()
        orders = tblOrders.query.filter_by(customer_id=customer_id).order_by(tblOrders.id.desc()).first()
        for _key, product in orders.orders.items():
            subtotal += float(product['price']) * int(product['quantity'])  
            discount = float(product['discount']) * int(product['quantity'])
            subtotal -= discount
            grandtotal = float("%.2f" % (1.00 * subtotal))
    else:
        return redirect(url_for('customerLogin'))
    return render_template('customers/order.html', invoice=invoice, subtotal=subtotal, grandtotal=grandtotal, customer=customer, orders=orders,brands=brands(), categories=categories(), title = "Orders")


@app.route('/get_pdf/<invoice>', methods=['POST'])
@login_required
def get_pdf(invoice):
    if current_user.is_authenticated:
        grandtotal = 0
        subtotal = 0
        customer_id = current_user.id
        if request.method=="POST":
            customer = tblCustomers.query.filter_by(id=customer_id).first()
            orders = tblOrders.query.filter_by(customer_id=customer_id).order_by(tblOrders.id.desc()).first()
            for _key, product in orders.orders.items():
                subtotal += float(product['price']) * int(product['quantity'])  
                discount = float(product['discount']) * int(product['quantity'])
                subtotal -= discount
                grandtotal = float("%.2f" % (1.00 * subtotal))
            rendered = render_template('customers/pdf.html', invoice=invoice, subtotal=subtotal, grandtotal=grandtotal, customer=customer, orders=orders, brands=brands(), categories=categories())
            config = pdfkit.configuration(wkhtmltopdf='C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe')
            pdf = pdfkit.from_string(rendered, configuration=config)
            response = make_response(pdf)
            response.headers['content-Type']='application/pdf'
            response.headers['content-Disposition']='attached; filename='+invoice+'.pdf'
            return response
    return redirect(url_for('orders'))