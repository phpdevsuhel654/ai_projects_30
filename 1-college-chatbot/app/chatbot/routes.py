from flask import jsonify, render_template, request
from flask import current_app
from flask_login import current_user

from app.chatbot import chatbot_bp
from app.extensions import limiter
from app.services.chat_service import ChatService


@chatbot_bp.route("/chat")
def chat_page():
    return render_template("chat.html")


@chatbot_bp.route("/api/chat", methods=["POST"])
@limiter.limit(lambda: current_app.config.get("API_CHAT_RATE_LIMIT", "30 per minute"))
def chat_api():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    session_id = data.get("session_id", "web-session")

    user_id = current_user.id if current_user.is_authenticated else None

    result = ChatService().process_message(user_id=user_id, message=message, session_id=session_id)

    return jsonify(result)
