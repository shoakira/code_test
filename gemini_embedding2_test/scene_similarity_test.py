import os
import io
import numpy as np
import base64
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

# .env ファイルから API キーを読み込む
load_dotenv()

api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("⚠️ 警告: GOOGLE_API_KEYが設定されていません。")
    exit(1)

genai.configure(api_key=api_key)
model_name = "models/gemini-embedding-2-preview"

def get_embedding(content):
    """
    テキストまたは画像からエンベディングを取得します。
    """
    if isinstance(content, Image.Image):
        # 画像をBytesに変換してBase64エンコード
        buffered = io.BytesIO()
        content.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        content = {"mime_type": "image/jpeg", "data": img_str}
        
    result = genai.embed_content(
        model=model_name,
        content=content
    )
    return np.array(result['embedding'])

def main():
    image_path = "image_sample.png"
    texts = [
        "晴れた日の公園で、林の中をとぼとぼと歩きながら、赤いフリスビーを踏んでいるゴールデンレトリバー",
        "曇りの日の公園で、赤い花畑の横の芝生を、緑のフリスビーを口にくわえて眠っているゴールデンレトリバー",
        "晴れた日の公園、緑の芝生、赤いフリスビー、ゴールデンレトリバー",
        "天気の良い日、芝生の上で、赤い円盤を口にくわえ、元気に草の上を走っている犬",
        "晴れた日の公園で、フリスビーという名前の男が寝そべってボールを咥えている。"
    ]

    print(f"--- 処理開始 ---")
    
    # 画像のエンベディング取得
    if not os.path.exists(image_path):
        print(f"❌ エラー: {image_path} が見つかりません。")
        return
    
    img = Image.open(image_path).convert("RGB")
    img_emb = get_embedding(img)
    print("✅ 画像のエンベディング取得完了")

    results = []
    for i, text in enumerate(texts):
        text_emb = get_embedding(text)
        # 内積 (Dot Product) の計算
        dot_product = np.dot(img_emb, text_emb)
        
        # 参考としてコサイン類似度も計算 (正規化されたベクトル同士の点乗)
        norm_img = np.linalg.norm(img_emb)
        norm_text = np.linalg.norm(text_emb)
        cosine_sim = dot_product / (norm_img * norm_text)
        
        results.append({
            "id": i + 1,
            "text": text,
            "dot": dot_product,
            "cosine": cosine_sim
        })
        print(f"✅ テキスト {i+1} の処理完了")

    print("\n--- 比較結果 (類似度) ---")
    # 類似度が高い順にソートして表示
    results.sort(key=lambda x: x["dot"], reverse=True)
    
    for r in results:
        print(f"\n【第 {r['id']} 案】")
        print(f"内容: {r['text']}")
        print(f"類似度: {r['dot']:.4f}")

if __name__ == "__main__":
    main()
