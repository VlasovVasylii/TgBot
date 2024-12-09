from features import get_response


def generate_test(topic, num_questions=5):
    """Генерация учебного теста с помощью OpenAI API."""
    prompt = (f"Создай тест на тему '{topic}' с {num_questions} вопросами. "
              "Каждый вопрос должен иметь 4 варианта ответа, один из которых верный.")
    return get_response([
        {"role": "system", "content": "You are a helpful assistant that generates educational tests. "
                                      "You need to answer in Russian."},
        {"role": "user", "content": prompt},
    ])
