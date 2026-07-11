from pathlib import Path

import pandas as pd


class DatasetService:
    def __init__(self, dataset_path: str | None = None) -> None:
        self.dataset_path = Path(dataset_path or "dataset/spam.csv")

    def load_dataset(self) -> pd.DataFrame:
        if not self.dataset_path.exists():
            raise FileNotFoundError(f"Dataset not found: {self.dataset_path}")

        df = pd.read_csv(self.dataset_path, quotechar='"')
        if "label" not in df.columns or "message" not in df.columns:
            raise ValueError("Dataset must contain 'label' and 'message' columns")

        df = df[["label", "message"]].copy()
        df["label"] = df["label"].str.strip().str.lower()
        df["message"] = df["message"].fillna("").astype(str)
        return df

    def preprocess_text(self, text: str) -> str:
        text = text.lower()
        text = text.replace("\n", " ")
        text = " ".join(text.split())
        return text

    def prepare_dataset(self) -> pd.DataFrame:
        df = self.load_dataset()
        df["cleaned_message"] = df["message"].apply(self.preprocess_text)
        df["target"] = df["label"].map({"ham": 0, "spam": 1})
        df = df.dropna(subset=["target"])
        return df
