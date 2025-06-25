import json
from openai import OpenAI

client = OpenAI()

def generate_question():
    """
    OpenAIのAPIを使用して、科学に関する選択肢問題をJSON形式で生成する。
    """
    try:
        # OpenAI APIにリクエストを送信
        completion = client.chat.completions.create(
            # 使用するモデルを指定
            model="gpt-4o-mini",  # "gpt-4o-mini"はモデル名

            # ChatGPTへのメッセージリストを定義
            messages=[
                {"role": "system", "content": "You are a wise quiz generator."},  # システムの役割を指定
                {
                    # ユーザーが与えるプロンプト
                    "role": "user",
                    "content": "Create a multiple-choice question about Tokyo with four options in Japanese. \
                        Respond in the following JSON format: \
                        { \
                            'question': '問題文', \
                            'options': {'(1)': '選択肢1', '(2)': '選択肢2', '(3)': '選択肢3', '(4)': '選択肢4'}, \
                            'answer': '正しい選択肢' \
                        }"
                }
            ],

            # 応答フォーマットを定義
            response_format={
                # 出力形式のタイプを指定
                "type": "json_schema",  # JSONスキーマとして応答を受け取る
                "json_schema": {
                    # スキーマの名前を定義
                    "name": "quiz_format",  # スキーマに名前をつけることで他と区別可能

                    # スキーマの詳細な構造を指定
                    "schema": {
                        "type": "object",  # 応答はオブジェクト形式
                        "properties": {  # オブジェクト内のプロパティを定義
                            "question": {"type": "string"},  # 'question'は文字列型
                            "options": {  # 'options'は辞書型（オブジェクト）
                                "type": "object",
                                "properties": {  # 'options'内のプロパティを定義
                                    "(1)": {"type": "string"},  # 各選択肢は文字列型
                                    "(2)": {"type": "string"},
                                    "(3)": {"type": "string"},
                                    "(4)": {"type": "string"}
                                },
                                "required": ["(1)", "(2)", "(3)", "(4)"],  # 全ての選択肢が必須
                                "additionalProperties": False  # 未定義のプロパティを禁止
                            },
                            "answer": {"type": "string"}  # 'answer'は文字列型
                        },
                        "required": ["question", "options", "answer"],  # 'question', 'options', 'answer'は必須
                        "additionalProperties": False  # 未定義のプロパティを禁止
                    },
                    # 応答がスキーマに完全準拠していることを要求
                    "strict": True
                }
            },

            # 応答トークンの最大数を指定
            max_tokens=300,

            # 応答の多様性を指定（1.0で最大ランダム性）
            temperature=1.0,
        )
        
        # 応答を取得し、JSON形式で返す
        return completion.choices[0].message.content
    except Exception as e:
        # エラーハンドリング
        print(f"Error generating question: {e}")
        return None

def quiz_game():
    """
    クイズゲームを実行する。
    """
    score = 0
    num_questions = 3  # 出題する問題の数

    for i in range(1, num_questions + 1):
        print(f"\n問題 {i}:")
        
        # 問題を生成
        question_data = generate_question()
        parsed_data = json.loads(question_data)

        # 問題と選択肢を表示
        print(parsed_data["question"])
        for key, value in parsed_data['options'].items():
            # キーの数字部分を取り出してフォーマット
            number = key.strip("()")
            print(f"{number}. {value}")

        # ユーザーの回答を取得
        try:
            answer = int(input("答えを選んでください（番号を入力）："))
            c_ans = int(parsed_data["answer"].strip("()"))
            #print(parsed_data['options'])
            if answer == c_ans:
                print("正解です！\n")
                score += 1
            else:
                if 0 < c_ans <= len(parsed_data["options"]):
                    correct_option = list(parsed_data["options"].items())[c_ans-1][1]
                    print(f"不正解です。正解は {c_ans}. {correct_option} です。\n")
                else:
                    print(f"不正解です。正解は {c_ans} 番目です。\n")
        except ValueError:
            print("無効な入力です。番号を入力してください。\n")

    print(f"あなたのスコアは {score}/{num_questions} です。")


# 実行例
if __name__ == "__main__":
    quiz_game()

