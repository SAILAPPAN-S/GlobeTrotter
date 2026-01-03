from app.extensions import db

class Trip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    destination = db.Column(db.String(100))
    Title = db.Column(db.String(200))
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    decscription = db.Column(db.Text)
    user = db.relationship('User', backref=db.backref('trips', lazy=True))