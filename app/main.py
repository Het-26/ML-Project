from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db import models
from app.db.database import Base, engine
from app.deps import get_db
from app.ml.predictor import ChurnPredictor
from app.routers import auth, predict


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    app.state.predictor = ChurnPredictor()
    yield


app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(auth.router)
app.include_router(predict.router)


@app.get("/health")
def health(db: Session = Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"status": "ok", "database": "connected"}
