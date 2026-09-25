from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

YesNo = Literal["Yes", "No"]
PhoneOption = Literal["Yes", "No", "No phone service"]
InternetOption = Literal["Yes", "No", "No internet service"]


class CustomerInput(BaseModel):
    tenure: int = Field(ge=0, le=100, description="Months with the company")
    MonthlyCharges: float = Field(gt=0)
    TotalCharges: float = Field(ge=0)

    gender: Literal["Male", "Female"]
    SeniorCitizen: Literal[0, 1]
    Partner: YesNo
    Dependents: YesNo
    PhoneService: YesNo
    MultipleLines: PhoneOption
    InternetService: Literal["DSL", "Fiber optic", "No"]
    OnlineSecurity: InternetOption
    OnlineBackup: InternetOption
    DeviceProtection: InternetOption
    TechSupport: InternetOption
    StreamingTV: InternetOption
    StreamingMovies: InternetOption
    Contract: Literal["Month-to-month", "One year", "Two year"]
    PaperlessBilling: YesNo
    PaymentMethod: Literal[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ]

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "tenure": 2,
                "MonthlyCharges": 70.7,
                "TotalCharges": 151.65,
                "gender": "Female",
                "SeniorCitizen": 0,
                "Partner": "No",
                "Dependents": "No",
                "PhoneService": "Yes",
                "MultipleLines": "No",
                "InternetService": "Fiber optic",
                "OnlineSecurity": "No",
                "OnlineBackup": "No",
                "DeviceProtection": "No",
                "TechSupport": "No",
                "StreamingTV": "No",
                "StreamingMovies": "No",
                "Contract": "Month-to-month",
                "PaperlessBilling": "Yes",
                "PaymentMethod": "Electronic check",
            }
        }
    )


# --- Prediction response ---
class PredictionResponse(BaseModel):
    id: int
    input_data: CustomerInput
    prediction: int
    probability: float
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
