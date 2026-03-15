import google.generativeai as genai

# APIキーの設定
genai.configure(api_key="YOUR_API_KEY")

# 最新のプレビューモデルを指定
model_name = "models/gemini-embedding-2-preview"

# 例: 画像とテキストを同時にエンベディング（Interleaved Input）
# ※画像はPillow(PIL)で読み込んだものや、File APIでアップロードしたものを指定
result = genai.embed_content(
    model=model_name,
    content=[
        "この機器の電源の入れ方を教えてください",
        image_file  # 機器の写真
    ]
)

# 3072次元のベクトルが取得できる
print(result['embedding'])