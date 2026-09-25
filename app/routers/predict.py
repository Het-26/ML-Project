from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.models import Prediction, User
from app.deps import get_current_user, get_db, get_predictor
from app.ml.predictor import ChurnPredictor
from app.schemas.predict import CustomerInput, PredictionResponse

router = APIRouter(tags=["predict"])


# ---------- Predict ----------

@router.post("/predict", response_model=PredictionResponse, status_code=status.HTTP_201_CREATED)
def predict(
    customer: CustomerInput,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    predictor: ChurnPredictor = Depends(get_predictor),
):
    input_data = customer.model_dump()
    prediction, probability = predictor.predict(input_data)

    record = Prediction(
        user_id=current_user.id,
        input_data=input_data,
        prediction=prediction,
        probability=probability,
    )
    db.add(record)
    db.commit()
    db.refresh(record)

    return record


# ---------- History ----------

@router.get("/history", response_model=list[PredictionResponse])
def history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc(), Prediction.id.desc())
        .all()
    )
