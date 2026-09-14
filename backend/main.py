from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from database import Base, engine

from models.user import User
from models.document import Document
from models.customer import Customer
from models.transaction import Transaction

from routes.auth import router as auth_router
from routes.documents import router as documents_router
from routes.approval import router as approval_router
from routes.dashboard import router as dashboard_router
from routes.settings import router as settings_router
from routes.customers import router as customers_router


# ==========================================
# CREATE DATABASE TABLES
# ==========================================

Base.metadata.create_all(bind=engine)


# ==========================================
# FASTAPI APP
# ==========================================

app = FastAPI(
    title="FinFlow AI",
    description=(
        "AI-Powered Accounting Operations "
        "and Agentic Workflow Automation Platform"
    ),
    version="1.0.0"
)


# ==========================================
# CORS
# ==========================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"]
)


# ==========================================
# ROUTES
# ==========================================

app.include_router(auth_router)

app.include_router(documents_router)

app.include_router(approval_router)

app.include_router(dashboard_router)

app.include_router(settings_router)

app.include_router(customers_router)


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():

    return {
        "message":
            "FinFlow AI Backend is Running",

        "status":
            "success",

        "platform":
            (
                "AI-Powered Accounting "
                "Operations & Agentic Workflow"
            )
    }
