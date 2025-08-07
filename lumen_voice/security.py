from passlib.context import CryptContext
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os
from dotenv import load_dotenv


load_dotenv()
# Configuração do Hashing de Senha
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuração do Token JWT
# ESTA CHAVE DEVE ESTAR NUM ARQUIVO .env E NÃO NO CÓDIGO!
# Gere uma chave forte com: openssl rand -hex 32
SECRET_KEY = os.getenv("TOKEN") 
if SECRET_KEY is None:
    raise ValueError("A variável de ambiente SECRET_KEY não foi definida!")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt