import pandas as pd

from app.ml.config import RAW_DATA_PATH, CLEAN_DATA_PATH, TARGET_COLUMN, DROP_COLUMNS


class DataCleaner:

    def __init__(self, raw_path=RAW_DATA_PATH, clean_path=CLEAN_DATA_PATH, df=None):
        self.raw_path = raw_path
        self.clean_path = clean_path
        self.df = df

    def load(self):
        self.df = pd.read_csv(self.raw_path)
        return self

    def fix_total_charges(self):
        self.df["TotalCharges"] = pd.to_numeric(self.df["TotalCharges"], errors="coerce").fillna(0.0)
        return self

    def fix_senior_citizen(self):
        self.df["SeniorCitizen"] = self.df["SeniorCitizen"].astype(int)
        return self

    def encode_target(self):
        self.df[TARGET_COLUMN] = (self.df[TARGET_COLUMN] == "Yes").astype(int)
        return self

    def drop_unused_columns(self):
        cols_to_drop = [c for c in DROP_COLUMNS if c in self.df.columns]
        self.df = self.df.drop(columns=cols_to_drop)
        return self

    def save(self):
        self.df.to_csv(self.clean_path, index=False)
        return self

    def clean(self):
        (self.load()
             .fix_total_charges()
             .fix_senior_citizen()
             .encode_target()
             .drop_unused_columns()
             .save())
        print(f"Cleaned data saved to {self.clean_path}")
        return self.df


if __name__ == "__main__":
    DataCleaner().clean()
