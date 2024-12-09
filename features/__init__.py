import requests
import re

from config import OPENAI_API_KEY

BASE_URL = "https://api.pawan.krd/v1/chat/completions"


def get_response(messages):
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "pai-001",
        "messages": messages,
        "temperature": 0.7,
        "max_tokens": 8192
    }
    response = requests.post(BASE_URL, json=payload, headers=headers)
    if response.status_code == 200:
        answer = response.json()["choices"][0]["message"]["content"]
    else:
        answer = f"Ошибка: {response.status_code} - {response.text}"
    return clean_text(answer)


def clean_text(text):
    """Фильтрация текста от нежелательных символов."""
    return re.sub(r"[^\s.,?!:;()\[\]{}'\"-—а-яА-ЯёЁ]", "", text)


from features.problem_solving import solve_problem
from features.test_generation import generate_test
