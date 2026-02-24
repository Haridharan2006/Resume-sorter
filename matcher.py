from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_match_score(resume_text, job_desc):
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    job_embedding = model.encode(job_desc, convert_to_tensor=True)

    similarity = util.cos_sim(resume_embedding, job_embedding)
    return float(similarity[0][0]) * 100
