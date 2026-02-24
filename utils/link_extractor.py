import re

def extract_social_links(text):
    urls = re.findall(r'https?://[^\s]+', text)

    reddit_links = []

    for url in urls:
        if "reddit.com/user/" in url:
            reddit_links.append(url)

    return reddit_links