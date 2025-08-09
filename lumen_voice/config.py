import yaml # 1. Importe a biblioteca YAML
from pydantic_settings import BaseSettings, SettingsConfigDict
from google.cloud import translate_v2 as translate

# 2. Carregue os custos do ficheiro YAML
with open("costs.yaml", "r") as f:
    COSTS = yaml.safe_load(f)

class Settings(BaseSettings):
    SECRET_KEY: str
    STABILITY_KEY: str
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    PRICE_ID_HOBBY: str
    PRICE_ID_PRO: str
    
    #GOOGLE_TRANSLATE_API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS: str
    # 3. Adicione os custos carregados às nossas configurações
    COST_CONFIG: dict = COSTS

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()

# lumen_voice/config.py

#try:
    # Passamos a nossa chave de API explicitamente para a autenticação
#    translate_client = translate.Client(api_key=settings.GOOGLE_TRANSLATE_API_KEY)
#    print("Cliente do Google Translate inicializado com sucesso.")
#except Exception as e:
#    print(f"AVISO: Não foi possível inicializar o cliente do Google Translate. Erro: {e}")
#    translate_client = None