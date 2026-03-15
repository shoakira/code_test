import os
import io
import fitz  # PyMuPDF
from PIL import Image
import numpy as np
import base64
import google.generativeai as genai
from dotenv import load_dotenv

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
    return result['embedding']

def extract_pages_with_gemini(pdf_path, output_path, target_image_path=None, target_text=None, top_k=1):
    """
    Gemini Embedding 2 を使用して、PDF内の各ページとターゲット（画像またはテキスト）
    の類似度を計算し、類似度が最も高い上位ページを抽出します。
    """
    if not target_image_path and not target_text:
        print("検索対象の画像パスまたはテキストの少なくとも一方を指定してください。")
        return

    print("--- 検索クエリのエンベディング取得 ---")
    query_embeddings = {}
    
    # 1. 画像クエリのベクトル化
    if target_image_path:
        if not os.path.exists(target_image_path):
            print(f"❌ エラー: ターゲット画像 '{target_image_path}' が見つかりません。")
            print("画像をプログラムと同じフォルダに保存してください！")
            return
        print(f"ターゲット画像 '{target_image_path}' を読み込んでいます...")
        target_img = Image.open(target_image_path).convert("RGB")
        query_embeddings['image'] = get_embedding(target_img)
        print("✅ 画像クエリのエンベディング取得完了")
        
    # 2. テキストクエリのベクトル化
    if target_text:
        print(f"ターゲットテキスト '{target_text}' を処理しています...")
        query_embeddings['text'] = get_embedding(target_text)
        print("✅ テキストクエリのエンベディング取得完了")

    print("\n--- PDFの解析開始 ---")
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        print(f"PDFが開けません: {e}")
        return

    page_scores = []

    for page_num in range(len(doc)):
        print(f"\r📄 ページ {page_num + 1} / {len(doc)} を解析中...", end="")
        page = doc[page_num]
        
        # ページを画像（PIL.Image）として取得
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
        img_data = pix.tobytes("png")
        page_img = Image.open(io.BytesIO(img_data)).convert("RGB")
        
        # ページのエンベディングを取得
        page_embedding = get_embedding(page_img)
        
        # クエリとの類似度を計算し、最も高いスコアを記録
        best_score = -1.0
        
        if 'image' in query_embeddings:
            sim_img = compute_cosine_similarity(page_embedding, query_embeddings['image'])
            best_score = max(best_score, sim_img)
                
        if 'text' in query_embeddings:
            sim_text = compute_cosine_similarity(page_embedding, query_embeddings['text'])
            best_score = max(best_score, sim_text)

        page_scores.append((page_num, best_score))

    print("\n\n--- 類似度ランキング ---")
    # スコアが高い順に並び替え
    page_scores.sort(key=lambda x: x[1], reverse=True)
    
    extracted_doc = fitz.open()
    found_pages = []
    
    # 上位K件を抽出
    for rank in range(min(top_k, len(page_scores))):
        page_num, score = page_scores[rank]
        print(f"{rank + 1}位: ページ {page_num + 1} (スコア: {score:.4f})")
        found_pages.append(page_num)
        
        # PyMuPDFでは抽出元のページ番号をそのまま指定して挿入します
        extracted_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

    # 抽出結果の保存
    if found_pages:
        extracted_doc.save(output_path)
        print(f"\n🎉 抽出完了！ 上位 {len(found_pages)} ページを '{output_path}' に保存しました。")
        
    doc.close()
    extracted_doc.close()

if __name__ == "__main__":
    PDF_FILE = "sample.pdf"                 # 検索対象のPDF
    OUTPUT_FILE = "extracted_pages.pdf"     # 抽出結果のPDF
    # 検索したいロゴ画像があればファイル名を指定。ない場合は None
    LOGO_IMAGE = "logo.png"                 
    SEARCH_TEXT = None # 画像のみで検索するため、テキストはNoneにする
    
    # 上位何ページを抽出するか
    TOP_K = 1

    extract_pages_with_gemini(
        pdf_path=PDF_FILE,
        output_path=OUTPUT_FILE,
        target_image_path=LOGO_IMAGE, 
        target_text=SEARCH_TEXT,
        top_k=TOP_K
    )
