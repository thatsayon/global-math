import os
import requests

AI_BASE_URL = os.getenv("AI_BASE_URL")


def check_solution_with_ai(
    problem_text=None,
    solution_text=None,
    problem_url=None,
    solution_url=None,
):
    if not AI_BASE_URL:
        raise RuntimeError("AI_BASE_URL is not configured")

    payload = {}

    if problem_text:
        payload["problem_text"] = problem_text
    if solution_text:
        payload["solution_text"] = solution_text
    if problem_url:
        payload["problem_url"] = problem_url
    if solution_url:
        payload["solution_url"] = solution_url

    response = requests.post(
        f"{AI_BASE_URL}/check-solution",
        data=payload,  # form-data / x-www-form-urlencoded
        timeout=45
    )

    if response.status_code != 200:
        raise RuntimeError(
            f"AI service error {response.status_code}: {response.text}"
        )

    return response.json()

