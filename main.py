from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Finance App")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ── Customers ─────────────────────────────────────

@app.post("/customers/", response_model=schemas.CustomerResponse, tags=["Customer"])
def create_customer(user: schemas.CustomerCreate, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.aadhar == user.aadhar) | (models.User.pan == user.pan)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Aadhar or PAN already registered")
    new_user = models.User(**user.model_dump(), is_customer=True)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.get("/customers/", response_model=list[schemas.CustomerResponse], tags=["Customer"])
def get_all_customers(db: Session = Depends(get_db)):
    return db.query(models.User).all()

@app.get("/customers/{customer_id}", response_model=schemas.CustomerResponse, tags=["Customer"])
def get_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=schemas.CustomerResponse, tags=["Customer"])
def update_customer(customer_id: int, user: schemas.CustomerCreate, db: Session = Depends(get_db)):
    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, val in user.model_dump().items():
        setattr(customer, key, val)
    db.commit()
    db.refresh(customer)
    return customer

@app.delete("/customers/{customer_id}", tags=["Customer"])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted"}

# ── Loans ─────────────────────────────────────────

@app.post("/loans/", response_model=schemas.LoanResponse, tags=["Loan"])
def create_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db)):
    customer = db.query(models.User).filter(models.User.id == loan.customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # deduct interest from loan amount
    interest_amount = (loan.loan_amount * loan.interest_rate) / 100
    balance = loan.loan_amount - interest_amount

    new_loan = models.Loan(
        customer_id=loan.customer_id,
        loan_amount=loan.loan_amount,
        interest_rate=loan.interest_rate,
        balance_amount=balance,
        emi_amount=loan.emi_amount
    )
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return new_loan

@app.get("/loans/", response_model=list[schemas.LoanResponse], tags=["Loan"])
def get_all_loans(db: Session = Depends(get_db)):
    return db.query(models.Loan).all()

@app.get("/loans/{customer_id}", response_model=list[schemas.LoanResponse], tags=["Loan"])
def get_loans_by_customer(customer_id: int, db: Session = Depends(get_db)):
    loans = db.query(models.Loan).filter(models.Loan.customer_id == customer_id).all()
    if not loans:
        raise HTTPException(status_code=404, detail="No loans found for this customer")
    return loans

@app.put("/loans/{loan_id}/pay", response_model=schemas.LoanResponse, tags=["Loan"])
def pay_emi(loan_id: int, amount: float, db: Session = Depends(get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    # reduce balance
    loan.balance_amount -= amount

    if loan.balance_amount <= 0:
        loan.balance_amount = 0
        loan.is_paid = True
        loan.alert_sent = True

    db.commit()
    db.refresh(loan)
    return loan

@app.get("/loans/{loan_id}/alert", tags=["Loan"])
def check_alert(loan_id: int, db: Session = Depends(get_db)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.is_paid:
        return {"alert": False, "message": "Loan already paid"}
    return {"alert": True, "message": "EMI payment due tomorrow"}