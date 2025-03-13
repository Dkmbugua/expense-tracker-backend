from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.services.ai_service import analyze_spending, chatbot_response

ai_routes = Blueprint("ai_routes", __name__)

@ai_routes.route("/ai-insights", methods=["GET", "POST"])
@jwt_required()
def ai_insights():
    """Handles AI financial analysis."""
    user_id = get_jwt_identity()

    if request.method == "GET":
        timeframe = request.args.get("timeframe", "monthly")
        insights = analyze_spending(user_id, timeframe)
        return jsonify(insights), 200

    elif request.method == "POST":
        data = request.get_json()
        prompt_text = data.get("prompt", "")

        if not prompt_text:
            return jsonify({"error": "Prompt is required!"}), 400

        insights = analyze_spending(user_id, "monthly", prompt_text)
        return jsonify(insights), 200

@ai_routes.route("/chat", methods=["POST"])
def chat():
    """Handles chatbot responses."""
    data = request.get_json()
    user_input = data.get("message", "")

    if not user_input:
        return jsonify({"error": "Message is required!"}), 400

    response = chatbot_response(user_input)
    return jsonify({"response": response}), 200
