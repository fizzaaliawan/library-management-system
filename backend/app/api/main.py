from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import auth, books, members, loans, notifications
from app.database.session import engine
from app.models.models import Base

# Autocreate tables on startup for simplicity in dev/docker environments
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs"
)

# CORS configurations
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production-ready setups
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(books.router, prefix=f"{settings.API_V1_STR}/books", tags=["books"])
app.include_router(members.router, prefix=f"{settings.API_V1_STR}/members", tags=["members"])
app.include_router(loans.router, prefix=f"{settings.API_V1_STR}/loans", tags=["loans"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Library Management System (LMS) API"}
