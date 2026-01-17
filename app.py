from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

app = Flask(__name__)

@app.route("/ship")
def ship():
    try:
        avatar1 = request.args.get("a1")
        avatar2 = request.args.get("a2")
        percent = request.args.get("p")

        # 🚨 Verificação OBRIGATÓRIA
        if not avatar1 or not avatar2 or not percent:
            return "Parâmetros faltando: use ?a1=URL&a2=URL&p=NUMERO", 400

        percent = int(percent)
        if percent < 0: percent = 0
        if percent > 100: percent = 100

        # Base
        base = Image.open("base.png").convert("RGBA")

        # Avatares
        def load_avatar(url):
            r = requests.get(url, timeout=5)
            img = Image.open(BytesIO(r.content)).convert("RGBA")
            return img.resize((220, 220))

        avatar1_img = load_avatar(avatar1)
        avatar2_img = load_avatar(avatar2)

        # Máscara redonda
        def circle(img):
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
            img.putalpha(mask)
            return img

        avatar1_img = circle(avatar1_img)
        avatar2_img = circle(avatar2_img)

        # Colar avatares (ajuste se quiser)
        base.paste(avatar1_img, (100, 290), avatar1_img)
        base.paste(avatar2_img, (890, 290), avatar2_img)

# ❤️ Selecionar coração
        if percent <= 25:
            heart_file = "heart1.png"
        elif percent <= 49:
            heart_file = "heart2.png"
        elif percent <= 80:
            heart_file = "heart3.png"
        else:
            heart_file = "heart4.png"

        heart = Image.open(heart_file).convert("RGBA")
        heart = heart.resize((332, 332))

        # 📍 Colar coração (centro)
        base.paste(heart, (450, 240), heart)

        # Barra de porcentagem
        draw = ImageDraw.Draw(base)
        bar_x, bar_y = 250, 620
        bar_w, bar_h = 500, 40
        fill_w = int(bar_w * (percent / 100))

        draw.rounded_rectangle(
            [bar_x, bar_y, bar_x + fill_w, bar_y + bar_h],
            radius=20,
            fill=(255, 105, 180)
        )

        # Texto
        try:
            font = ImageFont.truetype("font.ttf", 32)
        except:
            font = ImageFont.load_default()

        draw.text(
            (bar_x + bar_w // 2 - 30, bar_y + 5),
            f"{percent}%",
            fill="white",
            font=font
        )

        output = BytesIO()
        base.save(output, format="PNG")
        output.seek(0)

        return send_file(output, mimetype="image/png")

    except Exception as e:
        return f"Erro interno: {e}", 500
