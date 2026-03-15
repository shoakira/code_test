import os
import io
import time
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

def get_image_embedding(image_path):
    """
    画像からエンベディングを取得します。
    """
    try:
        img = Image.open(image_path).convert("RGB")
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
        print(f"❌ 画像 '{image_path}' の取得エラー: {e}")
        return None

def get_video_embedding_fallback(video_path):
    """
    OpenCVを使用して動画の中央フレームを抽出し、そのエンベディングを取得します。
    """
    import cv2
    print(f"🔄 フォールバック: {video_path} からフレームを抽出中...")
    cap = cv2.VideoCapture(video_path)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_count // 2) # 中央のフレーム
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        print(f"❌ フレームの抽出に失敗しました: {video_path}")
        return None
        
    # BGRからRGBへ変換
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(frame_rgb)
    
    # 画像としてエンベディング取得
    buffered = io.BytesIO()
    img.save(buffered, format="JPEG")
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
    content = {"mime_type": "image/jpeg", "data": img_str}
    
    result = genai.embed_content(
        model=model_name,
        content=content
    )
    return np.array(result['embedding'])

def get_video_embedding(video_path):
    """
    動画をアップロードし、ACTIVEになるのを待ってからエンベディングを取得します。
    失敗した場合はフレーム抽出フォールバックを試みます。
    """
    try:
        print(f"🎥 動画をアップロード中: {video_path}...")
        video_file = genai.upload_file(path=video_path)
        
        # ACTIVEになるまでループで確認
        max_retries = 30
        for _ in range(max_retries):
            if video_file.state.name == "ACTIVE":
                break
            if video_file.state.name == "FAILED":
                break
            print(".", end="", flush=True)
            time.sleep(2)
            video_file = genai.get_file(video_file.name)
            
        if video_file.state.name == "ACTIVE":
            print(f" ✅ ACTIVE")
            result = genai.embed_content(
                model=model_name,
                content=video_file
            )
            return np.array(result['embedding'])
        else:
            print(f" ⚠️ API直接処理が失敗またはタイムアウトしました (State: {video_file.state.name})")
            return get_video_embedding_fallback(video_path)
            
    except Exception as e:
        print(f" ⚠️ APIエラー: {e}")
        return get_video_embedding_fallback(video_path)

def main():
    # 比較対象のリスト
    video_files = ["cat_park.mp4", "dog_house.mov", "dog_park.mov"]
    image_files = ["image1.png", "image2.png"]
    
    all_items = []
    
    # 動画の処理
    print("--- 動画のエンベディング取得開始 ---")
    for f in video_files:
        if os.path.exists(f):
            emb = get_video_embedding(f)
            if emb is not None:
                all_items.append({"label": f"Video: {f}", "emb": emb})
        else:
            print(f"⚠️ ファイルが見つかりません: {f}")

    # 画像の処理
    print("\n--- 画像のエンベディング取得開始 ---")
    for f in image_files:
        if os.path.exists(f):
            emb = get_image_embedding(f)
            if emb is not None:
                all_items.append({"label": f"Image: {f}", "emb": emb})
            print(f"✅ Image: {f} 完了")
        else:
            print(f"⚠️ ファイルが見つかりません: {f}")

    if len(all_items) < 2:
        print("比較には少なくとも2つ以上の要素が必要です。")
        return

    # 類似度マトリックスの計算
    num_items = len(all_items)
    matrix = np.zeros((num_items, num_items))
    labels = [item["label"] for item in all_items]
    embeddings = [item["emb"] for item in all_items]
    
    for i in range(num_items):
        for j in range(num_items):
            dot = np.dot(embeddings[i], embeddings[j])
            norm_i = np.linalg.norm(embeddings[i])
            norm_j = np.linalg.norm(embeddings[j])
            matrix[i, j] = dot / (norm_i * norm_j)

    print("\n--- 類似度マトリックスを作成中 ---")
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(matrix, annot=True, fmt=".3f", cmap="coolwarm",
                xticklabels=labels, yticklabels=labels)
    plt.title("Video & Image Similarity Matrix (Gemini Embedding 2)")
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    output_img = "video_image_similarity_matrix.png"
    plt.savefig(output_img)
    print(f"🎉 マトリックス図を '{output_img}' に保存しました。")
    
    # 簡易表示
    print("\n【類似度ランキング (上位10ペア)】")
    pairs = []
    for i in range(num_items):
        for j in range(i + 1, num_items):
            pairs.append(((labels[i], labels[j]), matrix[i, j]))
    
    pairs.sort(key=lambda x: x[1], reverse=True)
    for p, score in pairs[:10]:
        print(f"{score:.4f}: {p[0]} <---> {p[1]}")

if __name__ == "__main__":
    main()
