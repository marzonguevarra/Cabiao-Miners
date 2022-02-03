from main import db

class tblAdmins(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), unique=False, nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    role = db.Column(db.String(45), unique=False, nullable=False, default='Administrator')
    profile = db.Column(db.String(80), unique=False, nullable=False, default='profile.jpg')

    def __repr__(self):
        return '<tblAdmins %r>' % self.username


db.create_all()
