from database.db import SessionLocal
from ml.predictor import Predictor
from models.prediction_model import PredictionHistory


class PredictionService:
    def __init__(self) -> None:
        self.predictor = Predictor()

    def predict_message(self, message: str) -> dict:
        if not message or not message.strip():
            raise ValueError("Message cannot be empty")

        prediction, confidence = self.predictor.predict(message)
        history_entry = PredictionHistory(
            email_text=message.strip(),
            prediction=prediction,
            confidence=confidence,
        )

        db = SessionLocal()
        try:
            db.add(history_entry)
            db.commit()
            db.refresh(history_entry)
        finally:
            db.close()

        return {
            "prediction": prediction,
            "confidence": confidence,
            "history_id": history_entry.id,
        }

    def get_history(self) -> list[dict]:
        db = SessionLocal()
        try:
            rows = db.query(PredictionHistory).order_by(PredictionHistory.created_at.desc()).all()
            return [
                {
                    "id": row.id,
                    "email_text": row.email_text,
                    "prediction": row.prediction,
                    "confidence": row.confidence,
                    "created_at": row.created_at.isoformat(),
                }
                for row in rows
            ]
        finally:
            db.close()
