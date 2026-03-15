import os
import io
import numpy as np
import httpx
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# .env ファイルがあれば読み込む
load_dotenv()

# ==========================================
# 1. API キーとモデルの設定
# ==========================================
# 環境変数 GOOGLE_API_KEY が設定されていることを前提とします
# 設定されていない場合は、エラーになるか、ここで直接代入してください
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("⚠️ 警告: GOOGLE_API_KEYが設定されていません。")
    print("環境変数に設定するか、.envファイルを作成して GOOGLE_API_KEY=あなたのキー を記述してください。")
    exit(1)

genai.configure(api_key=api_key)
model_name = "models/gemini-embedding-2-preview"

# ==========================================
# 2. ユーティリティ関数
# ==========================================
def download_image(url: str) -> Image.Image:
    print(f"画像をダウンロード中: {url}")
    response = httpx.get(url)
    response.raise_for_status()
    return Image.open(io.BytesIO(response.content))

def compute_cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def get_embedding(content):
    result = genai.embed_content(
        model=model_name,
        content=content
    )
    return result['embedding']

# ==========================================
# 3. Gemini Embedding 2の真価（マルチモーダル・同一空間へのマッピング）をテスト
# ==========================================
print("=== Gemini Embedding 2 テスト開始 ===")

# (A) サンプル画像の準備
image_urls = {
    "犬の画像": "https://upload.wikimedia.org/wikipedia/commons/thumb/c/c8/Golden_Retriever_puppy_standing.jpg/320px-Golden_Retriever_puppy_standing.jpg",
    "猫の画像": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/4d/Cat_November_2010-1a.jpg/320px-Cat_November_2010-1a.jpg",
    "車の画像": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/df/Porsche_911_Carrera_S.jpg/320px-Porsche_911_Carrera_S.jpg"
}

images = {}
for name, url in image_urls.items():
    images[name] = download_image(url)

# (B) テキストプロンプトの準備
texts = [
    "かわいい犬の写真",
    "可愛らしい猫の画像",
    "スポーツカー",
    "動物"
]

print("\n--- エンベディングの取得中 ---")
embeddings = {}

# 画像のエンベディング
for name, img in images.items():
    embeddings[name] = get_embedding(img)
    print(f"{name} のエンベディング取得完了 (次元数: {len(embeddings[name])})")

# テキストのエンベディング
for text in texts:
    embeddings[text] = get_embedding(text)
    print(f"「{text}」 のエンベディング取得完了")

# ==========================================
# 4. 類似度（コサイン類似度）の計算と表示
# ==========================================
print("\n--- 類似度の比較結果（画像とテキストが同じベクトル空間にあるかどうかの検証） ---")

for text in texts:
    print(f"\n▶ テキスト: 「{text}」")
    for img_name in images.keys():
        sim = compute_cosine_similarity(embeddings[text], embeddings[img_name])
        print(f"  vs {img_name}: {sim:.4f}")

# ==========================================
# 5. Interleaved (テキストと画像の混合) のテスト
# ==========================================
print("\n--- Interleaved Input (画像+テキスト) のテスト ---")
interleaved_content = [
    "この動物は何ですか？",
    images["犬の画像"]
]
interleaved_emb = get_embedding(interleaved_content)
print(f"質問+犬の画像 のエンベディング取得完了 (次元数: {len(interleaved_emb)})")

sim_mixed_dog = compute_cosine_similarity(interleaved_emb, embeddings["犬の画像"])
sim_mixed_text = compute_cosine_similarity(interleaved_emb, embeddings["かわいい犬の写真"])
print(f"  vs 犬の画像のみ: {sim_mixed_dog:.4f}")
print(f"  vs かわいい犬の写真(テキストのみ): {sim_mixed_text:.4f}")

print("\nテスト完了！")