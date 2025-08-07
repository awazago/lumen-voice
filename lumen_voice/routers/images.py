# lumen_voice/routers/images.py
import os
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from .. import schemas
from ..auth import get_current_user
from ..database import get_db
from ..services import image_generator
import requests

router = APIRouter(
    prefix="/images", # Adiciona /images antes de todas as rotas aqui
    tags=["Images"]
)

@router.post("/generate", summary="Generate a new image")
def generate_image(
    request: schemas.ImageRequest, # Usaremos um schema para o corpo da requisição
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(get_current_user) # <-- A MÁGICA DA SEGURANÇA!
):
    """
    Gera uma nova imagem para o usuário autenticado.
    """
    # Futuramente, aqui virá a lógica de verificação de créditos do `current_user`

    try:
        image_content, finish_reason = image_generator.generate_stability_image(
            prompt=request.prompt,
            negative_prompt=request.negative_prompt,
            model=request.model # Adicionaremos 'model' ao nosso schema
        )

        if finish_reason == 'CONTENT_FILTERED':
            raise HTTPException(
                status_code=400,
                detail="A geração falhou porque o prompt foi classificado como inseguro."
            )

        # Salva a imagem em um diretório específico do usuário
        output_dir = f"generated_images/user_{current_user.id}"
        os.makedirs(output_dir, exist_ok=True)
        
        # Gera um nome de arquivo único
        file_path = os.path.join(output_dir, f"{current_user.id}_{os.urandom(8).hex()}.png")

        with open(file_path, "wb") as f:
            f.write(image_content)

        # Futuramente, salvaremos o `file_path` no banco de dados, associado ao usuário.

        # Retorna a imagem diretamente como um arquivo para o navegador/cliente
        return FileResponse(file_path, media_type="image/png")

    except requests.exceptions.HTTPError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Erro da API da Stability AI: {e.response.text}"
        )