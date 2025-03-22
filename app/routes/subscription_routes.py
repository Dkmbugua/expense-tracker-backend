from flask import Blueprint, request, jsonify
from app.db import db
from models.subscription import Subscription
from datetime import datetime
from app.services.tasks import schedule_subscription_payment

subscription_bp = Blueprint("subscriptions", __name__)

# ✅ GET all subscriptions
@subscription_bp.route("/subscriptions", methods=["GET"])
def get_subscriptions():
    subscriptions = Subscription.query.all()
    return jsonify([
        {
            "id": sub.id,
            "user_id": sub.user_id,
            "name": sub.name,
            "amount": sub.amount,
            "billing_cycle": sub.billing_cycle,
            "next_payment_date": sub.next_payment_date.strftime("%Y-%m-%d") if sub.next_payment_date else None,
        }
        for sub in subscriptions
    ]), 200


# ✅ POST: Add a new subscription
@subscription_bp.route("/subscriptions", methods=["POST"])
def add_subscription():
    data = request.json

    try:
        user_id = int(data.get("user_id", 0))  # Ensure user_id is an integer
    except ValueError:
        return jsonify({"error": "Invalid user_id. Must be an integer."}), 400

    # 🔴 Validate required fields
    if not user_id:
        return jsonify({"error": "User ID is required and must be an integer."}), 400

    if "name" not in data or not data["name"]:
        return jsonify({"error": "Subscription name is required"}), 400

    if "amount" not in data:
        return jsonify({"error": "Subscription amount is required"}), 400

    try:
        amount = float(data["amount"])  # Ensure amount is a float
    except ValueError:
        return jsonify({"error": "Invalid amount. Must be a number."}), 400

    # ✅ Handle Optional Date (Making next_payment_date Optional)
    next_payment_date = data.get("next_payment_date", None)
    if next_payment_date:
        try:
            next_payment_date = datetime.strptime(next_payment_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    frequency = data.get("billing_cycle", "monthly").lower()

    # ✅ Create Subscription Object
    new_subscription = Subscription(
        user_id=user_id,
        name=data["name"],
        amount=amount,
        billing_cycle=frequency,
        next_payment_date=next_payment_date,
    )

    db.session.add(new_subscription)
    db.session.commit()

    # 🔹 Schedule automated payments based on frequency
    schedule_subscription_payment(new_subscription.id, frequency)

    return jsonify({
        "message": "Subscription added successfully!",
        "subscription": {
            "id": new_subscription.id,
            "user_id": new_subscription.user_id,
            "name": new_subscription.name,
            "amount": new_subscription.amount,
            "billing_cycle": new_subscription.billing_cycle,
            "next_payment_date": new_subscription.next_payment_date.strftime("%Y-%m-%d") if new_subscription.next_payment_date else None
        }
    }), 201


# ✅ PUT: Update a subscription
@subscription_bp.route("/subscriptions/<int:sub_id>", methods=["PUT"])
def update_subscription(sub_id):
    sub = Subscription.query.get_or_404(sub_id)
    data = request.json

    sub.name = data.get("name", sub.name)
    sub.amount = data.get("amount", sub.amount)
    sub.billing_cycle = data.get("billing_cycle", sub.billing_cycle)

    next_payment_date = data.get("next_payment_date", None)
    if next_payment_date:
        try:
            sub.next_payment_date = datetime.strptime(next_payment_date, "%Y-%m-%d")
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400

    db.session.commit()
    return jsonify({"message": "Subscription updated successfully!"}), 200


# ✅ DELETE: Remove a subscription
@subscription_bp.route("/subscriptions/<int:sub_id>", methods=["DELETE"])
def delete_subscription(sub_id):
    sub = Subscription.query.get_or_404(sub_id)
    db.session.delete(sub)
    db.session.commit()
    return jsonify({"message": "Subscription deleted successfully!"}), 200
