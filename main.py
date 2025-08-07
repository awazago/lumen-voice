from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

import crud, models, schemas, security
from database import SessionLocal, engine

# Cria as tabelas no banco de dados (apenas na primeira vez)
models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Função para obter a sessão do banco de dados
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- ENDPOINT DE CADASTRO ---
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)

# --- ENDPOINT DE LOGIN (GERAÇÃO DE TOKEN) ---
@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email=form_data.username) # O form usa 'username' para o email
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

# --- EXEMPLO DE ENDPOINT PROTEGIDO ---
@app.get("/users/me/", response_model=schemas.User)
async def read_users_me():
    # A lógica para pegar o usuário atual a partir do token virá aqui depois
    # Por enquanto, é só para mostrar a estrutura
    # Este endpoint futuramente só funcionará se o usuário enviar um token válido
    pass