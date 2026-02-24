import praw

reddit = praw.Reddit(
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET",
    user_agent="resume_screening_app"
)

def fetch_reddit_posts(profile_url, limit=20):
    username = profile_url.split("/")[-2]

    user = reddit.redditor(username)

    posts = []
    for submission in user.submissions.new(limit=limit):
        posts.append(submission.title + " " + submission.selftext)

    for comment in user.comments.new(limit=limit):
        posts.append(comment.body)

    return posts