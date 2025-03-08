from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ai_service import analyze_spending

ai_routes = Blueprint("ai_routes", __name__)

@ai_routes.route("/ai-insights", methods=["GET"])
@jwt_required()
def ai_insights():
    """Returns AI-generated financial insights based on timeframe."""
    user_id = get_jwt_identity()
    
    # ✅ Get timeframe from query params (default to 'monthly')
    timeframe = request.args.get("timeframe", "monthly")
    
    insights = analyze_spending(user_id, timeframe)
    return jsonify(insights), 200
