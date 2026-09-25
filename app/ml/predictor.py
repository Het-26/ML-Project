import pickle

import pandas as pd

from app.ml.config import FEATURES, MODEL_PATH
from app.ml.data_cleaning import DataCleaner


class ChurnPredictor:

    def __init__(self, model_path=MODEL_PATH):
        if not model_path.exists():
            raise FileNotFoundError(
                f"{model_path} not found. Train it first: python -m app.ml.train"
            )
        with open(model_path, "rb") as f:
            self.pipeline = pickle.load(f)

    def prepare(self, input_data: dict) -> pd.DataFrame:
        df = pd.DataFrame([input_data])[FEATURES]
        return (DataCleaner(df=df)
                    .fix_total_charges()
                    .fix_senior_citizen()
                    .df)

    def predict(self, input_data: dict) -> tuple[int, float]:
        X = self.prepare(input_data)
        prediction = int(self.pipeline.predict(X)[0])
        probability = float(self.pipeline.predict_proba(X)[0, 1])
        return prediction, probability
