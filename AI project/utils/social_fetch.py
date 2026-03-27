import requests
import re


def extract_reddit_username(url):
    match = re.search(r"reddit\.com/user/([^/]+)/?", url)
    if match:
        return match.group(1)
    return None


def fetch_reddit_posts(profile_url, limit=20):

    username = extract_reddit_username(profile_url)

    if not username:
        return []

    print("Fetching Reddit JSON data for:", username)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }

    url = f"https://www.reddit.com/user/{username}.json"

    posts = []

    try:
        response = requests.get(url, headers=headers)

        if response.status_code != 200:
            print("Reddit blocked request:", response.status_code)
            return []

        data = response.json()

        for item in data["data"]["children"]:
            content = item["data"]

            if "title" in content:
                posts.append(content["title"])

            if "selftext" in content and content["selftext"]:
                posts.append(content["selftext"])

            if "body" in content:
                posts.append(content["body"])

    except Exception as e:
        print("Reddit scrape error:", e)

    print("Total text collected:", len(posts))

    return posts[:limit]