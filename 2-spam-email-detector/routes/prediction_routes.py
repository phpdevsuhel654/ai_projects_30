from flask import Blueprint, jsonify, render_template, request

from services.prediction_service import PredictionService

prediction_bp = Blueprint("prediction", __name__)
prediction_service = PredictionService()


@prediction_bp.route("/predict", methods=["GET", "POST"])
def predict():
    if request.method == "POST":
        data = request.form or request.get_json(silent=True) or {}
        message = data.get("message", "")
        try:
            result = prediction_service.predict_message(message)
            return jsonify(result), 200
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    return render_template("predict.html", title="Make a Prediction")


@prediction_bp.route("/history")
def history():
    return render_template("history.html", title="Prediction History", history=prediction_service.get_history())
