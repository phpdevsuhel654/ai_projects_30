import pickle
from pathlib import Path

from services.dataset_service import DatasetService


class Predictor:
    def __init__(self, model_path: str | None = None) -> None:
        self.model_path = Path(model_path or "ml/saved_model.pkl")
        self.dataset_service = DatasetService()

    def load_artifact(self) -> dict:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found: {self.model_path}")

        with self.model_path.open("rb") as f:
            return pickle.load(f)

    def predict(self, message: str) -> tuple[str, float]:
        artifact = self.load_artifact()
        model = artifact["model"]
        vectorizer = artifact["vectorizer"]

        cleaned = self.dataset_service.preprocess_text(message)
        transformed = vectorizer.transform([cleaned])
        prediction = model.predict(transformed)[0]
        probabilities = model.predict_proba(transformed)[0]
        confidence = round(float(max(probabilities)), 4)
        label = "spam" if prediction == 1 else "ham"
        return label, confidence
