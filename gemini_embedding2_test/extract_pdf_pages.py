import fitz  # PyMuPDF
import cv2
import numpy as np

def extract_pages_with_logo(pdf_path, logo_path, output_path, match_threshold=0.75):
    """
    PDF内のすべてのページを画像化し、ロゴ画像とテンプレートマッチングを行うことで
    ロゴが含まれるページのみを含む新しいPDFを作成します。
    """
    # 1. ロゴ画像の読み込み
    # cv2.IMREAD_UNCHANGEDで読み込み、透過(アルファ)チャンネルがあれば白背景に変換します
    logo_img = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    if logo_img is None:
        raise FileNotFoundError(f"ロゴ画像が見つかりません。ファイル名を確認してください: {logo_path}")
    
    # 透過PNGへの対応
    if len(logo_img.shape) == 3 and logo_img.shape[2] == 4:
        # アルファチャンネルを使って背景を白にする
        alpha = logo_img[:, :, 3] / 255.0
        bg = np.ones_like(logo_img[:, :, :3]) * 255
        fg = logo_img[:, :, :3]
        for c in range(3):
            bg[:, :, c] = alpha * fg[:, :, c] + (1 - alpha) * bg[:, :, c]
        logo_gray = cv2.cvtColor(bg.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    else:
        logo_gray = cv2.cvtColor(logo_img, cv2.COLOR_BGR2GRAY) if len(logo_img.shape) == 3 else logo_img

    # 2. PDFの読み込みと出力用PDFの準備
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise FileNotFoundError(f"PDFファイルが開けません: {pdf_path}")
        
    extracted_doc = fitz.open()
    found_pages = []

    print(f"PDFを読み込みました: 全 {len(doc)} ページ")
    print("ロゴの検索を開始します...")

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # ページを画像としてレンダリング (zoom=2.0で高解像度化)
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        
        # PyMuPDFのPixmapをNumPy配列（OpenCV形式）に変換
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        
        # RGBからグレースケールに変換
        page_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        found_in_page = False
        best_overall_score = -1.0
        best_overall_scale = 1.0
        
        # マルチスケールマッチング
        # サイズの違いに非常に敏感なため、より細かく60段階で探すように変更します。
        scales = np.linspace(0.1, 2.5, 60)[::-1]
        
        for scale in scales:
            # OpenCVはピクセルサイズが整数である必要があるため、1未満の縮小でエラーにならないよう制御
            new_width = int(logo_gray.shape[1] * scale)
            new_height = int(logo_gray.shape[0] * scale)
            if new_width == 0 or new_height == 0:
                continue

            resized_logo = cv2.resize(logo_gray, (new_width, new_height))
            
            # ページ画像よりロゴが大きくなってしまった場合はスキップ
            if page_gray.shape[0] < resized_logo.shape[0] or page_gray.shape[1] < resized_logo.shape[1]:
                continue
                
            # テンプレートマッチング
            result = cv2.matchTemplate(page_gray, resized_logo, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, _ = cv2.minMaxLoc(result)
            
            if max_val > best_overall_score:
                best_overall_score = max_val
                best_overall_scale = scale
            
            # 類似度がしきい値を超えたら「ロゴあり」と判定
            if max_val >= match_threshold:
                print(f"✅ ページ {page_num + 1} にロゴを発見 (スコア: {max_val:.2f}, 縮尺: {scale:.2f})")
                found_pages.append(page_num)
                extracted_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                found_in_page = True
                break
        
        if not found_in_page:
            print(f"❌ ページ {page_num + 1} はスキップ (最大スコア: {best_overall_score:.2f}, 縮尺: {best_overall_scale:.2f})")

    # 3. 抽出結果の保存
    if found_pages:
        extracted_doc.save(output_path)
        print(f"\n🎉 抽出完了！ 対象の {len(found_pages)} ページを '{output_path}' に保存しました。")
    else:
        print("\n⚠️ ロゴが含まれるページは見つかりませんでした。")
        
    doc.close()
    extracted_doc.close()

if __name__ == "__main__":
    # 対象ファイルの設定
    PDF_FILE = "sample.pdf"                # 解析したいPDFファイル
    LOGO_FILE = "logo.png"                 # 添付いただいたロゴ画像（ファイル名に合わせて変更してください）
    OUTPUT_FILE = "extracted_pages.pdf"    # 抽出後の保存PDFファイル名
    
    # マッチングのしきい値 (0.0 〜 1.0)
    # うまく見つからない場合は少し下げ(例: 0.6)、誤検知が多い場合は上げて(例: 0.85)ください
    MATCH_THRESHOLD = 0.75
    
    try:
        extract_pages_with_logo(PDF_FILE, LOGO_FILE, OUTPUT_FILE, MATCH_THRESHOLD)
    except Exception as e:
        print(f"プログラム実行中にエラーが発生しました: {e}")
