from features import get_response


def solve_problem(description):
    prompt = (
        f"Реши следующую задачу и предоставь подробное пошаговое объяснение на русском языке:\n\n"
        f"Задача: {description}\n\n"
        f"Важно: если задача связана с математикой, физикой или "
        f"другой точной наукой, включи формулы и краткие обоснования. "
        f"Если задача относится к гуманитарным наукам, дай чёткий, логичный и обоснованный ответ. "
        f"Структура ответа:\n"
        f"1. Анализ задачи.\n"
        f"2. Решение с пояснениями.\n"
        f"3. Итоговый ответ."
    )
    return get_response([
        {"role": "system", "content": "Вы опытный репетитор, который объясняет задачи шаг за шагом."},
        {"role": "user", "content": prompt}
    ])
