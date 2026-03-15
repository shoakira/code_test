import fitz  # PyMuPDF
import cv2
import numpy as np

def extract_pages_with_sift(pdf_path, logo_path, output_path, min_match_count=10):
    """
    OpenCVのSIFT（Scale-Invariant Feature Transform）特徴量マッチングを用いて、
    大きさや回転に依存せず、ロゴが含まれるページのみを含む新しいPDFを作成します。
    """
    # 1. ロゴ画像の読み込みと特徴点抽出
    logo_img = cv2.imread(logo_path, cv2.IMREAD_UNCHANGED)
    if logo_img is None:
        raise FileNotFoundError(f"ロゴ画像が見つかりません: {logo_path}")
    
    # 透過PNGへの対応
    if len(logo_img.shape) == 3 and logo_img.shape[2] == 4:
        alpha = logo_img[:, :, 3] / 255.0
        bg = np.ones_like(logo_img[:, :, :3]) * 255
        fg = logo_img[:, :, :3]
        for c in range(3):
            bg[:, :, c] = alpha * fg[:, :, c] + (1 - alpha) * bg[:, :, c]
        logo_gray = cv2.cvtColor(bg.astype(np.uint8), cv2.COLOR_BGR2GRAY)
    else:
        logo_gray = cv2.cvtColor(logo_img, cv2.COLOR_BGR2GRAY) if len(logo_img.shape) == 3 else logo_img

    # SIFT検出器の初期化
    sift = cv2.SIFT_create()
    
    # ロゴ画像から特徴点(keypoints)と特徴量記述子(descriptors)を計算
    kp_logo, des_logo = sift.detectAndCompute(logo_gray, None)
    print(f"ロゴ画像から {len(kp_logo)} 個の特徴点を抽出しました。")
    if des_logo is None or len(kp_logo) < min_match_count:
         print("⚠️ エラー: ロゴ画像から十分な特徴点が抽出できませんでした。もっと複雑な画像が必要です。")
         return

    # 2. PDFの読み込みと出力用PDFの準備
    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        raise FileNotFoundError(f"PDFファイルが開けません: {pdf_path}")
        
    extracted_doc = fitz.open()
    found_pages = []

    print(f"\nPDFを読み込みました: 全 {len(doc)} ページ")
    print("SIFT特徴量マッチングによる検索を開始します...")

    # 高速な近似近傍探索（FLANN）のパラメータ設定
    FLANN_INDEX_KDTREE = 1
    index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=5)
    search_params = dict(checks=50) # 精度と速度のトレードオフ
    flann = cv2.FlannBasedMatcher(index_params, search_params)

    for page_num in range(len(doc)):
        page = doc[page_num]
        
        # ページを画像としてレンダリング (zoom=2.0で高解像度化)
        zoom = 2.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_array = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        page_gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        # ページ画像から特徴点と記述子を計算
        kp_page, des_page = sift.detectAndCompute(page_gray, None)
        
        if des_page is None or len(kp_page) == 0:
            print(f"❌ ページ {page_num + 1} はスキップ (特徴点なし)")
            continue

        # 特徴量マッチング（FLANN）
        matches = flann.knnMatch(des_logo, des_page, k=2)

        # Lowe's ratio test (誤認識を強力に弾くためのテスト)
        good_matches = []
        for match in matches:
            if len(match) == 2:
                m, n = match
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
        
        # 良いマッチが閾値以上見つかった場合、さらに幾何学的チェック(Homography)を行う
        if len(good_matches) > min_match_count:
            # 良いマッチング点から座標を取得
            src_pts = np.float32([kp_logo[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            dst_pts = np.float32([kp_page[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)
            
            # ホモグラフィ行列（平面射影変換）の推定（RANSACで外れ値を除外）
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            
            if M is not None:
                # 正常な変換行列が求まった場合は、形状として見つかったと判定
                matchesMask = mask.ravel().tolist()
                inlier_count = sum(matchesMask)
                
                # インライア（外れ値を除外した正しい対応点）の数で最終判定
                if inlier_count >= min_match_count:
                    print(f"✅ ページ {page_num + 1} にロゴを発見 (良いマッチ数: {len(good_matches)}, 形状一致点: {inlier_count})")
                    found_pages.append(page_num)
                    extracted_doc.insert_pdf(doc, from_page=page_num, to_page=page_num)
                    continue
                else:
                    print(f"❌ ページ {page_num + 1} はスキップ (形状チェック不合格: {inlier_count})")
            else:
                print(f"❌ ページ {page_num + 1} はスキップ (図形の変形が計算不可)")
        else:
            print(f"❌ ページ {page_num + 1} はスキップ (良いマッチ数: {len(good_matches)})")

    # 3. 抽出結果の保存
    if found_pages:
        extracted_doc.save(output_path)
        print(f"\n🎉 抽出完了！ 対象の {len(found_pages)} ページを '{output_path}' に保存しました。")
    else:
        print("\n⚠️ ロゴが含まれるページは見つかりませんでした。")
        
    doc.close()
    extracted_doc.close()

if __name__ == "__main__":
    PDF_FILE = "sample.pdf"                 # 対象のPDFファイル
    LOGO_FILE = "logo.png"                  # 対象のロゴ画像
    OUTPUT_FILE = "extracted_pages.pdf"     # 保存PDFファイル名
    
    # 画像内の特徴点が何個以上(相似な配置で)一致したら「ロゴあり」とするかの閾値
    # アイコンのようにシンプルなものは少なめ(10)、複雑な写真は多め(30など)にします
    MIN_MATCH_COUNT = 10 
    
    try:
        extract_pages_with_sift(PDF_FILE, LOGO_FILE, OUTPUT_FILE, MIN_MATCH_COUNT)
    except Exception as e:
        print(f"プログラム実行中にエラーが発生しました: {e}")
