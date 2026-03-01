import random
import re


def extract_reddit_username(url):
    match = re.search(r"reddit\.com/user/([^/]+)/?", url)
    if match:
        return match.group(1)
    return None


def fetch_reddit_posts(profile_url, limit=20):

    username = extract_reddit_username(profile_url)

    print("Fetching Reddit data for:", username)

    demo_posts_pool = [
        "I completely disagree with this opinion",
        "This is the worst thing I've seen online",
        "Amazing explanation, thanks!",
        "People like this are annoying",
        "Great work, very informative",
        "This community is toxic sometimes",
        "Absolutely terrible take",
        "Nice discussion overall",
        "I hate how this was presented",
        "Very respectful conversation here",
        "This idea makes no sense",
        "Best post today honestly",
        "You clearly don't understand anything",
        "Fantastic explanation!",
        "This is stupid and misleading"
    ]

    posts = random.sample(demo_posts_pool, k=random.randint(6, 12))

    print("Demo Reddit posts generated:", len(posts))

    return posts