from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import timedelta
import models
from database import engine, get_db
from schemas import UserRegister, UserLogin, Token, UserResponse
from auth import hash_password, verify_password, create_access_token
from config import settings

# Create database tables
models.Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Simple authentication API with email-based registration"
)

# CORS - Allow all origins (for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Simple Auth API",
        "version": settings.APP_VERSION,
        "endpoints": {
            "register": "POST /register",
            "login": "POST /login",
            "profile": "GET /profile",
            "users": "GET /users"
        },
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    """Health check for Render"""
    return {"status": "healthy", "environment": settings.ENVIRONMENT}

@app.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """
    Register a new user with email
    
    - **email**: Valid email address (unique)
    - **username**: Username (unique, 3-50 chars)
    - **password**: Password (minimum 8 chars)
    - **full_name**: User's full name
    """
    
    # Check if email already exists
    if db.query(models.User).filter(models.User.email == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Check if username already exists
    if db.query(models.User).filter(models.User.username == user.username).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )
    
    # Create new user
    db_user = models.User(
        email=user.email,
        username=user.username,
        hashed_password=hash_password(user.password),
        full_name=user.full_name
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@app.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login with username and password
    
    Returns JWT token for authentication
    """
    
    # Find user by username
    user = db.query(models.User).filter(
        models.User.username == credentials.username
    ).first()
    
    # Verify user exists and password is correct
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Check if account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"user_id": user.id, "username": user.username},
        expires_delta=timedelta(hours=24)
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "message": f"Welcome back, {user.username}!"
    }

@app.get("/users")
def get_all_users(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """
    Get list of all registered users
    
    - **skip**: Number of users to skip (for pagination)
    - **limit**: Maximum number of users to return
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    
    return {
        "total": db.query(models.User).count(),
        "showing": len(users),
        "users": [
            {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "full_name": user.full_name,
                "created_at": user.created_at
            }
            for user in users
        ]
    }

@app.get("/users/{username}", response_model=UserResponse)
def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """Get user by username"""
    user = db.query(models.User).filter(models.User.username == username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user