import os
from urllib.parse import quote

import requests
from dotenv import load_dotenv

load_dotenv()

backend_url = os.getenv("backend_url", default="http://localhost:3030")
sentiment_analyzer_url = os.getenv(
    "sentiment_analyzer_url", default="http://localhost:5050/"
)


def get_request(endpoint, **kwargs):
    request_url = backend_url + endpoint
    try:
        response = requests.get(request_url, params=kwargs)
        print(f"GET from {response.url}")
        return response.json()
    except requests.exceptions.RequestException as e:
        print("Network exception occurred:", e)
        return None


def analyze_review_sentiments(text):
    request_url = sentiment_analyzer_url + "analyze/" + quote(text)
    try:
        response = requests.get(request_url)
        return response.json()
    except requests.exceptions.RequestException as err:
        print(f"Unexpected {err=}, {type(err)=}")
        print("Network exception occurred")
        return None


def post_review(data_dict):
    request_url = backend_url + "/insert_review"
    try:
        response = requests.post(request_url, json=data_dict)
        try:
            json_data = response.json()
        except ValueError:
            json_data = response.text
        print(json_data)
        return json_data
    except requests.exceptions.RequestException as e:
        print("Network exception occurred:", e)
        return None
