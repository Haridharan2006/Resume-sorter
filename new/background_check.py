from detoxify import Detoxify

model = Detoxify("original")

def analyze_posts(posts, threshold=0.3):
    flagged = 0

    for post in posts:
        scores = model.predict(post)
        for score in scores.values():
            if score >= threshold:
                flagged += 1
                break

    risk_percent = (flagged / len(posts)) * 100 if posts else 0

    return round(risk_percent, 2)