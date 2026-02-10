import requests
from PIL import Image
from io import BytesIO
from openai import OpenAI
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import textwrap
import base64
import sys

client = OpenAI()

# URL指定の画像
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
#image_url = "https://commons.wikimedia.org/wiki/London#/media/File:Barking_Town_Hall_-_geograph.org.uk_-_1210124.jpg"


# Download the image first
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
try:
    response_image = requests.get(image_url, headers=headers)
    response_image.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Failed to download image: {e}")
    sys.exit(1)

# Encode image to base64
base64_image = base64.b64encode(response_image.content).decode('utf-8')
data_url = f"data:image/jpeg;base64,{base64_image}"

try:
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "What's in this image? Please explain in Japanese."},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": data_url,
                        },
                    },
                ],
            }
        ],
        max_tokens=300,
    )
except Exception as e:
    print(f"OpenAI API Error: {e}")
    sys.exit(1)


# LLMからの解説を取得
explanation = response.choices[0]
print(explanation.message.content)
text = explanation.message.content
# キャプションを適切な長さで改行
wrapped_explanation = "\n".join(textwrap.wrap(text, width=35))  # 40文字ごとに改行


# Use already downloaded content
try:
    img = Image.open(BytesIO(response_image.content))  # バイトデータをPillow形式に変換
except Exception as e:
    print(f"Failed to open image: {e}")
    sys.exit(1)

# 画像を表示し、キャプションとしてLLMの解説を表示
plt.figure(figsize=(8, 8))  # matplotlibで表示サイズを指定
plt.imshow(img)  # 画像をプロット
plt.axis("off")  # 軸を非表示
plt.title(wrapped_explanation, fontsize=12, loc='center')  # 改行済みキャプションを使用
try:
    plt.show()  # プロットを表示
except Exception as e:
    print(f"Failed to show plot (possibly no display): {e}")
