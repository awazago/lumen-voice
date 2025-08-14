# lumen_voice/services/watermark.py
from PIL import Image, ImageDraw, ImageFont
import io

def add_watermark(image_bytes: bytes) -> bytes:
    try:
        # Abre a imagem a partir dos bytes recebidos
        image = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

        # Cria uma camada transparente para desenhar a marca d'água
        txt_layer = Image.new("RGBA", image.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Define o texto e a fonte (pode precisar de ajustar o caminho da fonte)
        text = "Criado com LumenVoice.ai"
        try:
            font = ImageFont.truetype("arial.ttf", size=40)
        except IOError:
            font = ImageFont.load_default() # Fonte padrão caso a Arial não seja encontrada

        # Posição da marca d'água (canto inferior direito)
        text_width, text_height = draw.textbbox((0,0), text, font=font)[2:]
        position = (image.width - text_width - 20, image.height - text_height - 20)

        # Desenha o texto com transparência
        draw.text(position, text, font=font, fill=(255, 255, 255, 128)) # Branco com 50% de opacidade

        # Combina a imagem original com a camada de texto
        watermarked_image = Image.alpha_composite(image, txt_layer)

        # Salva a imagem final de volta para bytes
        byte_arr = io.BytesIO()
        watermarked_image.convert("RGB").save(byte_arr, format='PNG')

        return byte_arr.getvalue()
    except Exception as e:
        print(f"AVISO: Falha ao adicionar marca d'água. Erro: {e}")
        return image_bytes # Retorna a imagem original em caso de erro