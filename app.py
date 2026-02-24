from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

from utils.resume_parser import extract_resume_text
from utils.skill_extractor import extract_skills
from utils.matcher import get_match_score
from utils.background_check import analyze_posts
from utils.social_fetch import fetch_reddit_posts

# -----------------------------------
# FLASK SETUP
# -----------------------------------
app = Flask(__name__)

# Database Configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///candidates.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)

# Upload Folder
UPLOAD_FOLDER = "resumes"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# -----------------------------------
# DATABASE MODEL
# -----------------------------------
class Candidate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150))
    resume_score = db.Column(db.Float)
    toxicity_percent = db.Column(db.Float)
    risk_level = db.Column(db.String(20))
    penalty = db.Column(db.Float)
    final_score = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "resume_score": self.resume_score,
            "toxicity_percent": self.toxicity_percent,
            "risk_level": self.risk_level,
            "penalty": self.penalty,
            "final_score": self.final_score,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }


# Create database tables automatically
with app.app_context():
    db.create_all()


# -----------------------------------
# RISK LEVEL FUNCTION
# -----------------------------------
def risk_level(score):
    if score < 20:
        return "LOW"
    elif score < 50:
        return "MEDIUM"
    else:
        return "HIGH"


# -----------------------------------
# HOME PAGE
# -----------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# -----------------------------------
# ANALYZE ROUTE
# -----------------------------------
@app.route("/analyze", methods=["POST"])
def analyze():

    resumes = request.files.getlist("resume")
    job_desc = request.form.get("job_desc")
    profile_link = request.form.get("profile_link")

    if not resumes or not job_desc:
        return jsonify({"error": "Resumes and Job Description are required"}), 400

    # -------------------------------
    # Fetch Social Media Posts
    # -------------------------------
    posts = []
    if profile_link:
        try:
            posts = fetch_reddit_posts(profile_link, limit=20)
        except Exception as e:
            print("Reddit Fetch Error:", e)
            posts = []

    # -------------------------------
    # Background Analysis
    # -------------------------------
    background_report = analyze_posts(posts) if posts else {
        "total_posts": 0,
        "flagged_posts": 0,
        "risk_percent": 0,
        "details": []
    }

    toxicity_percent = background_report["risk_percent"]
    level = risk_level(toxicity_percent)

    results = []

    # -------------------------------
    # Process Each Resume
    # -------------------------------
    for resume_file in resumes:

        file_path = os.path.join(UPLOAD_FOLDER, resume_file.filename)
        resume_file.save(file_path)

        resume_text = extract_resume_text(file_path)
        skills = extract_skills(resume_text)
        resume_score = get_match_score(resume_text, job_desc)

        penalty = toxicity_percent * 0.5
        final_score = resume_score - penalty

        # Save to Database
        candidate = Candidate(
            filename=resume_file.filename,
            resume_score=round(resume_score, 2),
            toxicity_percent=toxicity_percent,
            risk_level=level,
            penalty=round(penalty, 2),
            final_score=round(final_score, 2)
        )

        db.session.add(candidate)
        db.session.commit()

        results.append({
            "filename": resume_file.filename,
            "skills": skills,
            "resume_score": round(resume_score, 2),
            "toxicity_percent": toxicity_percent,
            "risk_level": level,
            "penalty": round(penalty, 2),
            "final_score": round(final_score, 2)
        })

    # Rank by Final Score
    results = sorted(results, key=lambda x: x["final_score"], reverse=True)

    return jsonify({
        "ranked_candidates": results,
        "background_report": background_report
    })


# -----------------------------------
# DASHBOARD ROUTE
# -----------------------------------
@app.route("/dashboard")
def dashboard():
    candidates = Candidate.query.order_by(Candidate.final_score.desc()).all()
    return jsonify([c.to_dict() for c in candidates])


# -----------------------------------
# RUN APP
# -----------------------------------
if __name__ == "__main__":
    app.run(debug=True)