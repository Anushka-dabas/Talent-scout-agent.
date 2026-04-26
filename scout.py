import os
import json
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def get_match_score(jd, source_info, exp_val):
    prompt = f"""
    Act as a Senior Recruiter. Analyze this candidate: {source_info}
    Target Experience: {exp_val}
    Job Description: {jd}
    
    Evaluate strictly. Do not give a default score. 
    Return exactly this format:
    Score: [0-100]
    Reason: [Detailed Analysis]
    Gaps: [Missing Skills]
    """
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return res.choices[0].message.content

def start_outreach(name, jd):
    # Now generates a detailed career pitch from the recruiter's perspective
    prompt = f"""
    Write a detailed, professional recruitment message to {name}.
    Context: {jd}
    
    Include:
    1. The specific role and company mission.
    2. Key career growth opportunities mentioned in the JD.
    3. A clear call to action for an interview.
    Keep it professional and encouraging.
    """
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}]
    )
    return res.choices[0].message.content

def check_interest(text):
    prompt = f"Score interest 0-100: '{text}'. Return ONLY the number."
    res = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.1
    )
    return res.choices[0].message.content.strip()