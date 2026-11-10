import os
import re
import requests
from bs4 import BeautifulSoup

WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

NEWS_URL = "https://sake-wadaya.com/news/"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(
    NEWS_URL,
    headers=headers,
    timeout=30
)

response.raise_for_status()

soup = BeautifulSoup(response.text, "html.parser")

# 新着記事URL抽出
articles = []

for a in soup.find_all("a", href=True):

    href = a["href"]

    match = re.match(
        r"https://sake-wadaya\.com/(\d+)/?$",
        href
    )

    if match:

        title = a.get_text(" ", strip=True)

        if title:
            articles.append({
                "title": title,
                "url": href,
                "id": int(match.group(1))
            })

if not articles:
    raise Exception("記事を取得できませんでした")

# 記事ID最大 = 最新記事
latest = max(articles, key=lambda x: x["id"])

latest_url = latest["url"]
latest_title = latest["title"]

print(f"最新記事: {latest_title}")
print(f"URL: {latest_url}")

# 前回状態取得
if os.path.exists("last_post.txt"):
    with open("last_post.txt", "r", encoding="utf-8") as f:
        previous_url = f.read().strip()
else:
    previous_url = ""

# 初回実行
if previous_url == "":
    with open("last_post.txt", "w", encoding="utf-8") as f:
        f.write(latest_url)

    print("初回実行のため通知しません")
    raise SystemExit(0)

# 更新確認
if previous_url != latest_url:

    message = f"""🍶 ワダヤ新着情報

{latest_title}

{latest_url}
"""

    requests.post(
        WEBHOOK_URL,
        json={"content": message},
        timeout=30
    )

    print("通知送信完了")

    with open("last_post.txt", "w", encoding="utf-8") as f:
        f.write(latest_url)

else:
    print("更新なし")