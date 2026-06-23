from flask import jsonify, render_template

from app.routes import main_bp


@main_bp.route("/")
def home():
    return render_template("index.html")


@main_bp.route("/api/docs")
def api_docs():
    return render_template("api_docs.html")


@main_bp.route("/api/openapi.json")
def api_openapi():
    spec = {
        "openapi": "3.0.3",
        "info": {
            "title": "College Chatbot API",
            "version": "1.0.0",
        },
        "paths": {
            "/api/chat": {
                "post": {
                    "summary": "Send a student query to chatbot",
                    "requestBody": {
                        "required": True,
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "object",
                                    "properties": {
                                        "message": {"type": "string"},
                                        "session_id": {"type": "string"},
                                    },
                                    "required": ["message"],
                                }
                            }
                        },
                    },
                    "responses": {
                        "200": {
                            "description": "Chatbot response",
                        }
                    },
                }
            }
        },
    }
    return jsonify(spec)
