from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from ..auth import get_current_user

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

@router.get("/users/me", response_model=schemas.User, summary="Get current user details")
def read_users_me(current_user: schemas.User = Depends(get_current_user)):
    """
    Retorna os detalhes do utilizador atualmente autenticado.
    A dependência `get_current_user` faz toda a magia de verificar o token.
    """
    return current_user

@router.put("/users/password", summary="Update user password")
def update_password(
    password_data: schemas.PasswordUpdate,
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user)
):
    # Verifica se a senha atual está correta
    if not security.verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(status_code=400, detail="Senha atual incorreta")
    
    # Cria o hash da nova senha
    new_hashed_password = security.get_password_hash(password_data.new_password)
    
    # Atualiza no banco de dados
    crud.update_user_password(db, user_id=current_user.id, new_hashed_password=new_hashed_password)
    
    return {"message": "Senha atualizada com sucesso"}