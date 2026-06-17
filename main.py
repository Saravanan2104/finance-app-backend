from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import datetime, timedelta, timezone, date
import models, schemas, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="Finance App")

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

SECRET_KEY = "finance-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str):
    return pwd_context.verify(plain, hashed)

def create_token(data: dict):
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    data.update({"exp": expire})
    return jwt.encode(data, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        aadhar = payload.get("sub")
        if aadhar is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(models.User).filter(models.User.aadhar == int(aadhar)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def add_notification(db: Session, user_id: int, message: str):
    notif = models.Notification(user_id=user_id, message=message)
    db.add(notif)
    db.commit()

# ── Auth ──────────────────────────────────────────

@app.post("/register/", response_model=schemas.UserResponse, tags=["Auth"])
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    existing = db.query(models.User).filter(
        (models.User.aadhar == user.aadhar) | (models.User.pan == user.pan)
    ).first()
    if existing:
        raise HTTPException(status_code=400, detail="Aadhar or PAN already registered")
    new_user = models.User(
        name=user.name,
        dob=user.dob,
        aadhar=user.aadhar,
        pan=user.pan,
        phone_no=user.phone_no,
        relative_name=user.relative_name,
        relative_phone=user.relative_phone,
        relative_relation=user.relative_relation,
        role=user.role,
        password=hash_password(user.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.post("/login/", response_model=schemas.Token, tags=["Auth"])
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.aadhar == int(form_data.username)).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect password")
    token = create_token({"sub": str(user.aadhar)})
    return {"access_token": token, "token_type": "bearer"}

# ── Customers ─────────────────────────────────────

@app.get("/customers/", response_model=list[schemas.UserResponse], tags=["Customer"])
def get_all_customers(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.User).filter(models.User.role == "customer").all()

@app.get("/customers/{customer_id}", response_model=schemas.UserResponse, tags=["Customer"])
def get_customer(customer_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer

@app.put("/customers/{customer_id}", response_model=schemas.UserResponse, tags=["Customer"])
def update_customer(customer_id: int, user: schemas.UserRegister, db: Session = Depends(get_db), admin=Depends(require_admin)):
    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    for key, val in user.model_dump(exclude={"password"}).items():
        setattr(customer, key, val)
    db.commit()
    db.refresh(customer)
    return customer

@app.delete("/customers/{customer_id}", tags=["Customer"])
def delete_customer(customer_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    customer = db.query(models.User).filter(models.User.id == customer_id).first()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    db.delete(customer)
    db.commit()
    return {"message": "Customer deleted"}

# ── Loans ─────────────────────────────────────────

@app.post("/loans/apply/", response_model=schemas.LoanResponse, tags=["Loan"])
def apply_loan(loan: schemas.LoanCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    if current_user.role != "customer":
        raise HTTPException(status_code=403, detail="Only customers can apply for loans")

    # check active loan
    active_loan = db.query(models.Loan).filter(
        models.Loan.customer_id == current_user.id,
        models.Loan.status == "active"
    ).first()
    if active_loan:
        raise HTTPException(status_code=400, detail="You already have an active loan. Admin approval needed for another loan.")

    interest_amount = (loan.loan_amount * loan.interest_rate) / 100
    balance = loan.loan_amount - interest_amount

    new_loan = models.Loan(
        customer_id=current_user.id,
        loan_amount=loan.loan_amount,
        interest_rate=loan.interest_rate,
        balance_amount=balance,
        emi_amount=loan.emi_amount,
        loan_date=date.today(),
        last_interest_date=date.today(),
        status="pending"
    )
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)

    # notify all admins
    admins = db.query(models.User).filter(models.User.role == "admin").all()
    for admin in admins:
        add_notification(db, admin.id, f"New loan application from {current_user.name} for amount {loan.loan_amount}")

    return new_loan

@app.get("/loans/", response_model=list[schemas.LoanResponse], tags=["Loan"])
def get_all_loans(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.Loan).all()

@app.get("/loans/my/", response_model=list[schemas.LoanResponse], tags=["Loan"])
def get_my_loans(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Loan).filter(models.Loan.customer_id == current_user.id).all()

@app.get("/loans/pending/", response_model=list[schemas.LoanResponse], tags=["Loan"])
def get_pending_loans(db: Session = Depends(get_db), admin=Depends(require_admin)):
    return db.query(models.Loan).filter(models.Loan.status == "pending").all()

@app.put("/loans/{loan_id}/approve/", response_model=schemas.LoanResponse, tags=["Loan"])
def approve_loan(loan_id: int, override: bool = False, db: Session = Depends(get_db), admin=Depends(require_admin)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")

    # check active loan override
    active_loan = db.query(models.Loan).filter(
        models.Loan.customer_id == loan.customer_id,
        models.Loan.status == "active"
    ).first()
    if active_loan and not override:
        raise HTTPException(status_code=400, detail="Customer has active loan. Pass override=true to approve anyway.")

    loan.status = "active"
    loan.approved_by = admin.id
    loan.admin_override = override
    db.commit()
    db.refresh(loan)

    add_notification(db, loan.customer_id, f"Your loan of {loan.loan_amount} has been approved!")
    return loan

@app.put("/loans/{loan_id}/reject/", response_model=schemas.LoanResponse, tags=["Loan"])
def reject_loan(loan_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    loan.status = "rejected"
    db.commit()
    db.refresh(loan)
    add_notification(db, loan.customer_id, f"Your loan of {loan.loan_amount} has been rejected.")
    return loan

@app.put("/loans/{loan_id}/pay/", response_model=schemas.LoanResponse, tags=["Loan"])
def pay_emi(loan_id: int, amount: float, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    loan = db.query(models.Loan).filter(
        models.Loan.id == loan_id,
        models.Loan.customer_id == current_user.id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status != "active":
        raise HTTPException(status_code=400, detail="Loan is not active")

    loan.balance_amount -= amount
    if loan.balance_amount <= 0:
        loan.balance_amount = 0
        loan.status = "paid"
        add_notification(db, current_user.id, "Congratulations! Your loan is fully paid.")

    db.commit()
    db.refresh(loan)
    return loan

@app.get("/loans/{loan_id}/alert/", tags=["Loan"])
def check_alert(loan_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status == "paid":
        return {"alert": False, "message": "Loan already paid"}

    today = date.today().day
    if 25 <= today <= 30:
        return {"alert": True, "message": f"EMI due! Pay between day 1-5. Balance: {loan.balance_amount}"}
    return {"alert": False, "message": "No alert. EMI due on day 1-5 of next month."}

@app.put("/loans/{loan_id}/recalculate/", response_model=schemas.LoanResponse, tags=["Loan"])
def recalculate_interest(loan_id: int, db: Session = Depends(get_db), admin=Depends(require_admin)):
    loan = db.query(models.Loan).filter(models.Loan.id == loan_id).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    if loan.status != "active":
        raise HTTPException(status_code=400, detail="Loan is not active")

    days_since = (date.today() - loan.last_interest_date).days
    if days_since >= 30:
        interest = (loan.balance_amount * loan.interest_rate) / 100
        loan.balance_amount += interest
        loan.last_interest_date = date.today()
        db.commit()
        db.refresh(loan)
        add_notification(db, loan.customer_id, f"Interest of {interest} added to your loan. New balance: {loan.balance_amount}")

    return loan

# ── Notifications ─────────────────────────────────

@app.get("/notifications/", response_model=list[schemas.NotificationResponse], tags=["Notification"])
def get_notifications(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return db.query(models.Notification).filter(
        models.Notification.user_id == current_user.id,
        models.Notification.is_read == False
    ).all()

@app.put("/notifications/{notif_id}/read/", tags=["Notification"])
def mark_read(notif_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    notif = db.query(models.Notification).filter(
        models.Notification.id == notif_id,
        models.Notification.user_id == current_user.id
    ).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notification not found")
    notif.is_read = True
    db.commit()
    return {"message": "Marked as read"}