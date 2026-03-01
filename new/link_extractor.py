import re


def extract_reddit_links(text):
    pattern = r"(https?://(?:www\.)?reddit\.com/user/[A-Za-z0-9_-]+)"
    return re.findall(pattern, text)