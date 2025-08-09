# lumen_voice/services/image_generator.py

import os
import requests
from dotenv import load_dotenv
#from ..config import settings, translate_client
from google.cloud import translate_v2 as translate

# Carrega as variáveis de ambiente
load_dotenv()
STABILITY_KEY = os.getenv("STABILITY_KEY")
translate_client = translate.Client()

if not STABILITY_KEY:
    raise ValueError("A variável de ambiente STABILITY_KEY não está definida.")

API_URL_CORE = "https://api.stability.ai/v2beta/stable-image/generate/core"
API_URL_ULTRA = "https://api.stability.ai/v2beta/stable-image/generate/ultra"

def translate_text_if_needed(text: str) -> str:
    if not text or not translate_client:
        return text
    
    try:
        detection = translate_client.detect_language(text)
        print(f"--- DEBUG GOOGLE TRANSLATE ---")
        print(f"Texto: '{text}', Detetado: {detection}")
        print(f"-----------------------------")
        
        if detection['language'] != 'en':
            return translate_client.translate(text, target_language='en')['translatedText']
        return text
    except Exception as e:
        print(f"Erro na tradução: {e}")
        return text

def generate_stability_image(prompt: str, negative_prompt: str, model: str = "core"):
    """
    Gera uma imagem usando a API da Stability AI.
    Retorna o conteúdo da imagem em bytes e o motivo da finalização.
    """
    url = API_URL_CORE if model == "core" else API_URL_ULTRA
    
    # 4. Traduza os prompts antes de os usar
    print(f"A traduzir prompt: '{prompt}'")
    translated_prompt = translate_text_if_needed(prompt)
    translated_negative_prompt = translate_text_if_needed(negative_prompt)
    print(f"Prompt traduzido: '{translated_prompt}'")
    
    headers = {
        "Authorization": f"Bearer {STABILITY_KEY}",
        "Accept": "image/*"
    }
    
    payload = {
        "prompt": translated_prompt,
        "negative_prompt": translated_negative_prompt,
        "aspect_ratio": "1:1", # Simplificado por enquanto
        "output_format": "png"
    }

    try:
        response = requests.post(
            url,
            headers=headers,
            files={"none": ''},
            data=payload,
            timeout=180
        )
        response.raise_for_status()
        
        finish_reason = response.headers.get("finish-reason")
        image_content = response.content
        
        return image_content, finish_reason

    except requests.exceptions.HTTPError as e:
        # Re-lança a exceção para ser tratada no roteador
        raise e