from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.trip import Trip
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.models.stop import TripStop
from datetime import datetime
from app.models.activity import Activity


trip_bp = Blueprint('trip', __name__)

@trip_bp.route('/', methods=['POST'])
@jwt_required()
def create_trip():
    data = request.get_json()
    user_id = get_jwt_identity()
    trip = Trip(
        user_id = user_id,
        Title = data['Title'],
        start_date = data['start_date'],
        end_date = data['end_date'],
        description = data.get("description", "")        
    )
    db.session.add(trip)
    db.session.commit()
    return jsonify({"message": "Trip created"})

@trip_bp.route("/", methods=["GET"])
@jwt_required()
def get_trips():
    user_id = get_jwt_identity()
    trips = Trip.query.filter_by(user_id=user_id).all()
    return jsonify([
        {"id": t.id, "title": t.title} for t in trips
    ])

@trip_bp.route("/<int:trip_id>/stops", methods=["POST"])
@jwt_required()
def add_stop(trip_id):
    data = request.json

    stop = TripStop(
        trip_id=trip_id,
        city=data["city"],
        country=data["country"],
        start_date=datetime.fromisoformat(data["start_date"]),
        end_date=datetime.fromisoformat(data["end_date"])
    )

    db.session.add(stop)
    db.session.commit()

    return jsonify({"message": "Stop added"})

@trip_bp.route("/<int:trip_id>/stops", methods=["GET"])
@jwt_required()
def get_stops(trip_id):
    stops = TripStop.query.filter_by(trip_id=trip_id).all()

    return jsonify([
        {
            "id": s.id,
            "city": s.city,
            "country": s.country,
            "start_date": s.start_date,
            "end_date": s.end_date
        } for s in stops
    ])

@trip_bp.route("/<int:trip_id>/itinerary", methods=["GET"])
@jwt_required()
def get_itinerary(trip_id):
    trip = Trip.query.get(trip_id)
    stops = TripStop.query.filter_by(trip_id=trip_id).all()

    itinerary = []

    for stop in stops:
        activities = Activity.query.filter_by(stop_id=stop.id).all()
        itinerary.append({
            "city": stop.city,
            "country": stop.country,
            "start_date": stop.start_date,
            "end_date": stop.end_date,
            "activities": [
                {
                    "name": a.name,
                    "category": a.category,
                    "cost": a.cost,
                    "day": a.day
                } for a in activities
            ]
        })

    return jsonify({
        "trip": {
            "title": trip.title,
            "start_date": trip.start_date,
            "end_date": trip.end_date
        },
        "itinerary": itinerary
    })

@trip_bp.route("/<int:trip_id>/budget", methods=["GET"])
@jwt_required()
def trip_budget(trip_id):
    stops = TripStop.query.filter_by(trip_id=trip_id).all()
    total = 0

    for stop in stops:
        activities = Activity.query.filter_by(stop_id=stop.id).all()
        total += sum(a.cost for a in activities)

    return jsonify({
        "trip_id": trip_id,
        "total_cost": total
    })
