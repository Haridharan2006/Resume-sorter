from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
import os

from utils.resume_parser import extract_resume_text
from utils.matcher import get_match_score
from utils.background_check import analyze_posts
from utils.social_fetch import fetch_reddit_posts
from utils.link_extractor import extract_social_links

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///candidates.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150))
    resume_score = db.Column(db.Float)
    toxicity_percent = db.Column(db.Float)
    final_score = db.Column(db.Float)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    resume_file = request.files["resume"]
    job_desc = request.form["job_desc"]

    file_path = os.path.join(UPLOAD_FOLDER, resume_file.filename)
    resume_file.save(file_path)

    resume_text = extract_resume_text(file_path)

    # Resume score
    resume_score = get_match_score(resume_text, job_desc)

    # Extract Reddit links automatically
    reddit_links = extract_social_links(resume_text)

    posts = []
    for link in reddit_links:
        try:
            posts.extend(fetch_reddit_posts(link))
        except:
            pass

    toxicity_percent = analyze_posts(posts)

    penalty = toxicity_percent * 0.5
    final_score = resume_score - penalty

    candidate = Candidate(
        filename=resume_file.filename,
        resume_score=round(resume_score,2),
        toxicity_percent=toxicity_percent,
        final_score=round(final_score,2)
    )

    db.session.add(candidate)
    db.session.commit()

    return redirect("/dashboard")

@app.route("/dashboard")
def dashboard():
    candidates = Candidate.query.order_by(Candidate.final_score.desc()).all()
    return render_template("dashboard.html", candidates=candidates)

if __name__ == "__main__":
    app.run(debug=True)