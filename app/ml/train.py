import pickle
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    f1_score, precision_score, recall_score, roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from app.ml.config import (
    CLEAN_DATA_PATH, MODEL_PATH, TARGET_COLUMN, FEATURES,
    NUMERIC_FEATURES, CATEGORICAL_FEATURES, RANDOM_STATE, TEST_SIZE,
)
from app.ml.data_cleaning import DataCleaner


class ChurnTrainer:
    def __init__(self, clean_path=CLEAN_DATA_PATH, model_path=MODEL_PATH):
        self.clean_path = clean_path
        self.model_path = model_path
        self.pipeline = None

    def load_data(self):
        df = pd.read_csv(self.clean_path)
        X = df[FEATURES]
        y = df[TARGET_COLUMN]
        return X, y

    def build_pipeline(self):
        preprocessor = ColumnTransformer(
            transformers=[
                ("num", StandardScaler(), NUMERIC_FEATURES),
                ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_FEATURES),
            ]
        )

        classifier = LogisticRegression(
            C=10,
            penalty="l2",
            class_weight="balanced",
            solver="liblinear",
            max_iter=2000,
            random_state=RANDOM_STATE,
        )

        self.pipeline = Pipeline(steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ])
        return self.pipeline

    def train_and_evaluate(self):
        X, y = self.load_data()

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        print(f"Train: {len(X_train)} rows | Test: {len(X_test)} rows | churn rate {y.mean():.1%}")

        self.build_pipeline()
        self.pipeline.fit(X_train, y_train)

        y_pred = self.pipeline.predict(X_test)
        y_proba = self.pipeline.predict_proba(X_test)[:, 1]

        print("\n=== Evaluation on Test Set ===")
        print(f"Accuracy : {accuracy_score(y_test, y_pred):.4f}")
        print(f"Precision: {precision_score(y_test, y_pred):.4f}")
        print(f"Recall   : {recall_score(y_test, y_pred):.4f}")
        print(f"F1       : {f1_score(y_test, y_pred):.4f}")
        print(f"ROC-AUC  : {roc_auc_score(y_test, y_proba):.4f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        return self.pipeline

    def save(self):
        with open(self.model_path, "wb") as f:
            pickle.dump(self.pipeline, f)
        print(f"Pipeline saved to {self.model_path}")

    def run(self):
        self.train_and_evaluate()
        self.save()
        return self.pipeline


if __name__ == "__main__":
    if not CLEAN_DATA_PATH.exists():
        print("Cleaned data not found. Running data cleaning...")
        DataCleaner().clean()
    else:
        print(f"Using existing cleaned data at {CLEAN_DATA_PATH}")

    print("\nTraining pipeline...")
    ChurnTrainer().run()
