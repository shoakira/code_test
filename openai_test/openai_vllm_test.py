import requests
from PIL import Image
from io import BytesIO
from openai import OpenAI
import numpy as np
import matplotlib.pyplot as plt
import japanize_matplotlib
import textwrap

client = OpenAI()

# URL指定の画像
image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"

#image_url = "https://commons.wikimedia.org/wiki/London#/media/File:Barking_Town_Hall_-_geograph.org.uk_-_1210124.jpg"


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
                        "url": image_url,
                    },
                },
            ],
        }
    ],
    max_tokens=300,
)


# LLMからの解説を取得
explanation = response.choices[0]
print(explanation.message.content)
text = explanation.message.content
# キャプションを適切な長さで改行
wrapped_explanation = "\n".join(textwrap.wrap(text, width=35))  # 40文字ごとに改行


response_image = requests.get(image_url)  # 画像をURLから取得
img = Image.open(BytesIO(response_image.content))  # バイトデータをPillow形式に変換

# 画像を表示し、キャプションとしてLLMの解説を表示
plt.figure(figsize=(8, 8))  # matplotlibで表示サイズを指定
plt.imshow(img)  # 画像をプロット
plt.axis("off")  # 軸を非表示
plt.title(wrapped_explanation, fontsize=12, loc='center')  # 改行済みキャプションを使用
plt.show()  # プロットを表示
