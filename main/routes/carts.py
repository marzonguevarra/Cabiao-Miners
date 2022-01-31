from flask import render_template, session, request, redirect, url_for, flash, current_app
from flask_login import login_required
from main import db, app
from main.models.products import tblProducts
from main.routes.products import brands, categories
import json

def MagerDicts(dict1, dict2):
    if isinstance(dict1, list) and isinstance(dict2, list):
        return dict1 + dict2
    elif isinstance(dict1, dict) and isinstance(dict2, dict):
        return dict(list(dict1.items()) + list(dict2.items()))
    return False

@app.route('/carts')
def GetCart():
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    subtotal = 0
    grandtotal = 0
    for key, product in session['Shoppingcart'].items():
        subtotal += float(product['price']) * int(product['quantity'])  
        discount = float(product['discount']) * int(product['quantity'])
        subtotal -= discount
        grandtotal = float("%.2f" % (1.00 * subtotal))
    return render_template('products/carts.html', title = "Carts", grandtotal=grandtotal, brands=brands(), categories=categories())
    
@app.route('/addcart', methods=['POST'])
def AddCart():
    try:
        product_id = request.form.get('product_id')
        quantity = int(request.form.get('quantity'))
        color = request.form.get('colors')
        product = tblProducts.query.filter_by(id=product_id).first()
        if request.method == "POST":
            DictItems = {product_id:{'name': product.name, 'price':float(product.price), 'discount': float(product.discount),
            'color':color, 'quantity': quantity, 'image': product.image_1, 'colors':product.colors, 'stock':product.stock}}
            if 'Shoppingcart' in session:
                print(session['Shoppingcart'])
                if product_id in session['Shoppingcart']:
                    session.modified = True
                    for key, item in session['Shoppingcart'].items():
                        if int(key) == int(product_id):
                            item['quantity'] += 1
                            flash(f"{item['quantity']} {product.name} has been added in your cart",'success')

                else:
                    session['Shoppingcart'] = MagerDicts(session['Shoppingcart'], DictItems)
                    flash(f"{product.name} successfully added in your cart",'success')
                    return redirect(request.referrer)              
            else:
                session['Shoppingcart'] = DictItems
                flash(f"{product.name} successfully added in your cart",'success')
                return redirect(request.referrer)
    except Exeption as e:
        print(e)
    finally:
        return redirect(request.referrer)    

@app.route('/updatecart/<int:code>', methods=['POST'])
@login_required
def updatecart(code):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    if request.method == "POST":
        quantity = request.form.get('quantity')
        color = request.form.get('color')
        try:
            session.modified = True
            for key, item in session['Shoppingcart'].items():
                if int(key) == code:
                    item['quantity'] = quantity
                    item['color'] = color
                    flash(f'Item is updated successfully', 'success')
                    return redirect(url_for('GetCart'))
        except Exception as e:
            print(e)
            flash(f'Error updating the Item', 'danger')
            return redirect(url_for('GetCart'))

@app.route('/deleteitem/<int:id>')
@login_required
def deleteitem(id):
    if 'Shoppingcart' not in session or len(session['Shoppingcart']) <= 0:
        return redirect(url_for('home'))
    try:
        session.modified = True
        for key, item in session['Shoppingcart'].items():
            if int(key) == id:
                session['Shoppingcart'].pop(key, None)
                return redirect(url_for('GetCart'))
    except Exception as e:
        print(e)
        return redirect(url_for('GetCart'))

@app.route('/clearcart')
def clearcart():
    try:
        session.pop('Shoppingcart', None)
        return redirect(url_for('home'))
    except Exception as e:
        print(e)