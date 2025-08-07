from pydantic import BaseModel

# Esquema para a criação de um usuário (o que recebemos da API)
class UserCreate(BaseModel):
    email: str
    password: str

# Esquema para ler os dados de um usuário (o que enviamos pela API, sem a senha!)
class User(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True # Ajuda o Pydantic a converter o modelo do SQLAlchemy

class TokenData(BaseModel):
    email: str | None = None