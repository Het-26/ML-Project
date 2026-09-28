import pandas as pd
import requests
import streamlit as st

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Churn Prediction", layout="wide")

YES_NO = ["No", "Yes"]
PHONE_OPTIONS = ["No", "Yes", "No phone service"]
INTERNET_OPTIONS = ["No", "Yes", "No internet service"]
CONTRACTS = ["Month-to-month", "One year", "Two year"]
PAYMENT_METHODS = [
    "Electronic check",
    "Mailed check",
    "Bank transfer (automatic)",
    "Credit card (automatic)",
]

for key in ("access_token", "refresh_token", "username"):
    if key not in st.session_state:
        st.session_state[key] = None


# ---------- API helpers ----------

def clear_session():
    for key in ("access_token", "refresh_token", "username"):
        st.session_state[key] = None


def error_detail(response):
    try:
        detail = response.json().get("detail", response.text)
    except ValueError:
        return response.text
    if isinstance(detail, list):
        return "; ".join(f"{err['loc'][-1]}: {err['msg']}" for err in detail)
    return detail


def api_request(method, path, **kwargs):
    try:
        return requests.request(method, f"{API_URL}{path}", timeout=10, **kwargs)
    except requests.ConnectionError:
        st.error(f"Cannot reach the API at {API_URL}. Is uvicorn running?")
        return None


def try_refresh():
    if not st.session_state["refresh_token"]:
        return False

    response = api_request(
        "POST", "/refresh", json={"refresh_token": st.session_state["refresh_token"]}
    )
    if response is not None and response.status_code == 200:
        st.session_state["access_token"] = response.json()["access_token"]
        return True
    return False


def authed_request(method, path, **kwargs):
    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    response = api_request(method, path, headers=headers, **kwargs)

    if response is None or response.status_code != 401:
        return response

    if not try_refresh():
        clear_session()
        return response

    headers = {"Authorization": f"Bearer {st.session_state['access_token']}"}
    return api_request(method, path, headers=headers, **kwargs)


# ---------- Auth page ----------

def show_auth_page():
    st.title("Customer Churn Prediction")

    login_tab, signup_tab = st.tabs(["Log in", "Sign up"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Log in")

        if submitted:
            response = api_request(
                "POST", "/login", data={"username": username, "password": password}
            )
            if response is None:
                return
            if response.status_code == 200:
                tokens = response.json()
                st.session_state["access_token"] = tokens["access_token"]
                st.session_state["refresh_token"] = tokens["refresh_token"]
                st.session_state["username"] = username
                st.rerun()
            else:
                st.error(f"Login failed: {error_detail(response)}")

    with signup_tab:
        with st.form("signup_form"):
            username = st.text_input("Username", help="3 to 50 characters")
            email = st.text_input("Email")
            password = st.text_input("Password", type="password", help="At least 8 characters")
            submitted = st.form_submit_button("Sign up")

        if submitted:
            response = api_request(
                "POST",
                "/signup",
                json={"username": username, "email": email, "password": password},
            )
            if response is None:
                return
            if response.status_code == 201:
                st.success(f"Account created for {response.json()['username']}. You can log in now.")
            else:
                st.error(f"Signup failed: {error_detail(response)}")


# ---------- Predict tab ----------

def input_row(title):
    left, right = st.columns(2, vertical_alignment="center")
    left.write(f"**{title}**")
    return right


def selectbox_row(title, options, **kwargs):
    return input_row(title).selectbox(title, options, label_visibility="collapsed", **kwargs)


def customer_form():
    gender = selectbox_row("Gender", ["Female", "Male"])
    senior = selectbox_row("Senior citizen", YES_NO)
    partner = selectbox_row("Partner", YES_NO)
    dependents = selectbox_row("Dependents", YES_NO)
    tenure = input_row("Tenure (months)").number_input(
        "Tenure (months)", min_value=0, max_value=100, value=2, step=1,
        label_visibility="collapsed",
    )

    phone = selectbox_row("Phone service", YES_NO, index=1)
    multiple_lines = selectbox_row("Multiple lines", PHONE_OPTIONS)
    internet = selectbox_row("Internet service", ["DSL", "Fiber optic", "No"], index=1)
    online_security = selectbox_row("Online security", INTERNET_OPTIONS)
    online_backup = selectbox_row("Online backup", INTERNET_OPTIONS)
    device_protection = selectbox_row("Device protection", INTERNET_OPTIONS)
    tech_support = selectbox_row("Tech support", INTERNET_OPTIONS)
    streaming_tv = selectbox_row("Streaming TV", INTERNET_OPTIONS)
    streaming_movies = selectbox_row("Streaming movies", INTERNET_OPTIONS)

    contract = selectbox_row("Contract", CONTRACTS)
    paperless = selectbox_row("Paperless billing", YES_NO, index=1)
    payment = selectbox_row("Payment method", PAYMENT_METHODS)
    monthly = input_row("Monthly charges").number_input(
        "Monthly charges", min_value=0.01, value=70.70, step=1.0,
        label_visibility="collapsed",
    )
    total = input_row("Total charges").number_input(
        "Total charges", min_value=0.0, value=151.65, step=10.0,
        label_visibility="collapsed",
    )

    return {
        "tenure": int(tenure),
        "MonthlyCharges": float(monthly),
        "TotalCharges": float(total),
        "gender": gender,
        "SeniorCitizen": 1 if senior == "Yes" else 0,
        "Partner": partner,
        "Dependents": dependents,
        "PhoneService": phone,
        "MultipleLines": multiple_lines,
        "InternetService": internet,
        "OnlineSecurity": online_security,
        "OnlineBackup": online_backup,
        "DeviceProtection": device_protection,
        "TechSupport": tech_support,
        "StreamingTV": streaming_tv,
        "StreamingMovies": streaming_movies,
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment,
    }


def show_result(result):
    probability = result["probability"]
    if result["prediction"] == 1:
        st.error(f"### Likely to churn\nChurn probability: **{probability:.0%}**")
    else:
        st.success(f"### Likely to stay\nChurn probability: **{probability:.0%}**") 


def show_predict_tab():
    customer = customer_form()

    if st.button("Predict churn", type="primary"):
        response = authed_request("POST", "/predict", json=customer)
        if response is None:
            return
        if response.status_code == 201:
            show_result(response.json())
        elif response.status_code == 401:
            st.rerun()
        else:
            st.error(f"Prediction failed: {error_detail(response)}")


# ---------- History tab ----------

def show_history_tab():
    response = authed_request("GET", "/history")
    if response is None:
        return
    if response.status_code == 401:
        st.rerun()
    if response.status_code != 200:
        st.error(f"Could not load history: {error_detail(response)}")
        return

    records = response.json()
    if not records:
        st.info("No predictions yet. Make one in the Predict tab.")
        return

    rows = [
        {
            "Date": pd.to_datetime(r["created_at"]).strftime("%Y-%m-%d %H:%M"),
            "Result": "Churn" if r["prediction"] == 1 else "Stay",
            "Probability": f"{r['probability']:.1%}",
            **r["input_data"],
        }
        for r in records
    ]
    st.write(f"{len(rows)} prediction(s), newest first.")
    st.dataframe(pd.DataFrame(rows), hide_index=True)


# ---------- Main page ----------

def show_main_page():
    title_col, user_col, logout_col = st.columns([6, 2, 1], vertical_alignment="center")
    title_col.title("Customer Churn Prediction")
    user_col.write(f"Logged in as **{st.session_state['username']}**")
    if logout_col.button("Log out"):
        clear_session()
        st.rerun()

    predict_tab, history_tab = st.tabs(["Predict", "History"])
    with predict_tab:
        show_predict_tab()
    with history_tab:
        show_history_tab()


if st.session_state["access_token"]:
    show_main_page()
else:
    show_auth_page()
