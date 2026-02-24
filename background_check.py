from detoxify import Detoxify

model = Detoxify("original")

def analyze_posts(posts, threshold=0.6):
    results = []
    flagged_count = 0

    for post in posts:
        scores = model.predict(post)

        flagged_labels = []
        for label, score in scores.items():
            if score >= threshold:
                flagged_labels.append({
                    "label": label,
                    "score": round(float(score), 3)
                })

        flagged = len(flagged_labels) > 0
        if flagged:
            flagged_count += 1

        results.append({
            "post": post,
            "flagged": flagged,
            "flagged_labels": flagged_labels,
            "scores": {k: round(float(v), 3) for k, v in scores.items()}
        })

    risk_percent = (flagged_count / len(posts)) * 100 if posts else 0

    return {
        "total_posts": len(posts),
        "flagged_posts": flagged_count,
        "risk_percent": round(risk_percent, 2),
        "details": results
    }
