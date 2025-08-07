from fastapi import FastAPI
from .database import engine
from . import models
from .routers import authentication, images

# Cria as tabelas no banco de dados, se não existirem
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lumen Voice API",
    description="API for generating AI content.",
    version="0.1.0"
)

# Inclui o roteador de autenticação no aplicativo principal
app.include_router(authentication.router)
app.include_router(images.router) # 2. Adicione o roteador de imagens

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Lumen Voice API"}