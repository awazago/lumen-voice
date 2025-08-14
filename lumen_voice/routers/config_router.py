from fastapi import APIRouter
from ..config import settings

router = APIRouter(
    prefix="/config",
    tags=["Configuration"]
)

@router.get("/costs", summary="Get the cost configuration for different models")
def get_costs():
    """
    Retorna a configuração de custos carregada a partir do ficheiro costs.yaml.
    """
    return settings.COST_CONFIG