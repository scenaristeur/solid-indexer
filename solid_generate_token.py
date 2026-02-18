import requests
import os
from dotenv import load_dotenv

load_dotenv()

IDP_URL = os.getenv("SOLID_ENDPOINT")  # ex: https://solid.example.com

def generate_client_credentials(email, password, token_name="mon-indexeur"):
    url = f"{IDP_URL}/idp/credentials/"
    payload = {
        "email": email,
        "password": password,
        "name": token_name
    }
    response = requests.post(url, json=payload)
    response.raise_for_status()
    data = response.json()
    print(f"ID: {data['id']}")
    print(f"Secret: {data['secret']}")
    return data['id'], data['secret']

if __name__ == "__main__":
    email = os.getenv("SOLID_EMAIL")
    password = os.getenv("SOLID_PASSWORD")
    id, secret = generate_client_credentials(email, password)
    print(id, secret)
    # À stocker dans .env : SOLID_CLIENT_ID et SOLID_CLIENT_SECRET