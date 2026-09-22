from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

RAW_DATA_PATH = ROOT / "data" / "WA_Fn-UseC_-Telco-Customer-Churn.csv"
CLEAN_DATA_PATH = ROOT / "data" / "cleaned_data.csv"
MODEL_PATH = Path(__file__).resolve().parent / "model.pkl"

TARGET_COLUMN = "Churn"

DROP_COLUMNS = ["customerID"]

NUMERIC_FEATURES = ["tenure", "MonthlyCharges", "TotalCharges"]

CATEGORICAL_FEATURES = [
    "gender", "SeniorCitizen", "Partner", "Dependents",
    "PhoneService", "MultipleLines", "InternetService",
    "OnlineSecurity", "OnlineBackup", "DeviceProtection", "TechSupport",
    "StreamingTV", "StreamingMovies",
    "Contract", "PaperlessBilling", "PaymentMethod",
]

FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES

RANDOM_STATE = 42
TEST_SIZE = 0.2
