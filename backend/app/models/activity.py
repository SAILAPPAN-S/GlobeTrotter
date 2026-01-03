from app.extensions import db

class Activity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    stop_id = db.Column(db.Integer, db.ForeignKey("trip_stop.id"))
    name = db.Column(db.String(100))
    category = db.Column(db.String(50))
    cost = db.Column(db.Float)
    day = db.Column(db.Date)
