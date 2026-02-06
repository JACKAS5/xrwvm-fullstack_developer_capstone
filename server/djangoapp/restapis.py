import requests
import os
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv("backend_url", default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url", default="http://localhost:5050/"
)


def get_request(endpoint, **kwargs):
    """
    Send GET request to backend with optional query parameters.
    Returns JSON data or None on failure.
    """
    params = ""
    if kwargs:
        params = "&".join(f"{key}={value}" for key, value in kwargs.items())

    request_url = f"{backend_url}{endpoint}"
    if params:
        request_url += f"?{params}"

    print(f"GET from {request_url}")

    try:
        response = requests.get(request_url, timeout=10)
        response.raise_for_status()  # Raise if HTTP error (4xx/5xx)
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Network exception occurred: {err}")
        return None


def analyze_review_sentiments(text):
    """
    Send review text to sentiment analyzer and return sentiment result.
    Returns dict with 'sentiment' key (defaults to 'neutral' on failure).
    """
    # Safely encode text to avoid URL issues
    encoded_text = requests.utils.quote(text)
    request_url = f"{sentiment_analyzer_url}analyze/{encoded_text}"

    try:
        response = requests.get(request_url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Sentiment analysis failed: {err}")
        return {"sentiment": "neutral"}


def post_review(data_dict):
    """
    Post a review dictionary to the backend.
    Returns response JSON or None on failure.
    """
    request_url = f"{backend_url}/insert_review"

    try:
        response = requests.post(request_url, json=data_dict, timeout=10)
        response.raise_for_status()
        result = response.json()
        print("Post review response:", result)
        return result
    except requests.exceptions.RequestException as err:
        print(f"Network exception occurred during post: {err}")
        return None
