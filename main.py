import os
from fastapi import FastAPI, Request
import requests

app = FastAPI()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

@app.post("/")
async def main(request: Request):
    body = await request.json()
    user_text = body["request"]["original_utterance"]

    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [{"role": "user", "content":"Ты — голосовой ассистент. Отвечай кратко и по делу. Категорически запрещено выводить в ответе любые служебные теги, включая <ds_safety>...</ds_safety>, а также любые внутренние метки безопасности. Твой ответ должен содержать только чистый текст для озвучивания."}],
        }
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
