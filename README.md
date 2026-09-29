# Customer Churn Prediction

This is my internship project. It is a web app that predicts if a telecom customer will churn
(cancel their subscription) or stay, based on details like contract type, tenure, services
and monthly charges.

You can sign up, log in, enter a customer's details and the app tells you "Likely to churn" or
"Likely to stay" along with the churn probability. All predictions are saved, so you can see
your previous predictions in the History tab.

## Tech Stack

- **Backend:** FastAPI
- **Frontend:** Streamlit
- **Database:** MySQL with SQLAlchemy
- **Authentication:** JWT (access token + refresh token), passwords hashed with bcrypt
- **Machine Learning:** pandas, scikit-learn

## How it works

- Streamlit is the frontend. It only talks to the FastAPI backend (it does not connect to the
  database or the model directly).
- When you click Predict, Streamlit sends the customer details to the `/predict` endpoint with
  your access token.
- FastAPI checks the token and validates the input. If a value is wrong it returns a 422 error.
- The input goes through the same cleaning steps as the training data, then the trained model
  gives the prediction and the probability.
- The result is saved in MySQL and shown in Streamlit.

The access token expires after 15 minutes. When that happens Streamlit gets a new one using the
refresh token, so you don't have to log in again. If the refresh token (7 days) also expires,
you are sent back to the login page.

## Folder Structure

```
app/
  main.py            - FastAPI app, creates tables and loads the model on startup
  deps.py            - dependencies (database session, current user, model)
  core/
    config.py        - reads settings from .env
    security.py      - password hashing and JWT tokens
  db/
    database.py      - database connection
    models.py        - users and predictions tables
  schemas/           - request and response models (Pydantic)
  routers/
    auth.py          - /signup, /login, /refresh, /me
    predict.py       - /predict, /history
  ml/
    config.py        - file paths and column lists
    data_cleaning.py - cleans the raw data
    train.py         - trains the model and saves model.pkl
    predictor.py     - loads the model and makes predictions for the API
frontend/
  streamlit_app.py   - Streamlit app
notebooks/
  eda_and_training.ipynb - data analysis and model experiments
requirements.txt
```

## Setup

You need Python 3.10 and MySQL 8.

**1. Clone the repo and install the packages**

```bash
git clone https://github.com/Het-26/ML-Project.git
cd ML-Project
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

(On Mac/Linux use `source venv/bin/activate` instead.)

**2. Download the dataset**

Download the Telco Customer Churn dataset from Kaggle:
https://www.kaggle.com/datasets/blastchar/telco-customer-churn

Put it in a `data` folder as `data/WA_Fn-UseC_-Telco-Customer-Churn.csv`.

**3. Create the database**

```sql
CREATE DATABASE churn_db;
```

The tables are created automatically when the API starts.

**4. Create a `.env` file** in the project folder:

```env
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=churn_db
SECRET_KEY=any_long_random_string
```

`DB_PASSWORD` and `SECRET_KEY` are required, the app won't start without them. You can also set
`ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` and `REFRESH_TOKEN_EXPIRE_DAYS`, but they already have
default values. Don't add any other variables to `.env`, otherwise the app gives an error on startup.

**5. Train the model**

`model.pkl` is not uploaded to GitHub, so you have to train it first:

```bash
python -m app.ml.train
```

This cleans the data, trains the model, prints the results and saves `app/ml/model.pkl`.
It only takes a few seconds.

## Running the project

Start the backend:

```bash
python -m uvicorn app.main:app --reload
```

Swagger docs will be at http://127.0.0.1:8000/docs

Then open another terminal and start the frontend:

```bash
python -m streamlit run frontend/streamlit_app.py
```

The app will open at http://localhost:8501

## API Endpoints

| Method | Endpoint | What it does |
|---|---|---|
| POST | /signup | Create a new account |
| POST | /login | Log in and get access + refresh token |
| POST | /refresh | Get a new access token using the refresh token |
| GET | /me | Get logged in user details |
| POST | /predict | Predict churn and save the result |
| GET | /history | Get your past predictions |
| GET | /health | Check if the API and database are working |

`/me`, `/predict` and `/history` need the access token. To test them in Swagger, click the
**Authorize** button and log in first.

## Dataset and Model

The dataset has 7,043 customers and 21 columns. I used 19 of them as features (3 numeric and
16 categorical). Around 26.5% of the customers churned, so the data is imbalanced.

Data cleaning:
- `TotalCharges` was stored as text and had 11 empty values. All of them were new customers with
  tenure 0, so I filled them with 0.
- Dropped `customerID` because it's just an ID.
- Converted `Churn` from Yes/No to 1/0.

In the notebook I compared Logistic Regression and Random Forest and tuned both with
GridSearchCV. Random Forest was only slightly better (by 0.002 ROC-AUC), which is basically the
same, so I went with Logistic Regression because it is simpler and easier to explain. I used
`class_weight="balanced"` because of the imbalanced data.

Results on the test set (20% of the data):

| ROC-AUC | Recall | Precision | F1 | Accuracy |
|---|---|---|---|---|
| 0.84 | 0.78 | 0.51 | 0.61 | 0.74 |


