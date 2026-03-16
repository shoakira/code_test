import os
import io
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import base64
import google.generativeai as genai
from dotenv import load_dotenv
import matplotlib.pyplot as plt
import seaborn as sns

# .env ファイルがあれば読み込む
load_dotenv()

# APIキーとモデルの設定
api_key = os.getenv("GOOGLE_API_KEY")
if not api_key:
    print("⚠️ 警告: GOOGLE_API_KEYが設定されていません。")
    exit(1)

genai.configure(api_key=api_key)
model_name = "models/gemini-embedding-2-preview"

def compute_cosine_similarity(vec1, vec2):
    v1 = np.array(vec1)
    v2 = np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))

def compute_cosine_distance(vec1, vec2):
    """コサイン距離 (1 - 類似度) を計算します。"""
    return 1.0 - compute_cosine_similarity(vec1, vec2)

def get_embedding(content):
    if isinstance(content, Image.Image):
        # 画像をBytesに変換してBase64エンコード
        buffered = io.BytesIO()
        content.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")
        # genaiのembed_contentに渡せるフォーマットに変換
        content = {"mime_type": "image/jpeg", "data": img_str}
        
    result = genai.embed_content(
        model=model_name,
        content=content
    )
    return np.array(result['embedding'])

def analyze_pdf_distances(pdf_path, target_image_path=None, target_text=None):
    """
    PDF内の全てのページのエンベディングを取得し、
    ターゲットとの距離およびページ間の距離マトリックスを計算・表示します。
    """
    if not target_image_path and not target_text:
        print("検索対象の画像パスまたはテキストの少なくとも一方を指定してください。")
        return

    # --- 1. PDFの読み込みとエンベディング取得 ---
    print(f"--- PDF '{pdf_path}' の解析開始 ---")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"❌ PDFが開けません: {e}")
        return

    all_items = [] # {"emb": embedding, "label": label}
    
    # PDF各ページのエンベディング
    for page_num in range(len(doc)):
        print(f"\r📄 ページ {page_num + 1} / {len(doc)} を解析中...", end="")
        page = doc[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
        img_data = pix.tobytes("png")
        page_img = Image.open(io.BytesIO(img_data)).convert("RGB")
        
        emb = get_embedding(page_img)
        all_items.append({"emb": emb, "label": f"Page {page_num + 1}"})
    print("\n✅ PDF全ページのエンベディング取得完了")

    # --- 2. ターゲットのエンベディング取得 ---
    print("\n--- 検索ターゲットのエンベディング取得 ---")
    if target_image_path:
        if os.path.exists(target_image_path):
            print(f"ターゲット画像 '{target_image_path}' を読み込んでいます...")
            target_img = Image.open(target_image_path).convert("RGB")
            emb = get_embedding(target_img)
            all_items.append({"emb": emb, "label": "Target (Img)"})
            print("✅ 画像ターゲット完了")
        else:
            print(f"⚠️ 警告: ターゲット画像 '{target_image_path}' が見つかりません。")

    if target_text:
        print(f"ターゲットテキスト '{target_text}' を処理しています...")
        emb = get_embedding(target_text)
        all_items.append({"emb": emb, "label": "Target (Txt)"})
        print("✅ テキストターゲット完了")

    # --- 3. マトリックス計算 (全要素間のコサイン距離) ---
    num_elements = len(all_items)
    dist_matrix = np.zeros((num_elements, num_elements))
    labels = [item["label"] for item in all_items]
    
    for i in range(num_elements):
        for j in range(num_elements):
            dist_matrix[i, j] = compute_cosine_distance(all_items[i]["emb"], all_items[j]["emb"])

    # --- 4. 結果の可視化とレポート ---
    print("\n--- 類似度解析レポート ---")
    
    # ヒートマップ作成
    plt.figure(figsize=(12, 10))
    sns.heatmap(dist_matrix, annot=(num_elements <= 15), fmt=".3f", cmap="viridis_r",
                xticklabels=labels, yticklabels=labels)
    plt.title(f"Cosine Distance Matrix (PDF Pages & Targets)")
    plt.tight_layout()
    
    output_img = "pdf_distance_matrix.png"
    plt.savefig(output_img)
    print(f"🎉 距離マトリックス図を '{output_img}' に保存しました。")

    # ターゲットが存在する場合、それとの距離を全ページ分表示
    target_indices = [i for i, l in enumerate(labels) if "Target" in l]
    for t_idx in target_indices:
        print(f"\n【{labels[t_idx]} と各ページのコサイン距離】")
        page_dists = []
        for i in range(len(doc)):
            page_dists.append((i + 1, dist_matrix[t_idx, i]))
        
        # 距離が近い順 (昇順) にソート
        page_dists.sort(key=lambda x: x[1])
        
        for rank, (p_num, d) in enumerate(page_dists):
            print(f"{rank + 1}位: ページ {p_num:2d} (距離: {d:.4f})")

    doc.close()

if __name__ == "__main__":
    PDF_FILE = "sample.pdf"                 # 検索対象のPDF
    LOGO_IMAGE = "logo.png"                 # 検索したいロゴ画像
    SEARCH_TEXT = None                      # 必要に応じてテキストを指定
    
    analyze_pdf_distances(
        pdf_path=PDF_FILE,
        target_image_path=LOGO_IMAGE, 
        target_text=SEARCH_TEXT
    )
