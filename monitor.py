import os
import re
import requests
from bs4 import BeautifulSoup


from datetime import datetime, timezone

print(
    "実行時刻:",
    datetime.now(timezone.utc)
)


WEBHOOK_URL = os.environ["DISCORD_WEBHOOK"]

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}


def send_discord(message):
    requests.post(
        WEBHOOK_URL,
        json={"content": message},
        timeout=30
    )


def load_state(filename):
    if not os.path.exists(filename):
        return ""

    with open(filename, "r", encoding="utf-8") as f:
        return f.read().strip()


def save_state(filename, value):
    with open(filename, "w", encoding="utf-8") as f:
        f.write(value)


# -----------------------------
# ワダヤ
# -----------------------------
def get_wadaya_latest():

    url = "https://sake-wadaya.com/news/"

    r = requests.get(url, headers=HEADERS, timeout=30)
    r.raise_for_status()

    text = r.text

    matches = re.findall(
        r'href="(https://sake-wadaya\.com/\d+/?)"',
        text
    )

    if not matches:
        raise Exception("ワダヤ記事取得失敗")

    article_url = matches[0]

    html = requests.get(
        article_url,
        headers=HEADERS,
        timeout=30
    ).text

    soup = BeautifulSoup(html, "html.parser")

    title = soup.title.get_text(strip=True)

    return {
        "site": "ワダヤ",
        "url": article_url,
        "title": title
    }


# -----------------------------
# 福原酒店
# -----------------------------
def get_fukuhara_latest():

    url = "http://blog.livedoor.jp/fukuharasaketen/"

    html = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    ).text

    m = re.search(
        r'(http://blog\.livedoor\.jp/fukuharasaketen/archives/\d+\.html)',
        html
    )

    if not m:
        raise Exception("福原酒店記事取得失敗")

    article_url = m.group(1)

    article_html = requests.get(
        article_url,
        headers=HEADERS,
        timeout=30
    ).text

    soup = BeautifulSoup(
        article_html,
        "html.parser"
    )

    title = soup.title.get_text(strip=True)

    return {
        "site": "福原酒店",
        "url": article_url,
        "title": title
    }


# -----------------------------
# 地酒.com
# -----------------------------
def get_jizake_latest():

    url = "https://www.jizake.com/c/sake/new_sake"

    html = requests.get(
        url,
        headers=HEADERS,
        timeout=30
    ).text

    soup = BeautifulSoup(html, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):

        href = a["href"]

        if "/c/sake/new_sake/" in href:

            text = a.get_text(
                " ",
                strip=True
            )

            if len(text) > 5:
                links.append(
                    (
                        text,
                        href
                    )
                )

    if not links:
        raise Exception("地酒.com商品取得失敗")

    title, product_url = links[0]

    if product_url.startswith("/"):
        product_url = (
            "https://www.jizake.com"
            + product_url
        )

    return {
        "site": "地酒.com",
        "url": product_url,
        "title": title
    }


# -----------------------------
# サイト一覧
# -----------------------------
SITES = [
    (
        get_wadaya_latest,
        "state_wadaya.txt"
    ),
    (
        get_fukuhara_latest,
        "state_fukuhara.txt"
    ),
    (
        get_jizake_latest,
        "state_jizake.txt"
    )
]


# -----------------------------
# 実行
# -----------------------------
for getter, state_file in SITES:

    try:

        latest = getter()

        current_url = latest["url"]

        previous_url = load_state(
            state_file
        )

        # 初回実行
        if previous_url == "":

            save_state(
                state_file,
                current_url
            )

            print(
                latest["site"],
                "初回登録"
            )

            continue

        # 更新検知
        if current_url != previous_url:

            message = f"""
🍶 新着情報

【{latest['site']}】

{latest['title']}

{latest['url']}
"""

            send_discord(message)

            save_state(
                state_file,
                current_url
            )

            print(
                latest["site"],
                "更新検知"
            )

        else:

            print(
                latest["site"],
                "更新なし"
            )

    except Exception as e:

        print(
            "ERROR:",
            str(e)
        )