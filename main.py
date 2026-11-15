import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.deepseek.com/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]

    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
         json={
            "model": "deepseek-flash",
            "thinking": {"type": "enabled"},
            "tools": [
                {"type": "deepseek_web_search", "name": "deepseek_web_search"}
            ],
            "messages": [
                {
                    "role": "system",
                    "content": "Ты — голосовой ассистент. Твой ответ должен быть на русском языке. Отвечай кратко и по делу. Если ты используешь информацию из интернета, не зачитывай ссылки и источники, просто дай ответ. Твой ответ должен содержать только чистый текст для озвучивания."
                },
                {
                    "role": "user",
                    "content": user_text
                }
            ],
            "stream": False
        },
    )
    answer = response.json()["choices"][0]["message"]["content"]

    return {
        "version": body["version"],
        "session": body["session"],
        "response": {
            "end_session": False,
            "text": answer
        }
    }
