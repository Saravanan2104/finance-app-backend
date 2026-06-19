from fastapi import APIRouter

from v1.endpoints.auth import router as auth_router
from v1.endpoints.customers import router as customer_router
from v1.endpoints.loans import router as loan_router
from v1.endpoints.notifications import router as notification_router

api_router = APIRouter(
    prefix="/api/v1"
)

api_router.include_router(auth_router)
api_router.include_router(customer_router)
api_router.include_router(loan_router)
api_router.include_router(notification_router)