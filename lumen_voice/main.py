from fastapi import FastAPI
from .database import engine
from . import models
from .routers import authentication, images
from fastapi.middleware.cors import CORSMiddleware
from .routers import authentication, images, billing, config_router # Adicione billing

# Cria as tabelas no banco de dados, se não existirem
models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Lumen Voice API",
    description="API for generating AI content.",
    version="0.1.0"
)

# ▼▼▼ ADICIONE ESTE BLOCO DE CÓDIGO ▼▼▼
# 2. Defina as "origens" permitidas (de onde o nosso front-end virá)
origins = [
    "http://localhost:3000", 
    "https://lumen-voice-app.vercel.app",# A nossa aplicação Next.js
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,       
    allow_credentials=True,
    allow_methods=["*"],         
    allow_headers=["*"],         
)

app.include_router(authentication.router)
app.include_router(images.router) 
app.include_router(billing.router) 
app.include_router(config_router.router)

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to Lumen Voice API"}