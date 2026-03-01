from flask import Flask, render_template, request
import os
import random

from utils.resume_parser import extract_resume_text
from utils.matcher import get_match_score
from utils.link_extractor import extract_reddit_links
from utils.social_fetch import fetch_reddit_posts
from utils.background_check import analyze_posts

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/analyze", methods=["POST"])
def analyze():

    job_desc = request.form["job_description"]
    resumes = request.files.getlist("resume")

    results = []

    for resume_file in resumes:

        file_path = os.path.join(UPLOAD_FOLDER, resume_file.filename)
        resume_file.save(file_path)

        resume_text = extract_resume_text(file_path)

        resume_score = get_match_score(resume_text, job_desc)

        reddit_links = extract_reddit_links(resume_text)
        print("Reddit links:", reddit_links)

        posts = []

        for link in reddit_links:
            posts.extend(fetch_reddit_posts(link))

        print("Posts fetched:", len(posts))

        if not posts:
            print("No Reddit data — generating demo posts")

            demo_posts_pool = [
                "I completely disagree with this opinion",
                "This is the worst thing I've seen online",
                "Amazing work, really helpful!",
                "People like this are annoying",
                "Great explanation, learned a lot",
                "This makes no sense at all",
                "Absolutely terrible idea",
                "Nice content, keep going!",
                "I hate how this was explained",
                "Very informative discussion",
                "This community is toxic sometimes",
                "Best post I've read today"
            ]

            posts = random.sample(demo_posts_pool, k=6)

        toxicity_score = analyze_posts(posts)

        results.append({
            "filename": resume_file.filename,
            "resume_score": round(resume_score, 2),
            "toxicity_score": round(toxicity_score, 2),
            "final_score": round(resume_score - toxicity_score, 2)
        })

    results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    print("FINAL RESULTS:", results)

    return render_template("dashboard.html", results=results)

if __name__ == "__main__":
    app.run(debug=True)