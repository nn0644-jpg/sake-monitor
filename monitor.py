import os
import requests

url = os.environ["DISCORD_WEBHOOK"]

requests.post(
    url,
    json={
        "content": "ワダヤ更新"
    }
)