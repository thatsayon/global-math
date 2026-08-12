import requests

url = "http://127.0.0.1:8000/api/v1/post/1/react/"
headers = {
    "Authorization": "Bearer fake_token",
    "Content-Type": "application/json"
}
# We don't have a token, but let's just see what happens if we grep the view output or something.
# Better yet, let's look at what the backend ACTUALLY returns for PostReactionView.
