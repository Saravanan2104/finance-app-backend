# Finance App API

A FastAPI-based Finance Management System for handling customer registration, loan applications, approvals, EMI payments, interest calculation, and notifications.

---

## Features

### Authentication

* Customer Registration
* Customer Login
* JWT Token Authentication
* Admin Role Authorization

### Customer Management

* Create Customer
* Get All Customers
* Get Customer By ID
* Update Customer
* Delete Customer

### Loan Management

* Apply Loan
* Loan Approval Workflow
* Loan Rejection Workflow
* Get All Loans
* Get Customer Loans
* Get Pending Loans
* EMI Payment
* Interest Recalculation
* Loan Eligibility Validation

### Notifications

* Admin Notifications
* Customer Notifications
* Mark Notification as Read

---

# Business Workflow

## New Customer Loan

Customer applies for a loan.

```text
Apply Loan
↓
Pending
↓
Admin Review
↓
Approve?
    Yes → Active
    No  → Rejected
```

---

## Existing Customer Loan

Customer already has an active loan.

```text
Loan A = Active

Customer Applies Loan B
↓
Loan B = Pending
```

### If Admin Rejects

```text
Loan A = Active
Loan B = Rejected
```

### If Admin Approves

```text
Loan A = Closed
Loan B = Active
```

This ensures that an active loan is never closed until the new loan is approved.

---

# Loan Eligibility Rules

A customer can apply for a new loan while having an active loan.

Before creating the application:

```text
Net Amount =
Requested Loan
- Interest
- Existing Loan Balance
```

### Example

```text
Requested Loan = 10000
Interest Rate = 2.10%
Interest = 210

Old Balance = 3000

Net Amount =

10000
-210
-3000
------
6790
```

Customer will receive:

```text
₹6790
```

---

## Not Eligible Condition

```text
Requested Loan = 10000

Old Balance = 11000

Interest = 210

Net Amount =

10000
-11000
-210
-------
-1210
```

Result:

```text
Loan Rejected
Not Eligible
```

Because the outstanding balance exceeds the requested loan amount.

---

# Interest Deduction Logic

Interest is deducted before disbursement.

Example:

```text
Loan Amount = 10000
Interest Rate = 2.10%

Interest = 210

Customer Receives

10000 - 210

= 9790
```

---

# Interest Recalculation

Interest is calculated on the remaining balance.

Example:

```text
Loan Amount = 10000

Customer Pays = 4000

Remaining Balance = 6000
```

Next interest calculation:

```text
6000 × Interest Rate
```

Interest is always calculated on the remaining outstanding balance.

---

# API Endpoints

## Authentication

### Register

POST

```http
/register/
```

### Login

POST

```http
/login/
```

---

## Customers

### Get All Customers

GET

```http
/customers/
```

### Get Customer

GET

```http
/customers/{customer_id}
```

### Update Customer

PUT

```http
/customers/{customer_id}
```

### Delete Customer

DELETE

```http
/customers/{customer_id}
```

---

## Loans

### Apply Loan

POST

```http
/loans/apply/
```

### Get All Loans

GET

```http
/loans/
```

### Get My Loans

GET

```http
/loans/my/
```

### Get Pending Loans

GET

```http
/loans/pending/
```

### Approve Loan

PUT

```http
/loans/{loan_id}/approve/
```

### Reject Loan

PUT

```http
/loans/{loan_id}/reject/
```

### Pay EMI

PUT

```http
/loans/{loan_id}/pay/
```

### Loan Alert

GET

```http
/loans/{loan_id}/alert/
```

### Recalculate Interest

PUT

```http
/loans/{loan_id}/recalculate/
```

---

## Notifications

### Get Notifications

GET

```http
/notifications/
```

### Mark Notification Read

PUT

```http
/notifications/{notif_id}/read/
```

---

# Tech Stack

* FastAPI
* SQLAlchemy
* SQLite
* JWT Authentication
* Passlib (bcrypt)
* Pydantic
* Python-Jose

---

# Installation

Clone the repository:

```bash
git clone <repository-url>
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run application:

```bash
uvicorn main:app --reload
```

Swagger Documentation:

```text
http://localhost:8000/docs
```

ReDoc Documentation:

```text
http://localhost:8000/redoc
```

---

# Future Enhancements

* Aadhaar File Upload
* PAN File Upload
* Customer Photo Upload
* Loan Payment History
* EMI Schedule
* Automatic Reminder Notifications
* SMS Integration
* WhatsApp Integration
* AWS S3 Document Storage
* PostgreSQL Migration
* Audit Logs
* Loan Disbursement Reports
