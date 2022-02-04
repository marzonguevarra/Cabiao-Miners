from flask import render_template, session, request, redirect, url_for, flash, current_app
from main import db, app, photos, search
from main.models.products import Brand, Category, tblProducts
from main.models.customers import tblOrders, tblCustomers
from main.forms.products import ProductForm
import secrets, os

def brands():
    brands = Brand.query.join(tblProducts,(Brand.id == tblProducts.brand_id)).all()
    return brands

def categories():
    categories = Category.query.join(tblProducts,(Category.id == tblProducts.category_id)).all()
    return categories

def newordercount():
    newordercount = db.session.query(tblOrders, tblCustomers).join(tblCustomers).filter(tblOrders.status=='New').order_by(tblOrders.id.desc()).count()
    return newordercount

@app.route('/')
def home():
    page = request.args.get('page',1, type=int)
    products = tblProducts.query.filter(tblProducts.stock > 0).order_by(tblProducts.id.desc()).paginate(page=page, per_page=8)
    return render_template('products/index.html', products=products, brands=brands(), categories=categories(), title = "Online Miners ")

@app.route('/result')
def result():
    searchword = request.args.get('q')
    products = tblProducts.query.msearch(searchword, fields=['name','description'], limit=3)
    return render_template('products/result.html', products=products, brands=brands(), categories=categories() , title = "Online Miners | " + searchword) 


@app.route('/productdetails/<int:id>')
def getproductdetails(id):
    product = tblProducts.query.get_or_404(id)
    get_product = tblProducts.query.filter_by(id=id).first_or_404()
    return render_template('products/productdetails.html', product=product, brands=brands(), categories=categories(), get_product=get_product, title = "Online Miners | " + get_product.name) 


@app.route('/filterbybrand/<int:id>')
def getbrandfilter(id):
    page = request.args.get('page',1, type=int)
    get_brand = Brand.query.filter_by(id=id).first_or_404()
    brand = tblProducts.query.filter_by(brand = get_brand).paginate(page=page, per_page=8)
    return render_template('products/index.html', brand=brand, brands=brands(), categories=categories(), get_brand=get_brand, title = "Online Miners | " + get_brand.name)

@app.route('/filterbycategory/<int:id>')
def getcategoryfilter(id):
    page = request.args.get('page',1, type=int)
    get_category = Category.query.filter_by(id=id).first_or_404()
    category = tblProducts.query.filter_by(category = get_category).paginate(page=page, per_page=8)
    return render_template('products/index.html', category=category, categories=categories(), brands=brands(), get_category=get_category, title = "Online Miners | " + get_category.name)


# Brand
@app.route('/addbrand', methods=['GET', 'POST'])
def addbrand():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    if request.method =="POST":
        getbrand = request.form.get('brand')
        brand = Brand(name=getbrand)
        db.session.add(brand)
        flash(f'The Brand {getbrand} was added to your database','success')
        db.session.commit()
        return redirect(url_for('addbrand'))
    return render_template('products/addbrand.html', brand='brand', title='Add Brand Page', newordercount=newordercount())


@app.route('/updatebrand/<int:id>', methods=['GET', 'POST'])
def updatebrand(id):
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    updatebrand = Brand.query.get_or_404(id)
    brand = request.form.get('brand')
    if request.method == "POST":
        updatebrand.name = brand
        flash(f'Your Brand has been updated','success')
        db.session.commit()
        return redirect(url_for('brand'))
    return render_template('products/updatebrand.html', title='Update Brand Page', updatebrand=updatebrand, newordercount=newordercount())

@app.route('/deletebrand/<int:id>', methods=['POST'])
def deletebrand(id):
    brand = Brand.query.get_or_404(id)
    if request.method =="POST":
        db.session.delete(brand)
        db.session.commit()
        flash(f'{{brand.name}} has been deleted successfully','success')
        return redirect(url_for('brand'))
    flash(f'{{brand.name}} can not be deleted','danger')
    return redirect(url_for('brand'))

# Category
@app.route('/addcategory', methods=['GET', 'POST'])
def addcategory():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    if request.method =="POST":
        getcategory = request.form.get('category')
        category = Category(name=getcategory)
        db.session.add(category)
        flash(f'The Category {getcategory} was added to your database','success')
        db.session.commit()
        return redirect(url_for('addcategory'))
    return render_template('products/addbrand.html', category='category', title='Add Category Page', newordercount=newordercount())


