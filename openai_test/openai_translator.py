import os
import openai
from dotenv import load_dotenv
load_dotenv()


# 環境変数からAPIキーを読み込む
openai.api_key = os.environ.get("OPENAI_API_KEY")
# APIキーが設定されていない場合は警告
if not openai.api_key:
    raise ValueError("環境変数 OPENAI_API_KEY が設定されていません")


def translate_japanese_to_french(text):
    """日本語をフランス語に翻訳する"""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "あなたは優秀な翻訳アシスタントです。"},
                {"role": "user", "content": f"次の日本語をフランス語に翻訳してください: {text}"}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        return None


# 翻訳する日本語のテキスト
japanese_text = "来週には中学受験の最初のテストがあり、東京に行きます。"

# フランス語に翻訳
french_text = translate_japanese_to_french(japanese_text)

# 結果を表示
if french_text:
    print(f"日本語: {japanese_text}")
    print(f"フランス語: {french_text}")
