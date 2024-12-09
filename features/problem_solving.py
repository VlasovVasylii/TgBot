from features import get_response


def solve_problem(description):
    """Решение задачи с помощью OpenAI API."""
    prompt = f"Реши следующую задачу и объясни решение: {description}"
    return get_response([
        {"role": "system", "content": "You are a helpful assistant that solves problems step-by-step."
                                      " You need to answer in Russian."},
        {"role": "user", "content": prompt}
    ])
