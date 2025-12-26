import os
import requests

AI_BASE_URL = os.getenv("AI_BASE_URL")


def _check_ai():
    if not AI_BASE_URL:
        raise RuntimeError("AI_BASE_URL is not set")


def process_math_problem(prompt: str) -> str:
    _check_ai()

    res = requests.post(
        f"{AI_BASE_URL}/generate",
        json={"prompt": prompt},
        timeout=30
    )

    if res.status_code != 200:
        raise RuntimeError(res.text)

    return res.json().get("result", "")


def process_math_problem_from_url(image_url: str, prompt: str) -> str:
    _check_ai()

    data = {"prompt": prompt}
    files = None

    if image_url.startswith("file://"):
        path = image_url.replace("file://", "")
        files = {"image": open(path, "rb")}
    else:
        data["image_url"] = image_url

    try:
        res = requests.post(
            f"{AI_BASE_URL}/generate-from-image",
            data=data,
            files=files,
            timeout=45
        )
    finally:
        if files:
            files["image"].close()

    if res.status_code != 200:
        raise RuntimeError(res.text)

    return res.json().get("result", "")

