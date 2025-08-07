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

class ImageRequest(BaseModel):
    prompt: str
    negative_prompt: str = ""
    model: str = "core" # Permite ao usuário escolher entre 'core' e 'ultra'

class TokenData(BaseModel):
    email: str | None = None