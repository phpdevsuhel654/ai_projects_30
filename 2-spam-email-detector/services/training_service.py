import pickle
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB

from services.dataset_service import DatasetService


class TrainingService:
    def __init__(self, dataset_path: str | None = None, model_path: str | None = None) -> None:
        self.dataset_service = DatasetService(dataset_path=dataset_path)
        self.model_path = Path(model_path or "ml/saved_model.pkl")
        self.model_path.parent.mkdir(parents=True, exist_ok=True)

    def train_model(self) -> dict:
        df = self.dataset_service.prepare_dataset()
        vectorizer = TfidfVectorizer(ngram_range=(1, 2))
        X_vec = vectorizer.fit_transform(df["cleaned_message"])

        model = MultinomialNB()
        model.fit(X_vec, df["target"])

        artifact = {
            "model": model,
            "vectorizer": vectorizer,
            "accuracy": None,
        }

        with self.model_path.open("wb") as f:
            pickle.dump(artifact, f)

        return {
            "accuracy": None,
            "model_path": str(self.model_path),
            "train_size": len(df),
            "test_size": 0,
        }

    def load_model_artifact(self) -> dict:
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model artifact not found: {self.model_path}")

        with self.model_path.open("rb") as f:
            return pickle.load(f)
