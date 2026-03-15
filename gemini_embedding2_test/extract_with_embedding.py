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

def extract_pages_with_gemini(pdf_path, output_path, target_image_path=None, target_text=None, threshold=0.4):
    """
    Gemini Embedding 2 を使用して、PDF内の各ページとターゲット（画像またはテキスト）
    の類似度を計算し、類似度が高いページを抽出します。
    """
    if not target_image_path and not target_text:
        print("検索対象の画像パスまたはテキストの少なくとも一方を指定してください。")
        return

    print("--- 検索クエリのエンベディング取得 ---")
    query_embeddings = {}
    
    # 1. 画像クエリのベクトル化
    if target_image_path and os.path.exists(target_image_path):
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

    extracted_doc = fitz.open()
    found_pages = []

    for page_num in range(len(doc)):
        print(f"\n📄 ページ {page_num + 1} / {len(doc)} を解析中...")
        page = doc[page_num]
        
        # ページを画像（PIL.Image）として取得
        pix = page.get_pixmap(matrix=fitz.Matrix(2.0, 2.0), alpha=False)
        img_data = pix.tobytes("png")
        page_img = Image.open(io.BytesIO(img_data)).convert("RGB")
        
        # ページのエンベディングを取得
        page_embedding = get_embedding(page_img)
        
        # クエリとの類似度を計算
        is_target_page = False
        
        if 'image' in query_embeddings:
            sim_img = compute_cosine_similarity(page_embedding, query_embeddings['image'])
            print(f"  [画像比較] ロゴ画像との類似度: {sim_img:.4f}")
            if sim_img >= threshold:
                is_target_page = True
                print("    -> 画像類似度により抽出条件をクリア！")
                
        if 'text' in query_embeddings:
            sim_text = compute_cosine_similarity(page_embedding, query_embeddings['text'])
            print(f"  [テキスト比較] 検索テキストとの類似度: {sim_text:.4f}")
            if sim_text >= threshold:
                is_target_page = True
                print("    -> テキスト類似度により抽出条件をクリア！")

        # 抽出対象であれば記録する
        if is_target_page:
            found_pages.append(page_num)
            extracted_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)

    # 抽出結果の保存
    if found_pages:
        extracted_doc.save(output_path)
        print(f"\n🎉 抽出完了！ 対象の {len(found_pages)} ページを '{output_path}' に保存しました。")
    else:
        print("\n⚠️ 類似度がしきい値を超えるページは見つかりませんでした。")
        
    doc.close()
    extracted_doc.close()

if __name__ == "__main__":
    PDF_FILE = "sample.pdf"                 # 検索対象のPDF
    OUTPUT_FILE = "extracted_pages.pdf"     # 抽出結果のPDF
    LOGO_IMAGE = "logo.png"                 # 探したいロゴ画像 (ない場合は None を指定)
    SEARCH_TEXT = "会社のロゴが入っているページ"  # 探したいテキスト (ない場合は None を指定)
    
    # 類似度のしきい値
    # Gemini Embeddingは一般的に値が高めに出るため、
    # 実際のログを見ながら 0.35 〜 0.45 あたりで調整してください。
    THRESHOLD = 0.40  

    extract_pages_with_gemini(
        pdf_path=PDF_FILE,
        output_path=OUTPUT_FILE,
        target_image_path=LOGO_IMAGE, 
        target_text=SEARCH_TEXT,
        threshold=THRESHOLD
    )
