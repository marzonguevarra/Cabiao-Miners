from main import db, login_manager
from datetime import datetime
from flask_login import UserMixin
import json

@login_manager.user_loader
def user_loader(user_id):
    return tblCustomers.query.get(user_id)

class tblCustomers(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(80), unique=False)
    address = db.Column(db.String(120), unique=False)
    number = db.Column(db.String(50), unique=True)
    profile = db.Column(db.String(80), unique=False, default='profile.jpg')
    datecreated = db.Column(db.DateTime, nullable=False, default=datetime.now)
    
    def __repr__(self):
        return '<tblCustomers %r>' % self.name

class JsonEcodedDict(db.TypeDecorator):
    impl = db.Text
    def process_bind_param(self, value, dialect):
        if value is None:
            return '{}'
        else:
            return json.dumps(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return {}
        else:
            return json.loads(value)


class tblOrders(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice = db.Column(db.String(20),unique=True, nullable=False)
    status = db.Column(db.String(20), default='Pending', nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('tbl_customers.id'), nullable=False)
    datecreated = db.Column(db.DateTime, nullable=False, default=datetime.now)
    orders = db.Column(JsonEcodedDict)

    def __repr__(self):
        return'<tblOrders %r>' % self.invoice

db.create_all()
