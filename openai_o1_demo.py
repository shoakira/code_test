from openai import OpenAI
client = OpenAI()

prompt = """
Please explain in detail the relationship between the Pollicotte-Ruelle resonance and the analytic connection, and the complex spectrum.
Please explain in Japanese.
"""

response = client.chat.completions.create(
    model="o1-preview",
    messages=[
        {
            "role": "user", 
            "content": prompt
        }
    ]
)

print(response.choices[0].message.content)