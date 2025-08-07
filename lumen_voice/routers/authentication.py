from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

# Importações relativas, pois estamos dentro do mesmo pacote
from .. import crud, schemas, security
from ..database import get_db

# 1. Crie o APIRouter
router = APIRouter(
    tags=["Authentication"] # Opcional: Agrupa os endpoints na documentação /docs
)

# 2. Mude todos os @app.post para @router.post
@router.post("/users/", response_model=schemas.User, summary="Register a new user")
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

@router.post("/token", summary="Login and get an access token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = security.create_access_token(
        data={"sub": user.email}
    )
    return {"access_token": access_token, "token_type": "bearer"}

# O endpoint de /users/me/ ficará aqui depois, quando implementarmos a proteção por token