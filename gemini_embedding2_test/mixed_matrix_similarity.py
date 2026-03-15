import os
import io
import numpy as np
import base64
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

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
    try:
        if isinstance(content, str) and os.path.exists(content) and (content.endswith('.png') or content.endswith('.jpg') or content.endswith('.jpeg')):
            # 画像ファイルの場合
            img = Image.open(content).convert("RGB")
            buffered = io.BytesIO()
            img.save(buffered, format="JPEG")
            img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
            payload = {"mime_type": "image/jpeg", "data": img_str}
        else:
            # テキストの場合
            payload = content
            
        result = genai.embed_content(
            model=model_name,
            content=payload
        )
        return np.array(result['embedding'])
    except Exception as e:
        print(f"❌ '{content}' の取得エラー: {e}")
        return None

def main():
    # 比較対象のミックスリスト (画像2つ、テキスト2つ)
    items = [
        {"type": "image", "content": "image1.png", "label": "Img: image1"},
        {"type": "image", "content": "image2.png", "label": "Img: image2"},
        {"type": "text", "content": "晴れた日の公園で、赤いフリスビーを口にくわえて緑の芝生の上を走っているゴールデンレトリバー", "label": "Txt: Running Dog"},
        {"type": "text", "content": "公園の芝生に置かれた赤いフリスビーの横で、犬が伏せて休んでいる様子", "label": "Txt: Resting Dog"},
        {"type": "text", "content": "公園の芝生で、猫が何かを咥えて走っている。", "label": "Txt: Running Cat"}
    ]

    print(f"--- {len(items)} つの要素（画像とテキスト）のエンベディングを取得中 ---")
    
    embeddings = []
    labels = []
    
    for item in items:
        # 画像ファイルが存在するかチェック (画像タイプのみ)
        if item["type"] == "image" and not os.path.exists(item["content"]):
            print(f"⚠️ 警告: 画像ファイル {item['content']} が見当たらないためスキップします。")
            continue
            
        emb = get_embedding(item["content"])
        if emb is not None:
            embeddings.append(emb)
            labels.append(item["label"])
            print(f"✅ {item['label']} 完了")

    if len(embeddings) < 2:
        print("比較には少なくとも2つ以上の要素が必要です。")
        return

    # 類似度マトリックスの計算
    num_items = len(embeddings)
    matrix = np.zeros((num_items, num_items))
    
    for i in range(num_items):
        for j in range(num_items):
            # コサイン類似度
            dot = np.dot(embeddings[i], embeddings[j])
            norm_i = np.linalg.norm(embeddings[i])
            norm_j = np.linalg.norm(embeddings[j])
            # Gemini Embedding 2 は既に正規化されていますが念のため
            matrix[i, j] = dot / (norm_i * norm_j)

    print("\n--- 類似度マトリックスを作成中 ---")
    
    # グラフの作成
    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix, annot=True, fmt=".3f", cmap="YlGnBu",
                xticklabels=labels, yticklabels=labels)
    plt.title("Mixed Similarity Matrix (Images & Texts)")
    plt.tight_layout()
    
    # 保存
    output_img = "mixed_similarity_matrix.png"
    plt.savefig(output_img)
    print(f"🎉 マトリックス図を '{output_img}' に保存しました。")
    
    # ターミナル用
    print("\n【簡易マトリックス】")
    header = "          " + "".join([f"{l:>15}" for l in labels])
    print(header)
    for i, row in enumerate(matrix):
        row_str = f"{labels[i]:<15}" + "".join([f"{val:15.3f}" for val in row])
        print(row_str)

if __name__ == "__main__":
    main()
