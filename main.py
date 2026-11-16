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

    search_response = requests.post(
        "https://api.deepseek.com/v1/tools/search",
        headers={
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "query": user_text,
            "count": 3,
            "need_content": True
        }
    )

    # Если поиск не удался, просто отвечаем без него
    search_context = "Информация из интернета не найдена."
    if search_response.status_code == 200:
        search_data = search_response.json()
        found_texts = []
        for result in search_data.get("results", []):
            title = result.get("title", "Без заголовка")
            content = result.get("content", result.get("summary", ""))
            found_texts.append(f"Заголовок: {title}\nТекст: {content}")
        
        if found_texts:
            search_context = "\n\n".join(found_texts)

    # 2. Теперь просим модель DeepSeek ответить, используя найденную информацию
    response = requests.post(
        DEEPSEEK_API_URL,
        headers={"Authorization": f"Bearer {DEEPSEEK_API_KEY}"},
        json={
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "Ты — голосовой ассистент. Твой ответ должен быть на русском языке. Отвечай кратко и по делу. Категорически запрещено выводить в ответе любые служебные теги. Твой ответ должен содержать только чистый текст для озвучивания. Используй предоставленную информацию из интернета, чтобы ответить на вопрос пользователя."
                },
                {
                    "role": "user",
                    "content": f"Вопрос пользователя: {user_text}\n\nИнформация из интернета для ответа:\n{search_context}"
                }
            ]
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