@app.route('/updatecategory/<int:id>', methods=['GET', 'POST'])
def updatecategory(id):
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    updatecategory = Category.query.get_or_404(id)
    category = request.form.get('category')
    if request.method == "POST":
        updatecategory.name = category
        flash(f'Your Category has been updated','success')
        db.session.commit()
        return redirect(url_for('category'))
    return render_template('products/updatebrand.html', title='Update Category Page', updatecategory=updatecategory, newordercount=newordercount())

@app.route('/deletecategory/<int:id>', methods=['POST'])
def deletecategory(id):
    category = Category.query.get_or_404(id)
    if request.method =="POST":
        db.session.delete(category)
        db.session.commit()
        flash(f'{{category.name}} has been deleted successfully','success')
        return redirect(url_for('category'))
    flash(f'{{category.name}} can not be deleted','danger')
    return redirect(url_for('category'))

# Product
    
@app.route('/addproduct', methods=['GET', 'POST'])
def addproduct():
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    brands = Brand.query.all()
    categories = Category.query.all()
    form = ProductForm(request.form)
    if request.method =="POST":
        name = form.name.data
        price = form.price.data
        discount = form.discount.data
        stock = form.stock.data
        colors = form.colors.data
        description = form.description.data
        brand = request.form.get('brand')
        category = request.form.get('category')
        image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
        image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
        image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        addprod = tblProducts(name=name, price=price, discount=discount, stock=stock, colors=colors, description=description, 
        brand_id=brand, category_id=category, image_1=image_1, image_2=image_2, image_3=image_3 )
        db.session.add(addprod)
        flash(f'The Product {name} has been added to your database','success')
        db.session.commit()
        return redirect(url_for('admin'))
    return render_template('products/addproduct.html', title='Add Product Page', form=form, brands=brands, categories=categories, newordercount=newordercount())

@app.route('/updateproduct/<int:id>', methods=['GET', 'POST'])
def updateproduct(id):
    if 'email' not in session:
        flash(f'Please login first','danger')
        return redirect(url_for('login'))
    brands = Brand.query.all()
    categories = Category.query.all()
    product = tblProducts.query.get_or_404(id)
    brand = request.form.get('brand')
    category = request.form.get('category')
    form = ProductForm(request.form)
    if request.method =="POST":
        product.name = form.name.data
        product.price = form.price.data
        product.discount = form.discount.data
        product.stock = form.stock.data
        product.colors = form.colors.data 
        product.brand_id = brand
        product.category_id = category
        product.description = form.description.data
        if request.files.get('image_1'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                product.image_1 = photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")
            except:
                photos.save(request.files.get('image_1'), name=secrets.token_hex(10) + ".")

        if request.files.get('image_2'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                product.image_2 = photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")
            except:
                photos.save(request.files.get('image_2'), name=secrets.token_hex(10) + ".")

        if request.files.get('image_3'):
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
                product.image_3 = photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
            except:
                photos.save(request.files.get('image_3'), name=secrets.token_hex(10) + ".")
        
        db.session.commit()
        flash(f'The Product {product.name} has been updated successfully','success')    
        return redirect(url_for('admin'))

    form.name.data = product.name
    form.price.data = product.price
    form.discount.data = product.discount
    form.stock.data = product.stock
    form.colors.data = product.colors
    form.description.data = product.description
    return render_template('products/updateproduct.html', title='Update Product Page', form=form, brands=brands, categories=categories, product=product, newordercount=newordercount())

@app.route('/deleteproduct/<int:id>', methods=['POST'])
def deleteproduct(id):
    product = tblProducts.query.get_or_404(id)
    if request.method =="POST":
            try:
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_1))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_2))
                os.unlink(os.path.join(current_app.root_path, "static/images/" + product.image_3))
            except Exeption as e:
                print(e)

            db.session.delete(product)
            db.session.commit()
            flash(f'{{product.name}} has been deleted successfully','success')
            return redirect(url_for('admin'))
    flash(f'{{product.name}} can not be deleted','danger')
    return redirect(url_for('admin'))