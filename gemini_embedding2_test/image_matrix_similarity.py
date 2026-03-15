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

def get_embedding(image_path):
    """
    画像からエンベディングを取得します。
    """
    try:
        img = Image.open(image_path).convert("RGB")
        # 画像をBytesに変換してBase64エンコード
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        content = {"mime_type": "image/jpeg", "data": img_str}
        
        result = genai.embed_content(
            model=model_name,
            content=content
        )
        return np.array(result['embedding'])
    except Exception as e:
        print(f"❌ '{image_path}' の取得エラー: {e}")
        return None

def main():
    # 比較する画像のリストをユーザー指定のものに固定
    image_files = [
        "image_sample.png",
        "image_sample2.png",
        "image_sample3.png"
    ]
    
    # 実際に存在するファイルのみに絞り込む
    image_files = [f for f in image_files if os.path.exists(f)]
    
    if len(image_files) < 2:
        print("比較には少なくとも2枚以上の画像が必要です。")
        return

    print(f"--- {len(image_files)} 枚の画像のエンベディングを取得中 ---")
    
    embeddings = []
    valid_files = []
    
    for f in image_files:
        emb = get_embedding(f)
        if emb is not None:
            embeddings.append(emb)
            valid_files.append(os.path.basename(f))
            print(f"✅ {f} 完了")

    # 類似度マトリックスの計算
    num_images = len(embeddings)
    matrix = np.zeros((num_images, num_images))
    
    for i in range(num_images):
        for j in range(num_images):
            # コサイン類似度
            dot = np.dot(embeddings[i], embeddings[j])
            norm_i = np.linalg.norm(embeddings[i])
            norm_j = np.linalg.norm(embeddings[j])
            matrix[i, j] = dot / (norm_i * norm_j)

    print("\n--- 類似度マトリックスを作成中 ---")
    
    # グラフの作成
    plt.figure(figsize=(10, 8))
    sns.heatmap(matrix, annot=True, fmt=".3f", cmap="YlGnBu",
                xticklabels=valid_files, yticklabels=valid_files)
    plt.title("Image Similarity Matrix (Gemini Embedding 2)")
    plt.tight_layout()
    
    # 保存
    output_img = "similarity_matrix.png"
    plt.savefig(output_img)
    print(f"🎉 マトリックス図を '{output_img}' に保存しました。")
    
    # 表示用の簡単な表もターミナルに出力
    print("\n【簡易マトリックス】")
    header = "          " + "".join([f"{f[:8]:>10}" for f in valid_files])
    print(header)
    for i, row in enumerate(matrix):
        row_str = f"{valid_files[i][:8]:<10}" + "".join([f"{val:10.3f}" for val in row])
        print(row_str)

if __name__ == "__main__":
    main()
