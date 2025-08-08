import yaml # 1. Importe a biblioteca YAML
from pydantic_settings import BaseSettings, SettingsConfigDict

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
    
    # 3. Adicione os custos carregados às nossas configurações
    COST_CONFIG: dict = COSTS

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()