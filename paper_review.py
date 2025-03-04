import PyPDF2
import openai
import os

# PDFファイルからテキストを抽出する関数
def extract_text_from_pdf(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        text = ''
        for page_num in range(len(reader.pages)):
            page = reader.pages[page_num]
            page_text = page.extract_text()
            if page_text:  # テキストが存在する場合のみ追加
                text += page_text + "\n"
    return text

# OpenAI APIを使用してテキストのサマリーを生成する関数
def summarize_text(text, api_key):
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-4o",  # 正しいモデル名を使用
        messages=[
            {"role": "system", "content": "以下の論文のテキストの要約を読みやすく構造化し、日本語で書いてください。"},
            {"role": "user", "content": text}
        ],
        max_tokens=5500,
        temperature=0.5,
    )
    summary = response.choices[0].message['content'].strip()
    return summary


# メイン関数
def main():
    pdf_path = '2412.06769v2.pdf'  # PDFファイルのパスを指定
    api_key = os.getenv('OPENAI_API_KEY')  # 環境変数からAPIキーを取得

    if not api_key:
        raise ValueError("APIキーが設定されていません。環境変数 'OPENAI_API_KEY' を設定してください。")

    # PDFからテキストを抽出
    text = extract_text_from_pdf(pdf_path)

    if not text:
        print("PDFからテキストを抽出できませんでした。")
        return

    # テキストのサマリーを生成
    summary = summarize_text(text, api_key)

    # サマリーを表示
    print("サマリー:")
    print(summary)

if __name__ == "__main__":
    main()
