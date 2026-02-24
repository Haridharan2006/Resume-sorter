SKILLS_DB = [
    "python", "java", "c", "c++", "sql",
    "html", "css", "javascript",
    "machine learning", "deep learning", "data science",
    "flask", "django", "fastapi",
    "react", "node.js", "express",
    "tensorflow", "pytorch", "nlp"
]

def extract_skills(text):
    text = text.lower()
    found = []

    for skill in SKILLS_DB:
        if skill in text:
            found.append(skill)

    return list(set(found))
