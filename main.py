from fastapi import FastAPI, Depends, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Annotated
from passlib.context import CryptContext
import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Finance APP")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])



def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/get_all_customers")
def get_all_loan_customers(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.post('/create_customer',response_model=schemas.Customer)
def create_customer(user: schemas.Customer, db: Session = Depends(get_db)):
    new_user = models.User(**user.model_dump())
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

    