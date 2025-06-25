import PyPDF2
import openai
import os  # 環境変数を読み込むためにosモジュールを追加
from dotenv import load_dotenv
load_dotenv()


def extract_text_from_pdf(pdf_path):
    # PDFファイルを開く
    with open(pdf_path, 'rb') as file:
        # PDFリーダーオブジェクトを作成
        reader = PyPDF2.PdfReader(file)
        # 全ページのテキストを格納するリスト
        text = []
        # 各ページのテキストを抽出
        for page in reader.pages:
            text.append(page.extract_text())
        # テキストを結合して返す
        formatted_text = '\\n'.join(text).strip()
        return formatted_text

def summarize_with_gpt4(text):
    # 環境変数からAPIキーを読み込む
    openai.api_key = os.environ.get("OPENAI_API_KEY")
    
    # APIキーが設定されていない場合は警告
    if not openai.api_key:
        raise ValueError("環境変数 OPENAI_API_KEY が設定されていません")

    # テキストの長さを制限
    max_length = 2000  # 必要に応じてさらに調整
    if len(text) > max_length:
        text = text[:max_length]

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"次のテキストを日本語で要約してください: {text}"}],
        max_tokens=2000,
        temperature=0.5
    )

    summary = response.choices[0].message["content"].strip()
    return summary

# PDFテキスト抽出と要約の使用例
if __name__ == "__main__":
    pdf_path = "2412.06769v2.pdf"  # PDFファイルのパスを指定
    extracted_text = extract_text_from_pdf(pdf_path)
    #print("Extracted and Formatted Text:")
    #print(extracted_text)

    # GPT-4を使用して要約
    summary = summarize_with_gpt4(extracted_text)
    print("Summary:")
    print(summary)
