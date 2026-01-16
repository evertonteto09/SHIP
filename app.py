from flask import Flask, request, send_file
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

app = Flask(__name__)

@app.route("/ship")
def ship():
    try:
        a1 = request.args.get("a1")
        a2 = request.args.get("a2")
        p = request.args.get("p")

        # 🔒 Validação
        if not a1 or not a2 or not p:
            return "Use ?a1=URL&a2=URL&p=NUMERO", 400

        percent = int(p)
        percent = max(0, min(percent, 100))

        # 🖼️ Base
        base = Image.open("base.png").convert("RGBA")

        # 👤 Avatar loader
        def load_avatar(url):
            r = requests.get(url, timeout=5)
            img = Image.open(BytesIO(r.content)).convert("RGBA")
            return img.resize((220, 220))

        av1 = load_avatar(a1)
        av2 = load_avatar(a2)

        # 🔵 Avatar circular
        def circle(img):
            mask = Image.new("L", img.size, 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, img.size[0], img.size[1]), fill=255)
            img.putalpha(mask)
            return img

        av1 = circle(av1)
        av2 = circle(av2)

        # 📍 Colar avatares
        base.paste(av1, (210, 240), av1)
        base.paste(av2, (690, 240), av2)

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
        heart = heart.resize((140, 140))

        # 📍 Colar coração (centro)
        base.paste(heart, (520, 300), heart)

        # 📊 Barra de porcentagem
        draw = ImageDraw.Draw(base)
        bar_x, bar_y = 250, 620
        bar_w, bar_h = 500, 40
        fill_w = int(bar_w * (percent / 100))

        draw.rounded_rectangle(
            (bar_x, bar_y, bar_x + bar_w, bar_y + bar_h),
            radius=20,
            fill=(120, 120, 120, 180)
        )

        draw.rounded_rectangle(
            (bar_x, bar_y, bar_x + fill_w, bar_y + bar_h),
            radius=20,
            fill=(255, 105, 180)
        )

        # 🔤 Texto
        try:
            font = ImageFont.truetype("font.ttf", 32)
        except:
            font = ImageFont.load_default()

        text = f"{percent}%"
        text_w, text_h = draw.textsize(text, font=font)

        draw.text(
            (bar_x + (bar_w - text_w) // 2, bar_y + 5),
            text,
            fill="white",
            font=font
        )

        # 💾 Retorno
        output = BytesIO()
        base.save(output, format="PNG")
        output.seek(0)

        return send_file(output, mimetype="image/png")

    except Exception as e:
        return f"Erro interno: {e}", 500
