from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    city = db.Column(db.String(50), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)

class trip(db.Model):
    __tablename__ = 'trips'
    id = db.Column(db.Integer, primary_key=True)
    startdate = db.Column(db.String(50), nullable=False)
    enddate = db.Column(db.String(50), nullable=False)
    place = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('trips', lazy=True))
    image_filename = db.Column(db.String(200), nullable=True)
    image_data = db.Column(db.LargeBinary, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='Pending')
    budget = db.Column(db.Float, nullable=True)
    members = db.Column(db.Integer, nullable=True)

class tripsections(db.Model):
    __tablename__ = 'dateranges'
    id = db.Column(db.Integer, primary_key=True)
    sectionname = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    startdate = db.Column(db.String(50), nullable=False)
    enddate = db.Column(db.String(50), nullable=False)
    budget = db.Column(db.Float, nullable=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id'), nullable=False)
    trip = db.relationship('trip', backref=db.backref('dateranges', lazy=True))
