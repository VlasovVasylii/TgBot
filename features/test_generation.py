from features import get_response


def generate_test(topic, num_questions=5):
    prompt = (
        f"Составь учебный тест на тему '{topic}' с {num_questions} вопросами. "
        f"Каждый вопрос должен быть четким и иметь 4 варианта ответа, один из которых правильный. "
        f"Ответы должны быть в формате:\n"
        f"1. Вопрос\nA) Вариант 1\nB) Вариант 2\nC) Вариант 3\nD) Вариант 4\nВерный ответ: X"
    )
    return get_response([
        {"role": "system", "content": "Вы помощник, который создает образовательные материалы."},
        {"role": "user", "content": prompt},
    ])
