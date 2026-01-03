from flask import Blueprint, request, jsonify
from app.models.activity import Activity
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime

activity_bp = Blueprint('activity', __name__)

@activity_bp.route("/<int:stop_id>", methods=["POST"])
@jwt_required()
def add_activity(stop_id):
    data = request.json

    activity = Activity(
        stop_id=stop_id,
        name=data["name"],
        category=data["category"],
        cost=data["cost"],
        day=datetime.fromisoformat(data["day"])
    )

    db.session.add(activity)
    db.session.commit()

    return jsonify({"message": "Activity added"})

@activity_bp.route("/<int:stop_id>", methods=["GET"])
@jwt_required()
def get_activities(stop_id):
    activities = Activity.query.filter_by(stop_id=stop_id).all()

    return jsonify([
        {
            "id": a.id,
            "name": a.name,
            "category": a.category,
            "cost": a.cost,
            "day": a.day
        } for a in activities
    ])
